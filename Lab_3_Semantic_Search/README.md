# Lab 3 - Semantic Search for Aircraft Maintenance

In this lab, you'll add semantic search capabilities to your aircraft knowledge graph. Building on the aircraft topology loaded in Lab 2, you'll create a Document-Chunk structure for the A320-200 Maintenance Manual and enable AI-powered retrieval of maintenance procedures.

> **Background Reading:** For the concepts and architecture behind this lab, see [CONTENT.md](CONTENT.md).

> **Infrastructure:** This lab uses your **personal** Aura instance. You'll load maintenance manual chunks and generate embeddings into the graph you built in Lab 2.

## Prerequisites

Before starting, make sure you have:
- Completed **Lab 2** (Databricks ETL) to load the aircraft graph (Aircraft, System, Component nodes)
- Neo4j Aura credentials from Lab 1 (URI, username, password)
- Running in a **Databricks notebook environment** (for Foundation Model API access)
- **Maintenance manual uploaded** to the Unity Catalog Volume

## Lab Overview

This lab consists of two core notebooks that add semantic search to your existing knowledge graph, plus an optional third notebook for hybrid retrieval:

### 03_data_and_embeddings.ipynb - Data Preparation
Build the foundation for semantic search over maintenance documentation:
- Understand the Document -> Chunk graph structure
- Load the A320-200 Maintenance Manual into Neo4j
- Create Document and Chunk nodes with relationships
- Generate embeddings using Databricks Foundation Model APIs (BGE-large)
- Create a vector index in Neo4j
- Perform similarity search to find relevant maintenance procedures

### 04_graphrag_retrievers.ipynb - Retrieval Strategies
Learn retrieval patterns from simple to graph-enhanced:
- Set up a VectorRetriever using Neo4j's vector index
- Use GraphRAG to combine vector search with LLM-generated answers
- Create custom Cypher queries with VectorCypherRetriever
- Connect maintenance documentation to your aircraft topology
- Compare standard vs. graph-enhanced retrieval results

### 05_hybrid_retrievers.ipynb - Hybrid Search (Optional)
Combine vector similarity with keyword-based fulltext search for more robust retrieval:
- Use HybridRetriever and HybridCypherRetriever to blend vector and keyword results
- Compare hybrid retrieval against pure vector search

## Configuration

Each notebook has a **Configuration** cell at the top where you enter your Neo4j credentials:

```python
NEO4J_URI = ""  # e.g., "neo4j+s://xxxxxxxx.databases.neo4j.io"
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = ""  # Your password from Lab 1
```

The embedding and LLM models use Databricks Foundation Model APIs which are pre-deployed and require no additional configuration. When running in Databricks, the MLflow deployments client automatically handles authentication.

## Getting Started

1. Ensure Lab 2 is complete (aircraft topology loaded)
2. Verify the maintenance manual is uploaded to the Volume:
   ```
   /Volumes/databricks-neo4j-lab/lab-schema/lab-volume/MAINTENANCE_A320.md
   ```
3. Upload the notebook files and `data_utils.py` to your Databricks workspace
4. Open `03_data_and_embeddings.ipynb`
5. Enter your Neo4j credentials in the Configuration cell
6. Run cells sequentially to load the maintenance manual and create embeddings
7. Continue to `04_graphrag_retrievers.ipynb` for retrieval strategies

## Files

| File | Description |
|------|-------------|
| `03_data_and_embeddings.ipynb` | Data loading and embedding generation |
| `04_graphrag_retrievers.ipynb` | Retrieval strategies and GraphRAG |
| `05_hybrid_retrievers.ipynb` | Hybrid search combining vector + keyword retrieval |
| `data_utils.py` | Utility functions for Neo4j and Databricks |
| `CONTENT.md` | Concepts and reference (knowledge graph structure, Foundation Model APIs, key concepts) |
| `README.md` | This file |

**Note:** The `MAINTENANCE_A320.md` file must be uploaded to the Unity Catalog Volume before running the notebooks.

## Next Steps

Congratulations! You've completed the Semantic Search lab. You can now combine vector search with graph traversal to build powerful GraphRAG retrievers.

Copy and paste queries from the [Sample Queries](SAMPLE_QUERIES.md) page to explore the Document-Chunk structure and verify your vector indexes in the Neo4j Query Workspace.
