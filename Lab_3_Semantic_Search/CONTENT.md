# Lab 3: Concepts and Reference

Lab 2 loaded structured data into Neo4j: aircraft, systems, components, sensors, flights. The graph captures topology and operational history, but it cannot answer questions about maintenance procedures, troubleshooting steps, or fault diagnostics. That knowledge lives in unstructured documentation. Lab 3 bridges this gap by ingesting the A320-200 Maintenance Manual into the knowledge graph and enabling semantic search over it.

## GenAI Limitations

Large language models generate the most probable continuation of a prompt, not the most accurate. Three structural limitations make them unreliable for enterprise applications without additional architecture.

**Hallucination.** LLMs produce confident, detailed responses even when they have no factual basis. The outputs read as authoritative because the model optimizes for fluency, not correctness. Production systems need a way to ground responses in verified data.

**Knowledge cutoff.** Models are trained at a fixed point in time on publicly available text. They cannot access your maintenance records, last quarter's sensor telemetry, or this morning's flight data. They don't decline to answer; ask about data they've never seen and they generate a plausible response anyway.

**Relationship blindness.** LLMs process text sequentially and treat each piece of information in isolation. Questions like "which aircraft have engines with critical maintenance events?" require reasoning across chains of connected entities. Similarity search over document chunks cannot reconstruct those chains.

All three limitations share a common remedy: providing the right context at inference time. Graph databases ground responses in verified, structured data (hallucination). RAG retrieval surfaces proprietary information at query time (knowledge cutoff). Knowledge graph traversal preserves and exposes the relationships between entities (relationship blindness).

> **Context ROT: when more context makes things worse.**
>
> Research from Chroma demonstrates that irrelevant context doesn't just fail to help; it actively degrades LLM accuracy. As retrieved chunks increase in volume but decrease in relevance, the model's responses get worse, not better. Quality of context matters more than quantity. This is the core argument for GraphRAG over traditional RAG: graph-structured retrieval returns connected, relevant context rather than similar but unrelated chunks, because it follows explicit relationships between entities instead of relying solely on embedding distance.

## Embeddings and Vector Search

Embedding models read text and produce numerical vectors that capture what the text means, not just what it says. "Engine overheating" and "thermal runaway in turbine" produce similar vectors because they mean similar things, even though they share no keywords. This enables semantic similarity search: given a question, find the stored text whose meaning is most similar.

Vector search is what makes RAG work. The system embeds a question, searches for the closest chunks in vector space, and feeds those chunks to the LLM as context. The next step is preparing documents for this process.

## From Documents to a Knowledge Graph

The `neo4j-graphrag` Python package provides `SimpleKGPipeline` to orchestrate the full transformation from raw text to a queryable knowledge graph. The pipeline reads the maintenance manual, chunks it, uses an LLM to extract entities and relationships, stores the results in Neo4j, and generates vector embeddings for semantic search.

### Documents to Chunks

Documents split into Chunk nodes with raw text, linked to their source Document via `FROM_DOCUMENT` and to adjacent chunks via `NEXT_CHUNK` to preserve reading order. An embedding model converts each chunk's text into a vector. A vector index over these embeddings enables semantic search by meaning rather than keyword matching.

**Chunking trade-offs.** Larger chunks give the LLM more context during entity extraction, improving its ability to resolve references like "the engine" to a specific component. Smaller chunks produce more precise retrieval results, returning only the relevant passage rather than a block of mixed content. A moderate chunk size (500-1000 characters) with overlap at boundaries is a reasonable starting point, tuned by evaluating results.

### Chunks to Graph Structure

An LLM reads each chunk and extracts entities: regulations, thresholds, procedures, components. These become graph nodes linked to their source chunks via `FROM_CHUNK`. Entity resolution deduplicates: the same regulation mentioned across five different chunks becomes one node with five links, not five separate nodes. Cross-linking connects extracted entities to the existing operational graph built in Lab 2, so a procedure that applies to a specific system links directly to that system's node.

**Schema design.** SimpleKGPipeline supports three schema modes: User-Provided (you define the entity and relationship types), Extracted (the LLM discovers the schema), and Free (no constraints). This workshop uses User-Provided because the aircraft domain has known entity types (Aircraft, System, Component, Sensor, MaintenanceEvent) and known relationship patterns. Constraining extraction to these types produces a consistent, queryable graph.

**Entity resolution.** The same real-world component can surface under different names ("HP Turbine," "High-pressure Turbine," "HPT"). Entity resolution merges these duplicates so that queries return complete results. Without it, maintenance event counts and relationship traversals silently miss data.

## Knowledge Graph Structure

After completing this lab, the graph combines structured data from Lab 2 with unstructured maintenance documentation:

```
(:Document)--[:FROM_DOCUMENT]-->(:Chunk {text, embedding})--[:NEXT_CHUNK]-->(:Chunk)
                                         |
                                   [:FROM_CHUNK]
                                         |
                                         v
                          (:Regulation)  (:Threshold)  (:Procedure)
                                              |
                                        [:APPLIES_TO]
                                              v
              (:Aircraft)-[:HAS_SYSTEM]->(:System)-[:HAS_COMPONENT]->(:Component)
```

The top half is what Lab 3 adds. The bottom is what the Spark Connector built in Lab 2. Entity extraction bridges them: entities extracted from maintenance documentation link to the same aircraft, system, and component nodes loaded from structured data.

## GraphRAG: Graph-Enriched Retrieval

With the data pipeline complete and knowledge graph constructed, the graph holds both structured connections and documentary knowledge. Vector or fulltext search finds the chunks most relevant to the user's question. That's standard RAG. GraphRAG adds graph traversal from those chunks through the entities and relationships surrounding them.

When search returns a chunk about turbine overheating procedures, graph traversal follows the extracted entities to find the specific components, maintenance events, and systems connected to that chunk. The agent receives all of this as context, not just the chunk text. Without extracted entities linked to chunks and cross-linked to the operational graph, there would be nothing for the traversal to follow.

## Retriever Comparison: Vector vs. VectorCypher

The `neo4j-graphrag` package provides two retriever patterns relevant to this lab.

**VectorRetriever** performs pure semantic search. It converts the user's question to an embedding, finds the most similar chunks by vector index lookup, and returns their text. This works well for conceptual questions ("How do I troubleshoot engine vibration?") where the answer lives within the matched chunks themselves. The limitation is that it returns text only, with no awareness of the entities or relationships surrounding those chunks.

**VectorCypherRetriever** adds a graph traversal step after vector search. It finds semantically similar chunks the same way, then executes a custom Cypher query that traverses from each matched chunk to related entities in the graph. The chunk acts as an anchor: vector search determines relevance, then Cypher gathers the structured context around it. This is the retriever to reach for when answers require both the passage content and the entities connected to it.

The key constraint: traversal starts from what vector search found. If the question does not surface relevant chunks, no amount of graph traversal compensates. Questions targeting a specific entity by name ("How many faults affect AC1001?") may be better served by direct Cypher queries.

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
