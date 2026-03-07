"""CLI entry point for populate-aircraft-db."""

from __future__ import annotations

import time
from collections.abc import Generator
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Literal

import sys

import typer
from neo4j import Driver, GraphDatabase
from neo4j.exceptions import ServiceUnavailable

from .config import Settings
from .loader import clear_database, load_nodes, load_relationships, verify
from .schema import (
    create_constraints,
    create_embedding_indexes,
    create_extraction_constraints,
    create_fulltext_indexes,
    create_indexes,
)

app = typer.Typer(
    name="populate-aircraft-db",
    help="Load the Aircraft Digital Twin dataset into a Neo4j Aura instance.",
    add_completion=False,
)


def _fmt_elapsed(seconds: float) -> str:
    m, s = divmod(int(seconds), 60)
    if m:
        return f"{m}m {s:02d}s"
    return f"{s}s"


@contextmanager
def _connect(settings: Settings) -> Generator[Driver, None, None]:
    """Create a Neo4j driver, verify connectivity, and close on exit."""
    driver = GraphDatabase.driver(
        settings.neo4j_uri,
        auth=(settings.neo4j_username, settings.neo4j_password.get_secret_value()),
    )
    try:
        driver.verify_connectivity()
    except (ServiceUnavailable, OSError) as exc:
        driver.close()
        print(f"[FAIL] Cannot connect to {settings.neo4j_uri}")
        print(f"       {exc}")
        print("\nCheck that the Neo4j instance is running and reachable.")
        sys.exit(1)
    try:
        print("[OK] Connected.\n")
        yield driver
    finally:
        driver.close()


# ---------------------------------------------------------------------------
# LLM credential resolution
# ---------------------------------------------------------------------------


@dataclass
class _LLMCredentials:
    provider: Literal["openai", "anthropic", "azure"]
    openai_key: str | None
    anthropic_key: str | None
    azure_key: str | None
    llm_model: str
    embedding_model: str
    embedding_dims: int


def _resolve_llm_credentials(settings: Settings) -> _LLMCredentials:
    """Validate and resolve LLM credentials from settings. Raises typer.BadParameter on failure."""
    provider = settings.llm_provider
    openai_key = None
    anthropic_key = None
    azure_key = None

    if provider == "openai":
        if settings.openai_api_key is None:
            raise typer.BadParameter(
                "OPENAI_API_KEY is required when using OpenAI. "
                "Set it in .env or as an env var."
            )
        openai_key = settings.openai_api_key.get_secret_value()
        llm_model = settings.openai_extraction_model
    elif provider == "anthropic":
        # Anthropic still needs OpenAI for embeddings.
        if settings.openai_api_key is None:
            raise typer.BadParameter(
                "OPENAI_API_KEY is required for embeddings when using Anthropic. "
                "Set it in .env or as an env var."
            )
        openai_key = settings.openai_api_key.get_secret_value()
        if settings.anthropic_api_key is None:
            raise typer.BadParameter(
                "ANTHROPIC_API_KEY is required when using Anthropic. "
                "Set it in .env or as an env var."
            )
        anthropic_key = settings.anthropic_api_key.get_secret_value()
        llm_model = settings.anthropic_extraction_model
    elif provider == "azure":
        for field, label in [
            ("azure_openai_api_key", "AZURE_OPENAI_API_KEY"),
            ("azure_openai_endpoint", "AZURE_OPENAI_ENDPOINT"),
            ("azure_openai_llm_deployment", "AZURE_OPENAI_LLM_DEPLOYMENT"),
            ("azure_openai_embedding_deployment", "AZURE_OPENAI_EMBEDDING_DEPLOYMENT"),
        ]:
            if getattr(settings, field) is None:
                raise typer.BadParameter(
                    f"{label} is required when using Azure. "
                    "Set it in .env or as an env var."
                )
        azure_key = settings.azure_openai_api_key.get_secret_value()  # type: ignore[union-attr]
        llm_model = settings.azure_openai_llm_deployment  # type: ignore[assignment]
    else:
        raise typer.BadParameter(
            f"Unknown provider: {provider!r}. Use 'openai', 'anthropic', or 'azure'."
        )

    if provider == "azure":
        embedding_model = settings.azure_openai_embedding_deployment
        embedding_dims = settings.azure_openai_embedding_dimensions
    else:
        embedding_model = settings.openai_embedding_model
        embedding_dims = settings.openai_embedding_dimensions

    return _LLMCredentials(
        provider=provider,
        openai_key=openai_key,
        anthropic_key=anthropic_key,
        azure_key=azure_key,
        llm_model=llm_model,
        embedding_model=embedding_model,
        embedding_dims=embedding_dims,
    )


# ---------------------------------------------------------------------------
# Enrichment helper
# ---------------------------------------------------------------------------


def _run_enrich(driver: Driver, settings: Settings, creds: _LLMCredentials) -> None:
    """Run the enrichment pipeline: chunk, embed, extract entities, and link."""
    from .pipeline import (
        clear_enrichment_data,
        link_to_existing_graph,
        process_all_documents,
        validate_enrichment,
    )

    print("Clearing existing enrichment data (safe re-run)...")
    clear_enrichment_data(driver)
    print()

    if settings.enrich_sample_size:
        print(f"Running SimpleKGPipeline (LLM: {creds.provider}/{creds.llm_model},"
              f" sample_size={settings.enrich_sample_size} chunks/doc)...")
    else:
        print(f"Running SimpleKGPipeline (LLM: {creds.provider}/{creds.llm_model})...")

    process_all_documents(
        driver,
        settings.data_dir,
        provider=creds.provider,
        openai_api_key=creds.openai_key,
        anthropic_api_key=creds.anthropic_key,
        azure_api_key=creds.azure_key,
        azure_endpoint=settings.azure_openai_endpoint if creds.provider == "azure" else None,
        azure_api_version=settings.azure_openai_api_version if creds.provider == "azure" else None,
        llm_model=creds.llm_model,
        embedding_model=creds.embedding_model,
        embedding_dimensions=creds.embedding_dims,
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        enrich_sample_size=settings.enrich_sample_size,
    )

    print("\nCreating extraction constraints (post entity-resolution)...")
    create_extraction_constraints(driver)

    print("\nCreating embedding indexes...")
    create_embedding_indexes(driver, creds.embedding_dims)

    print("\nLinking to existing graph...")
    link_to_existing_graph(driver)

    validate_enrichment(driver)


# ---------------------------------------------------------------------------
# CLI commands
# ---------------------------------------------------------------------------


@app.command("setup")
def setup_cmd() -> None:
    """Load CSV data into Neo4j and run GraphRAG enrichment in a single pass."""
    settings = Settings()  # type: ignore[call-arg]

    # Validate LLM credentials early, before any Neo4j work.
    creds = _resolve_llm_credentials(settings)

    start = time.monotonic()

    print(f"Connecting to {settings.neo4j_uri}...")
    with _connect(settings) as driver:
        print("Creating constraints...")
        create_constraints(driver)
        print("\nCreating indexes...")
        create_indexes(driver)
        print("\nCreating fulltext indexes...")
        create_fulltext_indexes(driver)
        print()

        load_nodes(driver, settings.data_dir)
        print()
        load_relationships(driver, settings.data_dir)
        print()

        try:
            _run_enrich(driver, settings, creds)
        except Exception as exc:
            print(f"\n[FAIL] Enrichment failed: {exc}")
            print("CSV data was loaded successfully. Fix the issue and re-run:")
            print("  uv run populate-aircraft-db setup")
            raise typer.Exit(code=1)

        verify(driver)

    elapsed = time.monotonic() - start
    print(f"\nDone in {_fmt_elapsed(elapsed)}.")


@app.command("verify")
def verify_cmd() -> None:
    """Print node and relationship counts (read-only)."""
    settings = Settings()  # type: ignore[call-arg]

    print(f"Connecting to {settings.neo4j_uri}...")
    with _connect(settings) as driver:
        verify(driver)


@app.command("clean")
def clean_cmd() -> None:
    """Clear all nodes and relationships from the database."""
    settings = Settings()  # type: ignore[call-arg]

    print(f"Connecting to {settings.neo4j_uri}...")
    with _connect(settings) as driver:
        clear_database(driver)

    print("\nDone.")


@app.command("clean-enrichment")
def clean_enrichment_cmd() -> None:
    """Clear enrichment data (Documents, Chunks, extracted entities) while preserving the operational graph."""
    from .pipeline import clear_enrichment_data

    settings = Settings()  # type: ignore[call-arg]

    print(f"Connecting to {settings.neo4j_uri}...")
    with _connect(settings) as driver:
        clear_enrichment_data(driver)

    print("\nDone.")


@app.command("samples")
def samples_cmd() -> None:
    """Run sample queries showcasing the knowledge graph (read-only)."""
    from .samples import run_all_samples

    settings = Settings()  # type: ignore[call-arg]

    print(f"Connecting to {settings.neo4j_uri}...")
    with _connect(settings) as driver:
        run_all_samples(driver, sample_size=settings.sample_size)


@app.command("agent-samples")
def agent_samples_cmd() -> None:
    """Simulate the Neo4j Aura Agent: send natural language questions to the LLM,
    generate Cypher or vector searches, execute them, and display results."""
    from .agent_samples import run_agent_samples

    settings = Settings()  # type: ignore[call-arg]
    creds = _resolve_llm_credentials(settings)

    print(f"Connecting to {settings.neo4j_uri}...")
    with _connect(settings) as driver:
        run_agent_samples(
            driver,
            provider=creds.provider,
            openai_key=creds.openai_key,
            anthropic_key=creds.anthropic_key,
            azure_key=creds.azure_key,
            azure_endpoint=settings.azure_openai_endpoint if creds.provider == "azure" else None,
            azure_api_version=settings.azure_openai_api_version if creds.provider == "azure" else None,
            llm_model=creds.llm_model,
            embedding_model=creds.embedding_model,
            embedding_dimensions=creds.embedding_dims,
            sample_size=settings.sample_size,
        )


if __name__ == "__main__":
    app()
