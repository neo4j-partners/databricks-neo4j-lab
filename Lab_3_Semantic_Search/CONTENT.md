# Lab 3: Concepts and Reference

Lab 2 loaded structured data into Neo4j: aircraft, systems, components, sensors, flights. The graph captures topology and operational history, but it cannot answer questions about maintenance procedures, troubleshooting steps, or fault diagnostics. That knowledge lives in unstructured documentation. Lab 3 bridges this gap by ingesting the A320-200 Maintenance Manual into the knowledge graph and enabling semantic search over it.

## From RAG to GraphRAG

Traditional RAG retrieves text chunks by embedding similarity and passes them to an LLM as context. This works well for single-document questions but struggles when answers require connecting information across entities, following causal chains through related components, or filtering results by graph structure. These are symptoms of what the workshop overview describes as Context ROT, where vector similarity alone retrieves context that is plausible but incomplete. GraphRAG addresses this by grounding retrieval in a knowledge graph. Instead of returning isolated text fragments, it can traverse from a semantically matched chunk to the entities, relationships, and metadata that give that chunk meaning.

## Building the Knowledge Graph from Documents

The `neo4j-graphrag` Python package provides `SimpleKGPipeline` to orchestrate the transformation from raw text to a queryable knowledge graph. The pipeline reads the maintenance manual, chunks it, uses an LLM to extract entities and relationships, stores the results in Neo4j, and generates vector embeddings for semantic search.

Several design decisions shape the quality of that graph:

**Schema design.** SimpleKGPipeline supports three schema modes: User-Provided (you define the entity and relationship types to extract), Extracted (the LLM discovers the schema from documents), and Free (no constraints). This workshop uses a User-Provided schema because the aircraft domain has known entity types (Aircraft, System, Component, Sensor, MaintenanceEvent) and known relationship patterns. Constraining extraction to these types produces a consistent, queryable graph rather than a noisy one.

**Chunking trade-offs.** Larger chunks give the LLM more context during entity extraction, improving its ability to resolve references like "the engine" to a specific component. Smaller chunks produce more precise retrieval results, returning only the relevant passage rather than a block of mixed content. The tension is real: optimizing for extraction quality and retrieval precision pull in opposite directions. A moderate chunk size (500-1000 characters) with overlap at boundaries is a reasonable starting point, tuned by evaluating results.

**Entity resolution.** When an LLM extracts entities from text, the same real-world component can surface under different names ("HP Turbine," "High-pressure Turbine," "HPT"). Entity resolution merges these duplicates so that queries against the graph return complete results. Without it, maintenance event counts and relationship traversals silently miss data.

## Knowledge Graph Structure

After completing this lab, the graph combines structured data from Lab 2 with unstructured maintenance documentation:

**From Lab 2 (Structured Data):**
```
(:Aircraft)-[:HAS_SYSTEM]->(:System)-[:HAS_COMPONENT]->(:Component)
```

**From Lab 3 (Unstructured Data):**
```
(:Document) <-[:FROM_DOCUMENT]- (:Chunk) -[:NEXT_CHUNK]-> (:Chunk)
```

The Document-Chunk structure breaks the maintenance manual into smaller pieces suitable for embedding and retrieval. Each Chunk links back to its parent Document and forward to the next Chunk, preserving reading order. Entities extracted from chunks connect to the same nodes loaded in Lab 2, linking unstructured knowledge to the structured topology.

## Retriever Comparison: Vector vs. VectorCypher

With chunks embedded and stored in Neo4j, retrieval determines how much of the graph's structure reaches the LLM. The `neo4j-graphrag` package provides two retriever patterns relevant to this lab.

**VectorRetriever** performs pure semantic search. It converts the user's question to an embedding, finds the most similar chunks by vector index lookup, and returns their text. This works well for conceptual questions ("How do I troubleshoot engine vibration?") where the answer lives within the matched chunks themselves. The limitation is that it returns text only, with no awareness of the entities or relationships surrounding those chunks.

**VectorCypherRetriever** adds a graph traversal step after vector search. It finds semantically similar chunks the same way, then executes a custom Cypher query that traverses from each matched chunk to related entities in the graph. The chunk acts as an anchor: vector search determines relevance, then Cypher gathers the structured context around it. This is the retriever to reach for when answers require both the passage content and the entities connected to it, such as "What maintenance events are associated with the systems described in this troubleshooting procedure?"

The key constraint of VectorCypherRetriever is that traversal starts from what vector search found. If the question does not surface relevant chunks, no amount of graph traversal compensates. Questions targeting a specific entity by name ("How many faults affect AC1001?") may be better served by direct Cypher queries rather than embedding-based retrieval.

## Databricks Foundation Model APIs

This lab uses Databricks-hosted embedding and LLM models, pre-deployed and accessible via the MLflow deployments client.

| Model | Type | Details |
|-------|------|---------|
| `databricks-bge-large-en` | Embedding (1024-dim) | 512 token context, used for chunk embeddings |
| `databricks-gte-large-en` | Embedding (1024-dim) | 8192 token context, for longer documents |
| `databricks-meta-llama-3-3-70b-instruct` | LLM | Llama 3.3 70B (default) |
| `databricks-llama-4-maverick` | LLM | Llama 4 Maverick |

The maintenance manual is loaded from the Unity Catalog Volume at:
```
/Volumes/databricks-neo4j-lab/lab-schema/lab-volume/MAINTENANCE_A320.md
```

## Sample Questions

After completing this lab, you can ask questions like:
- "How do I troubleshoot engine vibration?"
- "What are the EGT limits during takeoff?"
- "What causes hydraulic pressure loss?"
- "When should I replace the fuel filter?"
- "What oil analysis levels indicate bearing wear?"
