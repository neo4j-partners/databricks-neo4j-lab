# populate-aircraft-db

Standalone CLI tool that loads the Aircraft Digital Twin dataset into a Neo4j Aura instance. The `setup` command handles the full pipeline: CSV data loading, maintenance manual chunking, OpenAI embedding generation, and LLM-powered entity extraction (OpenAI or Anthropic) via `neo4j-graphrag`'s `SimpleKGPipeline`.

## Quick Start

```bash
cd lab_setup/populate_aircraft_db

# Create .env with your Neo4j credentials (see .env.example)
cp .env.example .env
# Edit .env with your credentials

# Install and run
uv sync                              # OpenAI only
uv sync --extra anthropic            # include Anthropic support
uv run populate-aircraft-db clean
uv run populate-aircraft-db setup
```

## Commands

| Command | Description |
|---------|-------------|
| `setup` | Load CSV data into Neo4j and run GraphRAG enrichment (chunking, embeddings, entity extraction, cross-linking) in a single pass. Safe to re-run — uses MERGE for CSV data and clears enrichment data before re-enriching. |
| `samples` | Run sample queries showcasing the knowledge graph (read-only, no API keys needed) |
| `verify` | Print node and relationship counts (read-only) |
| `clean` | Delete all nodes and relationships |
| `clean-enrichment` | Delete enrichment data (Documents, Chunks, OperatingLimits) while preserving the operational graph |

All configuration is via `.env` — no command-line flags needed.

### Typical full-load sequence

```bash
uv run populate-aircraft-db clean
uv run populate-aircraft-db setup     # uses LLM_PROVIDER from .env (default: openai)
uv run populate-aircraft-db samples   # run sample queries to explore the graph
```

## Configuration

Settings are loaded from a `.env` file in the project root or from environment variables.

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `NEO4J_URI` | yes | - | Connection URI (e.g. `neo4j+s://...`) |
| `NEO4J_USERNAME` | no | `neo4j` | Neo4j username |
| `NEO4J_PASSWORD` | yes | - | Neo4j password |
| `OPENAI_API_KEY` | for setup | - | OpenAI API key (always needed — embeddings use OpenAI) |
| `OPENAI_EMBEDDING_MODEL` | no | `text-embedding-3-small` | Embedding model |
| `OPENAI_EMBEDDING_DIMENSIONS` | no | `1536` | Embedding dimensions |
| `OPENAI_EXTRACTION_MODEL` | no | `gpt-4o-mini` | Chat model for entity extraction (OpenAI) |
| `LLM_PROVIDER` | no | `openai` | LLM provider for extraction: `openai` or `anthropic` |
| `ANTHROPIC_API_KEY` | for setup (anthropic) | - | Anthropic API key |
| `ANTHROPIC_EXTRACTION_MODEL` | no | `claude-sonnet-4-5-20250929` | Chat model for entity extraction (Anthropic) |
| `CHUNK_SIZE` | no | `800` | Characters per chunk (setup) |
| `CHUNK_OVERLAP` | no | `100` | Overlap between chunks (setup) |
| `ENRICH_SAMPLE_SIZE` | no | `0` | Max chunks per document during setup (`0` = no limit) |
| `SAMPLE_SIZE` | no | `10` | Rows per section in the `samples` command |

## What Gets Loaded

### Phase 1: Operational graph (from CSVs)

**9 node types:** Aircraft, System, Component, Sensor, Airport, Flight, Delay, MaintenanceEvent, Removal

**12 relationship types:** HAS_SYSTEM, HAS_COMPONENT, HAS_SENSOR, HAS_EVENT, OPERATES_FLIGHT, DEPARTS_FROM, ARRIVES_AT, HAS_DELAY, AFFECTS_SYSTEM, AFFECTS_AIRCRAFT, HAS_REMOVAL, REMOVED_COMPONENT

CSV files are read from `lab_setup/aircraft_digital_twin_data/`.

### Phase 2: Document chunks, embeddings, and operating limits

Uses `neo4j-graphrag`'s `SimpleKGPipeline` to process three maintenance manuals (A320-200, A321neo, B737-800):

1. **Chunking**: Splits text into ~800-character chunks with overlap
2. **Embedding**: Generates OpenAI embeddings stored on Chunk nodes
3. **Entity extraction**: Extracts **OperatingLimit** entities (parameter limits per regime and aircraft type)
4. **Entity resolution**: Deduplicates entities with matching `name` property (via APOC)
5. **Cross-linking**:
   - **Document → Aircraft** (APPLIES_TO) — links each manual to fleet aircraft by model
   - **Sensor → OperatingLimit** (HAS_LIMIT) — matches sensors to extracted operating limits by parameter name and aircraft type

Creates indexes:
- **Vector index:** `maintenanceChunkEmbeddings` on `Chunk.embedding`
- **Fulltext index:** `maintenanceChunkText` on `Chunk.text`

**Note:** Entity resolution requires APOC, which is available on Neo4j Aura by default. See `FIX_MANUALS.md` for known sensor name mismatches.
