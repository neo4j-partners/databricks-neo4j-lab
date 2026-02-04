# Lab 6 - Advanced RAG with Neo4j

This lab teaches advanced retrieval techniques for RAG applications using the **neo4j-graphrag** library with **Databricks Model Serving**. You'll learn to convert natural language to Cypher queries and automatically extract knowledge graphs from unstructured text.

## Before You Begin

> [!IMPORTANT]
> Complete these steps before running the notebooks.

**Prerequisites:**
- Lab 1 completed (Neo4j Aura database running)
- Lab 4 completed (GraphRAG fundamentals)
- Databricks workspace with Model Serving enabled

**Configure Credentials:**

Ensure `CONFIG.txt` in the root folder has your credentials:

```ini
# Neo4j Aura (from Lab 1)
NEO4J_URI=neo4j+s://xxxxxxxx.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password_here

# Databricks Model Serving
DATABRICKS_HOST=https://your-workspace.cloud.databricks.com
DATABRICKS_TOKEN=dapi-your-token-here
```

---

## What You'll Learn

This lab covers two advanced retrieval patterns:

| Pattern | Use Case |
|---------|----------|
| **Text2Cypher** | Convert natural language to Cypher queries for precise data retrieval |
| **Entity Extraction** | Build knowledge graphs automatically from unstructured text |

---

## Notebook 1: Text2Cypher Retriever

**Run [`01_text2cypher_retriever.ipynb`](01_text2cypher_retriever.ipynb)**

Convert natural language questions directly into Cypher queries.

### When to Use Text2Cypher

Text2Cypher excels at questions requiring precise graph queries:
- "What companies does BlackRock own?"
- "How many products does Apple offer?"
- "Which entities are connected to this risk factor?"

### How It Works

```
User Question → LLM + Schema → Generated Cypher → Neo4j → Results → LLM → Answer
```

```python
from neo4j_graphrag.retrievers import Text2CypherRetriever

retriever = Text2CypherRetriever(
    driver=driver,
    llm=llm,
    neo4j_schema=schema  # Graph structure guides Cypher generation
)

result = retriever.get_search_results("What companies are in the database?")
print(result.metadata["cypher"])  # See the generated query
```

### What You'll Do
- Extract graph schema automatically with `get_schema()`
- Create a `Text2CypherRetriever` with custom prompts
- Generate and execute Cypher from natural language
- Build a `GraphRAG` pipeline with Text2Cypher retrieval

---

## Notebook 2: Entity Extraction

**Run [`02_entity_extraction.ipynb`](02_entity_extraction.ipynb)**

Automatically extract structured knowledge graphs from unstructured text.

### Lexical vs Semantic Graphs

**Lexical Graph** (document structure):
```
(:Document) <-[:FROM_DOCUMENT]- (:Chunk) -[:NEXT_CHUNK]-> (:Chunk)
```

**Semantic Graph** (extracted entities):
```
(:Company)-[:OFFERS_PRODUCT]->(:Product)
         \-[:OFFERS_SERVICE]->(:Service)
```

Combining both enables powerful hybrid queries.

### How It Works

```python
from neo4j_graphrag.experimental.pipeline.kg_builder import SimpleKGPipeline

# Define what to extract
schema = {
    "node_types": [
        {"label": "Company", "description": "A company or organization"},
        {"label": "Product", "description": "A product offered by a company"},
    ],
    "relationship_types": [
        {"label": "OFFERS_PRODUCT", "description": "Company offers a product"},
    ],
    "patterns": [
        ("Company", "OFFERS_PRODUCT", "Product"),
    ],
}

# Create pipeline
pipeline = SimpleKGPipeline(
    llm=llm,
    driver=driver,
    embedder=embedder,
    schema=schema,
)

# Extract entities
await pipeline.run_async(text=document_text)
```

### What You'll Do
- Define entity and relationship schemas
- Use `SimpleKGPipeline` for automated extraction
- Explore the combined lexical + semantic graph
- Query chunks linked to extracted entities

---

## Text2Cypher vs Vector Retrieval

| Approach | Best For | Example |
|----------|----------|---------|
| **Vector Retrieval** | Semantic similarity, "find similar content" | "Tell me about Apple's products" |
| **Text2Cypher** | Precise queries, counts, aggregations | "How many products does Apple have?" |
| **Hybrid** | Combining both strengths | Use Text2Cypher for facts, vectors for context |

---

## Modern Cypher Syntax

The Text2Cypher prompt uses Neo4j 5+ compatible syntax:

| Deprecated | Modern Replacement |
|------------|-------------------|
| `id(node)` | `elementId(node)` |
| `size((pattern))` | `count{pattern}` |
| `exists((pattern))` | `EXISTS {MATCH pattern}` |

---

## Databricks Integration

This lab uses the same wrapper classes as Lab 4 (`data_utils.py`):

| Class | Purpose | Databricks Service |
|-------|---------|-------------------|
| `DatabricksEmbedder` | Generate embeddings | Foundation Model APIs (GTE) |
| `DatabricksLLM` | Text generation | Foundation Model APIs (Llama 3.3) |

---

## Troubleshooting

### Text2Cypher generates invalid queries
- Ensure your graph has data (run Lab 4 or 5 first)
- Check that the schema matches your actual graph structure
- Try simpler questions first

### Entity extraction is slow
- The LLM processes each chunk individually
- Reduce text size for testing
- Consider batching for large documents

### Neo4j connection issues
1. Verify `NEO4J_URI` starts with `neo4j+s://`
2. Check your Aura instance is running
3. Confirm credentials are correct

---

## Next Steps

Continue to **[Lab 10 - Aura Agents API](../Lab_10_Aura_Agents_API)** to learn how to programmatically invoke your Aura Agent via REST API with OAuth2 authentication.

## Additional Resources

- [Text2CypherRetriever Documentation](https://neo4j.com/docs/neo4j-graphrag-python/current/user_guide_rag.html#text2cypher-retriever)
- [SimpleKGPipeline Documentation](https://neo4j.com/docs/neo4j-graphrag-python/current/user_guide_kg_builder.html)
- [Databricks Foundation Model APIs](https://docs.databricks.com/aws/en/machine-learning/foundation-model-apis/)
- [Neo4j GraphRAG Python Library](https://neo4j.com/docs/neo4j-graphrag-python/)
