# Lab 4 - GraphRAG with Neo4j

This lab teaches you how to build Graph Retrieval-Augmented Generation (GraphRAG) applications using the official **neo4j-graphrag** Python library with **Databricks Model Serving**. Through two hands-on notebooks, you'll progress from loading data to building production-ready GraphRAG pipelines.


## Before You Begin

> [!IMPORTANT]
> Complete these steps before running the notebooks.

**Prerequisites:**
- Lab 1 completed (Neo4j Aura database running)
- Databricks workspace with Model Serving enabled

**Configure Credentials:**

Open `CONFIG.txt` in the root folder and add your credentials:

```ini
# Neo4j Aura (add your credentials from Lab 1)
NEO4J_URI=neo4j+s://xxxxxxxx.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password_here

# Databricks Model Serving
DATABRICKS_HOST=https://your-workspace.cloud.databricks.com
DATABRICKS_TOKEN=dapi-your-token-here

# Optional: Override default model endpoints
# DATABRICKS_LLM_ENDPOINT=databricks-meta-llama-3-3-70b-instruct
# DATABRICKS_EMBEDDING_ENDPOINT=databricks-gte-large-en
```

### Databricks Foundation Model APIs

This lab uses [Databricks Foundation Model APIs](https://docs.databricks.com/aws/en/machine-learning/foundation-model-apis/) for embeddings and LLM inference:

| Model | Endpoint | Dimensions | Description |
|-------|----------|------------|-------------|
| **GTE** | `databricks-gte-large-en` | 1024 | General Text Embedding for semantic search |
| **Llama 3.3** | `databricks-meta-llama-3-3-70b-instruct` | - | Default LLM for text generation |

> [!NOTE]
> Foundation Model APIs are available in **pay-per-token** mode (easy to start) or **provisioned throughput** mode (for production workloads).


## What is GraphRAG?

GraphRAG combines vector search with graph relationships for richer context:

```
Traditional RAG: Question → Vector Search → Chunks → LLM → Answer
GraphRAG:        Question → Vector Search → Chunks → Graph Traversal → Enriched Context → LLM → Answer
```

The graph structure allows you to follow relationships, understand entity connections, and retrieve contextual information not present in the original text.

---

## Notebook 1: Data Loading and Embeddings

**Run [`01_data_and_embeddings.ipynb`](01_data_and_embeddings.ipynb)**

Learn the foundational graph structure and enable semantic search:

### The Document-Chunk Model

Documents are split into chunks linked by relationships:

```
┌──────────┐     NEXT_CHUNK      ┌──────────┐     NEXT_CHUNK      ┌──────────┐
│  Chunk   │────────────────────▶│  Chunk   │────────────────────▶│  Chunk   │
│  (1)     │                     │  (2)     │                     │  (3)     │
└────┬─────┘                     └────┬─────┘                     └────┬─────┘
     │ FROM_DOCUMENT                  │ FROM_DOCUMENT                  │ FROM_DOCUMENT
     ▼                                ▼                                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                               Document                                       │
└─────────────────────────────────────────────────────────────────────────────┘
```

### What You'll Do
- Load sample SEC 10-K filing text
- Split text into chunks using `FixedSizeSplitter`
- Generate embeddings with Databricks GTE via Foundation Model APIs
- Store Document/Chunk nodes with embeddings in Neo4j
- Create a vector index (`chunkEmbeddings`)
- Verify with a test similarity search

**Expected outcome:** A graph with embedded chunks ready for retrieval.

---

## Notebook 2: GraphRAG Retrievers

**Run [`02_graphrag_retrievers.ipynb`](02_graphrag_retrievers.ipynb)**

Build complete question-answering pipelines:

### VectorRetriever

Abstracts vector search into a simple API:

```python
retriever = VectorRetriever(
    driver=driver,
    index_name="chunkEmbeddings",
    embedder=embedder,
    return_properties=["text"]
)
results = retriever.search(query_text="What products?", top_k=5)
```

### GraphRAG Pipeline

Combines retrieval with LLM generation:

```python
rag = GraphRAG(retriever=retriever, llm=llm)
response = rag.search("What are the main products?")
print(response.answer)  # Grounded answer from your data
```

### VectorCypherRetriever: The Power of Graphs

Run custom Cypher after vector search to traverse relationships:

```python
# Include adjacent chunks for expanded context
query = """
MATCH (node)-[:FROM_DOCUMENT]->(doc:Document)
OPTIONAL MATCH (prev:Chunk)-[:NEXT_CHUNK]->(node)
OPTIONAL MATCH (node)-[:NEXT_CHUNK]->(next:Chunk)
RETURN COALESCE(prev.text + ' ', '') + node.text + COALESCE(' ' + next.text, '') AS expanded_context
"""

retriever = VectorCypherRetriever(
    driver=driver,
    index_name="chunkEmbeddings",
    retrieval_query=query,
    embedder=embedder
)
```

### What You'll Do
- Use `VectorRetriever` for semantic search
- Build a `GraphRAG` pipeline with Databricks LLM
- Create a `VectorCypherRetriever` with expanded context
- Compare standard vs. graph-enhanced retrieval

**Expected outcome:** Working GraphRAG pipelines demonstrating the power of graph-enhanced retrieval.

---

## Databricks Integration Details

This lab uses custom wrapper classes in `data_utils.py` that implement the neo4j-graphrag interfaces:

| Class | Interface | Databricks Service |
|-------|-----------|-------------------|
| `DatabricksEmbedder` | `Embedder` | [DatabricksEmbeddings](https://python.langchain.com/docs/integrations/text_embedding/databricks/) |
| `DatabricksLLM` | `LLMInterface` | [ChatDatabricks](https://python.langchain.com/docs/integrations/chat/databricks/) |

### Available Databricks Models

**Embedding Models:**
- `databricks-gte-large-en` - 1024 dimensions, 8192 token window
- `databricks-bge-large-en` - 1024 dimensions, 512 token window

**LLM Models:**
- `databricks-meta-llama-3-3-70b-instruct` - Meta Llama 3.3 70B
- `databricks-claude-sonnet-4-5` - Claude Sonnet 4.5
- `databricks-gpt-5-2` - GPT-5.2

---

## Additional Retriever Types (Reference)

The neo4j-graphrag library provides additional retrievers:

| Retriever | Use Case |
|-----------|----------|
| `HybridRetriever` | Combine vector + full-text search for technical terms |
| `Text2CypherRetriever` | Convert natural language to Cypher queries |
| `HybridCypherRetriever` | Hybrid search with custom Cypher traversal |

---

## Key Concepts Reference

| Concept | Description |
|---------|-------------|
| **Chunk** | A segment of text small enough for embedding and retrieval |
| **Embedding** | A vector capturing semantic meaning (1024 floats for GTE) |
| **Vector Index** | Neo4j index enabling fast similarity search |
| **Retriever** | Component that fetches relevant data from Neo4j |
| **Retrieval Query** | Custom Cypher appended after vector search |

## Troubleshooting

### Embedding dimension mismatch
Ensure your vector index dimensions match the embedder output:
- Databricks GTE: 1024 dimensions
- Databricks BGE: 1024 dimensions

### Neo4j connection issues
1. Verify `NEO4J_URI` starts with `neo4j+s://`
2. Check your Aura instance is running
3. Confirm credentials are correct

### Databricks authentication issues
1. Verify `DATABRICKS_HOST` is your workspace URL (e.g., `https://xxx.cloud.databricks.com`)
2. Ensure `DATABRICKS_TOKEN` is a valid personal access token
3. Check that Foundation Model APIs are enabled in your workspace

## Next Steps

**Congratulations!** You've completed the GraphRAG lab.

Continue to **[Lab 5 - AgentBricks Multi-Agent Systems](../Lab_5_AgentBricks)** to build intelligent multi-agent systems using Databricks AI/BI Genie and AgentBricks.

## Additional Resources

- [neo4j-graphrag Documentation](https://neo4j.com/docs/neo4j-graphrag-python/)
- [Databricks Foundation Model APIs](https://docs.databricks.com/aws/en/machine-learning/foundation-model-apis/)
- [Query Embedding Models on Databricks](https://docs.databricks.com/aws/en/machine-learning/model-serving/query-embedding-models)
- [ChatDatabricks - LangChain](https://python.langchain.com/docs/integrations/chat/databricks/)
- [DatabricksEmbeddings - LangChain](https://python.langchain.com/docs/integrations/text_embedding/databricks/)
- [Neo4j Vector Index Documentation](https://neo4j.com/docs/cypher-manual/current/indexes-for-vector-search/)
