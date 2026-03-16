# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A hands-on workshop teaching production-ready AI agents combining **Neo4j graph databases** with **Databricks AI/ML**. Demonstrates a dual-database architecture for aircraft digital twins where Neo4j handles relationship-rich data (topology, maintenance, flights) and Databricks Lakehouse handles high-volume time-series sensor telemetry.

The workshop culminates in a **Multi-Agent Supervisor** (Databricks AgentBricks) that routes questions to specialized agents: Genie (sensor analytics via SQL) and Neo4j MCP (graph relationships via Cypher).

## Build & Run Commands

All Python tools use `uv` for package management and `hatchling` as build backend. Python 3.11+ required.

### populate_aircraft_db (Neo4j data loading CLI)
```bash
cd lab_setup/populate_aircraft_db
uv sync                                    # Install dependencies
uv run populate-aircraft-db setup           # Load CSV data + enrich (chunking, embeddings, entity extraction)
uv run populate-aircraft-db verify         # Print node/relationship counts
uv run populate-aircraft-db clean          # Delete all data
uv run populate-aircraft-db samples        # Run showcase Cypher queries
```

### databricks_setup (Admin workspace provisioning CLI)
```bash
cd lab_setup/auto_scripts
uv sync
uv run databricks-setup setup             # Full setup (cluster, data, tables, permissions)
uv run databricks-setup cleanup            # Tear down
uv run databricks-setup add-users          # Create accounts, per-user clusters
uv run databricks-setup remove-users       # Remove users and clusters
uv run databricks-setup list-users         # Show group members
```

### verify_labs (Neo4j verification CLI)
```bash
cd lab_setup/verify_labs
uv sync
uv run verify-labs check                   # Connectivity test
uv run verify-labs lab5                    # All Lab 5 verification queries
uv run verify-labs lab5 --notebook 01      # Notebook 1 only
```

### Linting (auto_scripts only)
```bash
cd lab_setup/auto_scripts
uv run ruff check .                        # Lint (rules: E, W, F, I, B, C4, UP, SIM)
uv run mypy src/                           # Type checking (strict mode)
```

## Architecture

### Three Independent CLI Tools
Each under `lab_setup/` is a standalone Python package with its own `pyproject.toml`, `.env`, and Typer CLI:

- **`populate_aircraft_db/`** — Loads aircraft CSV data into Neo4j Aura, runs GraphRAG enrichment (doc chunking, embeddings via BGE-large, entity extraction via SimpleKGPipeline)
- **`auto_scripts/`** (databricks_setup) — Automates Databricks workspace provisioning: cluster creation, Spark Connector install, Delta table creation, UC permissions, user management via SCIM
- **`verify_labs/`** — Verifies Neo4j data loaded correctly in Lab 5

### Dual-Database Strategy
- **Neo4j**: `(Aircraft)-[:HAS_SYSTEM]->(System)-[:HAS_COMPONENT]->(Component)`, plus Sensors, Flights, Delays, MaintenanceEvents
- **Databricks**: Delta tables for `sensor_readings` (345K+ rows), `sensors`, `systems`, `aircraft`
- Aircraft/Systems/Sensors exist in **both** databases as join points

### Multi-Agent Architecture (Lab 7)
```
User Question → Multi-Agent Supervisor (AgentBricks)
  ├→ Genie Agent → Databricks Lakehouse (natural language → SQL)
  └→ Neo4j MCP Agent → Neo4j Aura (LangGraph + MCP tools: get-schema, read-cypher)
```

The MCP agent (`lab_setup/neo4j_mcp_connection/neo4j_mcp_agent.py`) uses OAuth2 M2M auth via Unity Catalog HTTP connection to an external MCP server.

### Lab Progression
Lab 0 (sign-in) → Lab 1 (Neo4j Aura setup) → Lab 5 (ETL via Spark Connector notebooks) → Lab 6 (GraphRAG semantic search over maintenance manuals) → Lab 7 (multi-agent supervisor)

## Configuration

Each tool reads from `.env` files (see `.env.example` in each directory). Key variables:
- **Neo4j**: `NEO4J_URI`, `NEO4J_USERNAME`, `NEO4J_PASSWORD`
- **LLM**: `LLM_PROVIDER` (openai/anthropic/azure), `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`
- **Databricks**: `DATABRICKS_PROFILE`, `DATABRICKS_ACCOUNT_ID`, `CATALOG_NAME`

All config uses Pydantic `BaseSettings` with `SecretStr` for passwords.

## Code Conventions

- **Typer** for all CLIs with **Rich** for colored output/tables
- Batch processing with `BATCH_SIZE=1000` for Neo4j data loading
- Context managers for Neo4j driver lifecycle
- Full type hints; `mypy --strict` enforced in auto_scripts
- Ruff linting with rules: E, W, F, I, B, C4, UP, SIM

## Key Reference Files

- `lab_setup/README.md` — Main admin setup guide with troubleshooting
- `lab_setup/aircraft_digital_twin_data/ARCHITECTURE.md` — Complete data schema reference (all 19 CSVs, dual-DB strategy, query patterns)
- `lab_setup/auto_scripts/README.md` — Databricks CLI reference with all config options
