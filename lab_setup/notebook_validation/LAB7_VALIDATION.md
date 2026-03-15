# Lab 7 Validation: Embedding and Semantic Translation Pipeline

## The Problem

Lab 7 teaches participants to build a GraphRAG semantic search layer over aircraft maintenance documentation. The pipeline is four operations in sequence: load the maintenance manual from a Unity Catalog Volume, split it into chunks with a fixed-size splitter, generate embeddings through the Databricks Foundation Model API, and create vector and fulltext indexes in Neo4j for similarity and keyword search. Each operation depends on the previous one succeeding, and the final search quality depends on every intermediate step producing the right artifacts. A participant who gets garbled search results at the end has no way to know whether the problem was in the chunking, the embedding, the index creation, or the search query.

The validation script replicates the exact Lab 7 pipeline, using the same models, the same chunking parameters, and the same index configuration, then runs verification queries at each stage. It follows the upload-and-submit pattern already working for Lab 5 validation: a standalone Python script that runs on a dedicated admin cluster via `submit.sh`, with PASS/FAIL assertions that a workshop administrator can check before participants arrive.

The gap this fills is specific. `run_lab5_02.py` validates the structural graph (Aircraft, System, Component nodes and relationships loaded via Spark Connector). Lab 7 validation covers the semantic layer that sits on top of that graph: Document and Chunk nodes, embedding vectors, indexes, and retrieval quality. Together, the two scripts confirm that the complete knowledge graph is ready for Lab 7's retriever notebooks and, subsequently, the agent memory prototype's knowledge tools.


## Scope: A Clean Full-Pipeline Validation

The validation suite is a complete, independent run-through of the workshop data pipeline using Databricks-hosted models exclusively. It starts with Lab 5 (resetting the Neo4j database and loading the structural graph), then proceeds through Lab 7 (building the semantic layer with Databricks BGE embeddings). This is deliberately separate from the `populate_aircraft_db` CLI tool, which uses OpenAI embeddings at 1536 dimensions. The validation standardizes on `databricks-bge-large-en` at 1024 dimensions for all embedding operations, matching what participants experience in the lab notebooks.

The Lab 7 script always clears existing Document and Chunk nodes before creating new ones. This ensures no stale embeddings from prior runs or from `populate_aircraft_db` contaminate the validation. Lab 5 runs first and establishes a clean structural graph; Lab 7 assumes that structural graph exists and builds on top of it.


## What the Validation Covers

The validation script mirrors all three Lab 7 notebooks: data and embeddings (notebook 03), GraphRAG retrievers (notebook 04), and hybrid retrievers (notebook 05). Each stage produces artifacts the next stage depends on, so the validation checks accumulate.

### Stage 1: Document-Chunk Graph Structure

Load the A320-200 Maintenance Manual from the Unity Catalog Volume at `/Volumes/databricks-neo4j-lab/lab-schema/lab-volume/MAINTENANCE_A320.md`. Clear any existing Document and Chunk nodes to guarantee clean embeddings. Split the text into chunks using `FixedSizeSplitter` with the same parameters Lab 7 uses: 800-character chunks with 100-character overlap. Create a Document node with metadata (`documentId: AMM-A320-2024-001`, `type: Maintenance Manual`, `aircraftType: A320-200`), create Chunk nodes linked to the Document via `FROM_DOCUMENT` relationships, and chain them with `NEXT_CHUNK` relationships.

Validation checks:
- Document node exists with correct metadata
- Every Chunk has a `FROM_DOCUMENT` relationship to the Document
- Sequential `NEXT_CHUNK` chain is unbroken (first chunk has no inbound NEXT_CHUNK, last chunk has no outbound, every intermediate chunk has exactly one of each)
- No orphaned Chunks exist without a Document relationship
- Chunk text is non-empty and within the expected size range

### Stage 2: Embedding Generation and Storage

Generate embeddings for every Chunk using `databricks-bge-large-en` via the Databricks Foundation Model API (MLflow deployments client). Store them on Chunk nodes as an `embedding` property using `upsert_vectors` from the `neo4j-graphrag` library.

This uses the same model, the same API path, and the same storage method as Lab 7's notebook 03. The embedding model produces 1024-dimensional vectors. The script runs on a dedicated admin cluster, so Foundation Model API rate limits should not be a concern. The Databricks API does support batch embedding (multiple texts in a single `{"input": ["text1", "text2"]}` call), though the current `data_utils.DatabricksEmbeddings` wrapper and the `neo4j-graphrag` `Embedder` base class only expose single-text `embed_query`. Batch embedding is a later optimization.

Validation checks:
- Every Chunk node has an `embedding` property
- Every embedding is a list of exactly 1024 floats
- No embedding is a zero vector (all-zeros would indicate a failed API call that returned a default)
- Embeddings for semantically distinct chunks have cosine similarity below a threshold (confirms the model is producing differentiated vectors, not identical outputs)
- Embeddings for semantically similar content have higher similarity than unrelated chunks (a basic sanity check on vector quality)

### Stage 3: Index Creation and Search

Create the vector index `maintenanceChunkEmbeddings` on the Chunk label's `embedding` property (1024 dimensions, cosine similarity). Create the fulltext index `maintenanceChunkText` on the Chunk label's `text` property. Both use `create_vector_index` and `create_fulltext_index` from the `neo4j-graphrag` library, matching Lab 7 exactly.

After index creation, the script polls `SHOW INDEXES` every 10 seconds for up to 5 minutes, waiting for both indexes to reach ONLINE status. If either index is not ONLINE after 5 minutes, the script fails with an error.

Validation checks:
- Vector index `maintenanceChunkEmbeddings` exists and is ONLINE
- Fulltext index `maintenanceChunkText` exists and is ONLINE
- Vector similarity search for "How do I troubleshoot engine vibration?" returns results with scores above a midrange threshold (0.80 initial target; calibrate in a later phase against known-good runs)
- Vector search results contain text relevant to engine troubleshooting (keyword presence check)
- Fulltext search for "EGT limits" returns chunks containing that term
- A semantically rephrased query ("vibration exceedance diagnosis procedure") returns overlapping results with the direct query, confirming semantic matching works beyond keyword overlap

### Stage 4: Retriever Validation

Instantiate retrievers from the `neo4j-graphrag` library and run them against test queries with the Databricks LLM endpoint (`databricks-meta-llama-3-3-70b-instruct`).

**Vector retrievers** (notebook 04):
- `VectorRetriever` for basic semantic search with LLM answer generation
- `VectorCypherRetriever` with two Cypher patterns: document metadata enrichment and adjacent chunk retrieval via NEXT_CHUNK (the topology connection pattern that links to Lab 5's Aircraft/System nodes is deferred)

**Hybrid retrievers** (notebook 05):
- `HybridRetriever` combining vector similarity with fulltext keyword search
- `HybridCypherRetriever` for graph-enhanced hybrid search

Hybrid queries use two complementary approaches: natural-language queries (same as the vector checks, verifying hybrid produces equal or better results) and queries that mix semantic intent with exact technical terms pulled from the maintenance manual (fault codes, part numbers like V2500-A1, specific procedure references).

Validation checks:
- `VectorRetriever` returns a non-empty response for a maintenance query
- `VectorCypherRetriever` with a metadata enrichment query returns document context alongside the chunk
- `VectorCypherRetriever` with a NEXT_CHUNK adjacency query returns additional context beyond the base vector hit
- `HybridRetriever` returns results for a natural-language maintenance query
- `HybridRetriever` returns results for a fault-code-specific query (e.g., "V2500-A1 vibration troubleshooting")
- `HybridCypherRetriever` returns graph-enriched results
- LLM-generated answers reference content from the retrieved chunks (basic keyword presence check against source chunk text)


## Models and Configuration

The validation script uses the identical models and parameters as Lab 7's notebooks and `data_utils.py`:

| Component | Value | Source |
|-----------|-------|--------|
| Embedding model | `databricks-bge-large-en` | `data_utils.DEFAULT_EMBEDDING_MODEL` |
| Embedding dimensions | 1024 | `data_utils.EMBEDDING_DIMENSIONS` |
| Embedding API | MLflow deployments client (`mlflow.deployments.get_deploy_client("databricks")`) | `data_utils.DatabricksEmbeddings` |
| LLM model (retrievers) | `databricks-meta-llama-3-3-70b-instruct` | `data_utils.DEFAULT_LLM_MODEL` |
| Chunk size | 800 characters | Lab 7 notebook 03 |
| Chunk overlap | 100 characters | Lab 7 notebook 03 |
| Text splitter | `FixedSizeSplitter(approximate=True)` | `data_utils.split_text` |
| Vector index name | `maintenanceChunkEmbeddings` | Lab 7 notebook 03 |
| Fulltext index name | `maintenanceChunkText` | Lab 7 notebook 03 |
| Similarity function | Cosine | Lab 7 notebook 03 |
| Vector storage | `upsert_vectors` from `neo4j-graphrag` | Lab 7 notebook 03 |
| Data source | `/Volumes/databricks-neo4j-lab/lab-schema/lab-volume/MAINTENANCE_A320.md` | Lab 7 notebook 03 |
| Index wait timeout | 5 minutes (poll every 10s) | Validation-specific |
| Search score threshold | 0.80 (initial midrange; calibrate later) | Validation-specific |


## Script Structure

The script follows the same pattern as `run_lab5_02.py`: a standalone Python file that accepts command-line arguments for Neo4j credentials and data path, runs on the admin cluster via `submit.sh`, and reports PASS/FAIL for each check.

```
run_lab7_03.py
├── Argument parsing (--neo4j-uri, --neo4j-password, --data-path)
├── Clear existing Document/Chunk nodes and related indexes
├── Stage 1: Document-Chunk graph
│   ├── Load maintenance manual from Volume
│   ├── Split text into chunks
│   ├── Create Document node
│   ├── Create Chunk nodes with FROM_DOCUMENT
│   ├── Create NEXT_CHUNK chain
│   └── Verify graph structure (5 checks)
├── Stage 2: Embeddings
│   ├── Initialize DatabricksEmbeddings (BGE-large)
│   ├── Generate embeddings for all chunks
│   ├── Store via upsert_vectors
│   └── Verify embeddings (5 checks)
├── Stage 3: Indexes and search
│   ├── Create vector index
│   ├── Create fulltext index
│   ├── Poll for ONLINE status (5 min timeout)
│   ├── Run vector and fulltext test queries
│   └── Verify search quality (6 checks)
├── Stage 4: Retrievers
│   ├── VectorRetriever + LLM
│   ├── VectorCypherRetriever + LLM
│   ├── HybridRetriever + LLM
│   ├── HybridCypherRetriever + LLM
│   └── Verify retriever responses (7 checks)
├── Summary (total PASS/FAIL counts)
└── Exit code (0 if all pass, 1 if any fail)
```

A copy of Lab 7's `data_utils.py` lives in the notebook_validation directory and is uploaded alongside the script. The script imports `DatabricksEmbeddings`, `DatabricksLLM`, `Neo4jConnection`, `VolumeDataLoader`, `split_text`, and the model constants directly. This keeps the validation aligned with the lab code. The file is copied rather than symlinked because `data_utils.py` is stable and unlikely to change frequently.


## Relationship to populate_aircraft_db

The `populate_aircraft_db` CLI tool is a completely separate admin pre-population path. It runs a more extensive GraphRAG enrichment pipeline over three maintenance manuals (A320-200, A321neo, B737-800) using `SimpleKGPipeline` from `neo4j-graphrag`, extracting `OperatingLimit` entities, creating `APPLIES_TO` and `HAS_LIMIT` relationships, and using a context-prepending splitter that adds aircraft type metadata to every chunk. It currently uses OpenAI embeddings (1536 dimensions) but should be updated to use Databricks embeddings (`databricks-bge-large-en`, 1024 dimensions) to standardize across the project while retaining its full entity extraction capabilities.

The validation suite does not replicate or validate the `populate_aircraft_db` pipeline. The two serve different purposes: `populate_aircraft_db` is the admin enrichment tool with full entity extraction; the validation suite replicates the participant-facing Lab 7 notebook experience. They should not run against the same database instance simultaneously. The validation always clears Document and Chunk nodes before running to prevent stale data.


## Deployment

The full validation runs as two scripts in sequence on the admin cluster:

```bash
# Upload all files (Lab 5 script, Lab 7 script, data_utils.py)
./upload.sh --all

# Step 1: Reset database and load structural graph
./submit.sh run_lab5_02.py

# Step 2: Build semantic layer and validate
./submit.sh run_lab7_03.py
```

The `.env` configuration is unchanged from Lab 5 validation. Both scripts use the same `NEO4J_URI`, `NEO4J_USERNAME`, `NEO4J_PASSWORD`, and `DATA_PATH` variables.


---


## Phased Implementation Plan

### Phase 1: Core Embedding Pipeline

Build `run_lab7_03.py` with Stages 1-3: Document-Chunk graph creation, embedding generation via `databricks-bge-large-en`, vector and fulltext index creation, and basic search validation.

**Deliverables:**
- `run_lab7_03.py` with argument parsing, graph structure creation, embedding generation, index creation with 5-minute polling, and vector/fulltext search checks
- Upload `data_utils.py` from Lab 7 alongside the script
- PASS/FAIL reporting matching `run_lab5_02.py` pattern
- Midrange search score threshold (0.80) with keyword presence checks

**Depends on:** `run_lab5_02.py` executing successfully (clean structural graph in place)

**Validates:** Lab 7 notebook 03 (data and embeddings)

### Phase 2: Retriever Validation

Add Stage 4: vector retrievers and hybrid retrievers with LLM answer generation.

**Deliverables:**
- `VectorRetriever` and `VectorCypherRetriever` checks with `databricks-meta-llama-3-3-70b-instruct`
- `HybridRetriever` and `HybridCypherRetriever` checks
- LLM response validation (keyword presence against source chunks)
- Two VectorCypherRetriever patterns: Document metadata enrichment and NEXT_CHUNK adjacency (topology connection deferred)
- Hybrid queries using both natural-language and fault-code-specific test cases

**Depends on:** Phase 1 (indexes ONLINE, embeddings stored)

**Validates:** Lab 7 notebooks 04 and 05

### Phase 3: Search Quality Calibration

Run the Phase 1-2 script against a known-good Neo4j instance and record baseline scores for all test queries. Replace the midrange threshold with calibrated values.

**Deliverables:**
- Baseline score recording for all vector, fulltext, and hybrid queries
- Calibrated thresholds per query (replace the 0.80 default)
- Semantic overlap validation (rephrased queries returning similar chunks)
- Report of expected score ranges for workshop administrators

**Depends on:** Phase 2 complete, access to a stable Neo4j Aura instance with known-good data

### Phase 4: Batch Embedding Optimization

The Databricks Foundation Model API supports batch embedding (multiple texts in a single `{"input": [...]}` call), but the current `DatabricksEmbeddings.embed_query` wrapper and the `neo4j-graphrag` `Embedder` base class only handle single texts. This phase adds an `embed_batch` method to reduce API calls.

**Deliverables:**
- `embed_batch(texts: list[str]) -> list[list[float]]` method on `DatabricksEmbeddings`
- Batch size tuning (determine maximum texts per API call before the endpoint rejects)
- Updated embedding generation in `run_lab7_03.py` to use batch calls
- Fallback to sequential `embed_query` if batch call fails

**Depends on:** Phase 1 working; API batch limit testing on admin cluster

### Phase 5: Full Pipeline Orchestration

Create an orchestration script or wrapper that runs the complete validation sequence: Lab 5 (database reset + structural graph) followed by Lab 7 (semantic layer), with a single PASS/FAIL summary across both scripts.

**Deliverables:**
- Orchestration script (`run_full_validation.sh` or `run_full_validation.py`)
- Combined summary output spanning Lab 5 and Lab 7 checks
- Single exit code for CI-style pass/fail
- Timing output per stage for identifying bottlenecks

**Depends on:** Phases 1-2 stable


---


## Resolved Decisions

All open questions from the initial proposal and subsequent review have been resolved. These decisions are incorporated into the body above but collected here for reference.

1. **Index readiness:** Poll `SHOW INDEXES` every 10 seconds, 5-minute timeout, error on failure.
2. **Idempotency:** Lab 7 always clears Document/Chunk nodes before running. Lab 5 runs first and provides the clean structural graph.
3. **data_utils.py:** Copy into notebook_validation directory; upload alongside the script via `./upload.sh --all`.
4. **Expected chunk count:** Skip count validation for now.
5. **Embedding rate limits:** Runs on dedicated admin cluster; rate limits not a concern. Batch embedding API exists but deferred to Phase 4.
6. **Search quality thresholds:** 0.80 midrange initial target; calibrate in Phase 3 against known-good runs.
7. **Stale embeddings:** Always clear Document/Chunk nodes before running. Standardize on Databricks embeddings throughout.
8. **Hybrid retrievers:** Included in Stage 4 validation.
9. **LLM retriever validation:** Included in Stage 4; basic keyword presence check against source chunks.
10. **Full pipeline scope:** Complete separate run-through starting from Lab 5 database reset, Databricks embeddings only.
11. **Hybrid query design:** Both natural-language queries and fault-code-specific queries with technical terms from the manual.
12. **LLM answer criteria:** Basic keyword presence for initial phases; MLflow Agent Evaluation as future upgrade.
13. **VectorCypherRetriever patterns:** Two patterns (Document metadata enrichment, NEXT_CHUNK adjacency). Topology connection to Lab 5 nodes deferred.
14. **upload.sh approach:** Copy `data_utils.py` into notebook_validation rather than cross-directory upload.
15. **populate_aircraft_db:** Completely separate admin pre-population tool. Should be updated to use Databricks embeddings while retaining full entity extraction.