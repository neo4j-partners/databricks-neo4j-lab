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

| Location | Purpose | Status |
|----------|---------|--------|
| `Lab_3_Semantic_Search/` | Source of truth (student-facing notebooks) | Updated |
| `lab_setup/notebook_validation/agent_modules/` | Automated cluster testing scripts | Updated |
| `vocareum/courseware/data/Lab_3_Semantic_Search/` | Vocareum LMS distribution | Stale — still has old approach |

## Sync checklist

### 1. Vocareum data_utils.py

- [ ] Copy updated `Lab_3_Semantic_Search/data_utils.py` to
      `vocareum/courseware/data/Lab_3_Semantic_Search/data_utils.py`
- The vocareum copy currently uses LLMInterfaceV2-only (no dual inheritance)
  and is missing all SimpleKGPipeline-related code: TextSplitter,
  ContextPrependingSplitter, FixedSizeSplitter, TextChunks,
  build_extraction_schema, EXTRACTION_PROMPT, run_pipeline, split_text
- Decision needed: the vocareum copy deliberately stripped SimpleKGPipeline
  code. If vocareum notebooks are also being updated to use SimpleKGPipeline,
  copy the full file. If vocareum keeps the manual approach, leave it as-is.

### 2. Vocareum notebook 03

- [ ] Copy updated `Lab_3_Semantic_Search/03_data_and_embeddings.ipynb` to
      `vocareum/courseware/data/Lab_3_Semantic_Search/03_data_and_embeddings.ipynb`
- The vocareum copy still uses the old manual approach (split_text,
  upsert_vectors, no entity extraction, no APPLIES_TO/HAS_LIMIT)

### 3. Vocareum notebook 04

- [ ] Copy updated `Lab_3_Semantic_Search/04_graphrag_retrievers.ipynb` to
      `vocareum/courseware/data/Lab_3_Semantic_Search/04_graphrag_retrievers.ipynb`
- The vocareum copy still uses the old Example 3 (keyword-based system
  matching via CALL subquery) instead of the APPLIES_TO traversal
- The vocareum copy is missing Example 4 (OperatingLimit queries)

### 4. Vocareum notebook 05

- [ ] Verify `Lab_3_Semantic_Search/05_hybrid_retrievers.ipynb` matches
      `vocareum/courseware/data/Lab_3_Semantic_Search/05_hybrid_retrievers.ipynb`
- Notebook 05 imports only `Neo4jConnection, get_llm, get_embedder` from
  data_utils — no SimpleKGPipeline dependencies. Should work with either
  version of data_utils.py as long as the KG is built.

### 5. Minor data_utils.py drift between Lab_3 and notebook_validation

- [ ] Decide whether to keep or reconcile the minor differences between
      `Lab_3_Semantic_Search/data_utils.py` and
      `lab_setup/notebook_validation/agent_modules/data_utils.py`
- Differences are cosmetic: import line wrapping and a longer docstring on
  ContextPrependingSplitter in the Lab_3 copy. Functionally identical.

### 6. Lab 6 notebook reference

- [ ] Verify `Lab_6_MCP_Queries/06_mcp_graph_queries.ipynb` works with the
      updated KG (it was referenced in notebook 04's summary cell)
- This is a new untracked directory — confirm it is complete and tested
