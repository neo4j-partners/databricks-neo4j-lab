# Lab 3 Sync Plan

Status after the LLMInterfaceV2 migration and SimpleKGPipeline rewrite. The
notebook_validation run (run_lab3_03.py) completed with 15/15 PASS on the
Databricks cluster — the full KG is built and validated.

## What changed

Notebook 03 was rewritten from a manual chunking/embedding approach
(split_text, upsert_vectors) to use SimpleKGPipeline which handles chunking,
embedding, entity extraction (OperatingLimit), and entity resolution in one
pass. Notebook 04 was updated with new Cypher queries that traverse the
APPLIES_TO and HAS_LIMIT relationships created by the pipeline, plus a new
Example 4 (OperatingLimit queries). data_utils.py was updated to implement
both LLMInterface and LLMInterfaceV2 so DatabricksLLM works with both
SimpleKGPipeline (V1) and GraphRAG (V2).

## Three copies of Lab 3 files

All three locations are now synced. `Lab_3_Semantic_Search/` is the source
of truth — the other two are copies.

| Location | Purpose | Status |
|----------|---------|--------|
| `Lab_3_Semantic_Search/` | Source of truth (student-facing notebooks) | Updated |
| `lab_setup/notebook_validation/agent_modules/` | Automated cluster testing scripts | Synced |
| `vocareum/courseware/data/Lab_3_Semantic_Search/` | Vocareum LMS distribution | Synced |

## Sync checklist

### 1. Vocareum data_utils.py

- [x] Copied `Lab_3_Semantic_Search/data_utils.py` to
      `vocareum/courseware/data/Lab_3_Semantic_Search/data_utils.py`

### 2. Vocareum notebook 03

- [x] Copied `Lab_3_Semantic_Search/03_data_and_embeddings.ipynb` to
      `vocareum/courseware/data/Lab_3_Semantic_Search/03_data_and_embeddings.ipynb`

### 3. Vocareum notebook 04

- [x] Copied `Lab_3_Semantic_Search/04_graphrag_retrievers.ipynb` to
      `vocareum/courseware/data/Lab_3_Semantic_Search/04_graphrag_retrievers.ipynb`

### 4. Vocareum notebook 05/06 renumbering

- [x] Renamed `vocareum/.../05_hybrid_retrievers.ipynb` to `06_hybrid_retrievers.ipynb`
- [x] Copied `Lab_3_Semantic_Search/05_mcp_graph_queries.ipynb` to vocareum
- Vocareum now has: 03, 04, 05 (MCP), 06 (hybrid) — matches source of truth

### 5. notebook_validation data_utils.py

- [x] Copied `Lab_3_Semantic_Search/data_utils.py` to
      `lab_setup/notebook_validation/agent_modules/data_utils.py`
- All three copies are now byte-identical

### 6. Site documentation (Antora)

- [x] Verified — no changes needed
- `site/modules/ROOT/pages/lab3.adoc` already references SimpleKGPipeline
- `site/modules/ROOT/pages/lab3-instructions.adoc` already has correct
  notebook numbering (03, 04, 05 MCP, 06 hybrid) and Path A / Path B structure
- No references to old approach (split_text, upsert_vectors) in site docs

### 7. notebook_validation script updates

- [x] Renamed `verify_lab6.py` to `run_lab3_05.py` (matches Lab 3 notebook 05
      naming convention, consistent with `run_lab3_03.py`)
- [x] Created `run_lab3_04.py` — validates all retriever patterns from
      notebook 04: VectorRetriever, GraphRAG, VectorCypherRetriever with
      document context, adjacent chunks, APPLIES_TO topology, and
      OperatingLimit queries
- [ ] Upload and run `run_lab3_04.py` on Databricks cluster to validate
