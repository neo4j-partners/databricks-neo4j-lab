# Improvement Guide: `01-intro-databricks-neo4j-slides.md`

## Core Theme: Data Intelligence Meets Graph Intelligence

The deck frames the Databricks + Neo4j pairing as **complementary intelligence platforms**, not competing storage formats. Every slide should reinforce this: Databricks is the Data Intelligence Platform, Neo4j is the Graph Intelligence Platform. The combination compounds their value.

The GraphRAG deck (`02-power-of-graphrag-slides.md`, slide titled "Three Data Shapes, Two Platforms") correctly identifies three data shapes: Structured, Graph, and Unstructured. The in-depth deck should not contradict that framing.

---

## Deck Structure: Three Acts

The deck follows a three-act structure with transition slides between major sections.

### Act 1: The Two Platforms

Introduces both platforms, their query models, and why you need both.

| Slide | Purpose |
|-------|---------|
| Title: Databricks + Neo4j | DI meets GI framing |
| Data Intelligence Meets Graph Intelligence | One bullet per platform |
| Databricks: The Data Intelligence Platform | Platform capabilities |
| Neo4j: The Graph Intelligence Platform | Platform capabilities |
| Neo4j Graph Components | Nodes, relationships, properties notation |
| Different Data, Different Query Patterns | Table showing when to use each |
| Mapping the Lakehouse to the Graph | What stays, what moves |
| Tables Become Graphs | Comparison table: rows → nodes, FKs → relationships |

### `# Building the Intelligence Platform` (transition)

Subtitle: "From data intelligence through graph intelligence to agents that query both"

### Act 2: The Intelligence Platform + Working Example

Introduces the four-stage platform model, connection patterns, Medallion Architecture, and the fraud example.

| Slide | Purpose |
|-------|---------|
| The Intelligence Platform | Four stages with arrow flows |
| Connection Patterns by Platform Stage | One connector per stage |
| The Medallion Architecture | Bronze/Silver/Gold + bidirectional flow |
| Financial Fraud as a Working Example | The use case that demonstrates the pipeline |
| Fraud Ring — Dual Database Architecture | Architecture diagram |

### `# ELT: Lakehouse to Graph` (transition)

### Act 3: Building the Data Pipeline

Walks through the ELT stage in detail using the fraud example.

| Slide | Purpose |
|-------|---------|
| From Raw Data to Governed Delta Tables | Cloud storage → Delta tables |
| Extracting Connection Data from the Lakehouse | What moves, what stays |
| The Neo4j Spark Connector | Bidirectional bridge |
| Loading the Graph | Nodes first, relationships second, properties |
| Design Decision: Relationship Types vs. Properties | Type per connection vs. generic |
| Validation Through Spark Reads | Three checks |
| Graph Insights Flow Back to the Lakehouse | Graph algorithms → Gold Delta columns |
| The Foundation is in Place | Summary + forward reference to KG Construction |
| Summary | Bookends the DI meets GI framing |
| Appendices | SQL vs. Cypher decision framework, code examples, schema shift, fraud patterns |

---

## Four-Stage Intelligence Platform

The core organizing framework for the deck. Each stage builds a layer of intelligence.

| Stage | What It Does | Arrow Flow |
|-------|-------------|------------|
| **Data Pipeline** | Structured data from cloud storage through the lakehouse into the graph | cloud storage → lakehouse tables → data cleansing → graph nodes and relationships |
| **Knowledge Graph Construction** | Unstructured documents enriched into the graph | AML policy docs → chunking → embeddings + entity extraction → graph enrichment |
| **Data Analytics** | Graph insights combined with lakehouse data for consumption | graph insights + lakehouse data → dashboards, reports, ML features |
| **GraphRAG Retrieval/Agent** | AI-powered querying across both platforms | investigation queries → vector search + graph traversal + SQL → combined results |

### Connection Patterns by Stage

Each stage uses a different connector optimized for its workload.

| Stage | Primary Connector | Notes |
|-------|------------------|-------|
| **Data Pipeline** | Neo4j Spark Connector (batch writes) | Primary path for bulk loading structured data |
| **Knowledge Graph Construction** | Neo4j Python driver via neo4j-graphrag-python | SimpleKGPipeline handles chunking, entity extraction, embeddings; not a Spark operation |
| **Data Analytics** | Spark Connector (Graph Data Science reads) + Unity Catalog JDBC (governed SQL, BI tools) | Spark Connector for GDS algorithm results as DataFrames ("graph co-processor"); JDBC for analysts and BI tools |
| **GraphRAG Retrieval/Agent** | Neo4j MCP Server + Python driver | MCP exposes schema inspection + read-only Cypher as agent tools; Python driver powers VectorCypherRetriever |

---

## Databricks Data Flow Guidance

Databricks provided specific guidance on how the data flow should be described:

1. **S3/Azure Storage/GCS provides the data landing.** Cloud object storage is the raw landing zone, not a governed catalog.
2. **Databricks Jobs/Notebooks/Spark Declarative Pipelines process data into the Lakehouse.** These are the processing options (Spark Declarative Pipelines was formerly Delta Live Tables). Auto Loader can incrementally detect and process new files.
3. **Delta Lake enforces schema and rejects bad data at ingestion.** Column renaming happens here too (Customer_ID → account_id).
4. **Delta tables become the interchange format** for the Spark Connector.

This is **ELT, not ETL.** Data loads into cloud storage first, then gets transformed inside the lakehouse. The "T" happens after the "L."

---

## Neo4j Pipeline Terminology (neo4j-graphrag-python)

The `neo4j-graphrag-python` package is Neo4j's first-party Python library for building GenAI applications. It separates into three distinct user guides, each mapping to a platform stage. Slides should use these official terms to stay aligned with Neo4j's documentation.

| Platform Stage | Neo4j Official Term | Package Component | What It Does |
|---------------|--------------------|--------------------|-------------|
| **Data Pipeline** | No special name (Spark Connector) | `org.neo4j.spark.DataSource` | Batch reads/writes between DataFrames and Neo4j |
| **Knowledge Graph Construction** | **Knowledge Graph Builder** | `SimpleKGPipeline`, KG Builder pipeline | Chunks documents, generates embeddings, extracts entities/relationships, writes to Neo4j |
| **Data Analytics** | No special name (Spark Connector reads + JDBC) | `org.neo4j.spark.DataSource` (GDS), Neo4j JDBC driver | Graph Data Science results as DataFrames; governed SQL access via JDBC |
| **GraphRAG Retrieval** | **RAG** | `VectorCypherRetriever`, `GraphRAG` class | Combines vector search with graph traversal to retrieve context for LLM answers |
| **Agent Tooling** | **MCP** | Neo4j MCP Server | Exposes retrievers and Cypher execution as tools for AI agents |

**Key distinction:** "GraphRAG" in Neo4j's terminology refers specifically to the *retrieval* pattern (vector search + graph traversal augmenting LLM generation), not the construction/enrichment step. The construction pipeline (chunking, embedding, entity extraction) is officially "Knowledge Graph Construction" or "Knowledge Graph Builder."

**Knowledge Graph Builder pipeline stages:** data loader → text splitter → chunk embedder → schema builder → entity extractor → KG writer → entity resolver

**Sources:**
- [neo4j-graphrag-python docs](https://neo4j.com/docs/neo4j-graphrag-python/current/) — three user guides: RAG, Knowledge Graph Builder, Pipeline
- [Knowledge Graph Builder User Guide](https://neo4j.com/docs/neo4j-graphrag-python/current/user_guide_kg_builder.html)
- [Neo4j MCP Integration](https://neo4j.com/developer/genai-ecosystem/model-context-protocol-mcp/)
- [Neo4j Spark Connector Databricks Quickstart](https://neo4j.com/docs/spark/current/databricks/)
- [Neo4j Spark Connector GDS Integration](https://neo4j.com/docs/spark/current/gds/) — "graph co-processor" framing
- [Neo4j Spark Connector Reading](https://neo4j.com/docs/spark/current/reading/) — three read patterns: labels, relationship, query

---

## Official Platform Terminology

### Databricks: "The Data Intelligence Platform"

| Term | Source | URL |
|------|--------|-----|
| **"The data and AI company"** | About Us page H1 | https://www.databricks.com/company/about-us |
| **"Databricks Data Intelligence Platform"** | Product page | https://www.databricks.com/product/data-intelligence-platform |
| **"structured, semi-structured and unstructured"** | Delta Lake / Data Lakes docs | https://www.databricks.com/discover/data-lakes |
| **"Unified. Open. Scalable."** | Lakehouse architecture pillars | https://www.databricks.com/product/data-lakehouse |

### Neo4j: "The World's Leading Graph Intelligence Platform"

| Term | Source | URL |
|------|--------|-----|
| **"The World's Leading Graph Intelligence Platform"** | Homepage hero | https://neo4j.com/ |
| **"connected data"** | Primary marketing term | Used across neo4j.com |
| **"nodes and relationships"** | Getting Started docs | https://neo4j.com/docs/getting-started/whats-neo4j/ |
| **"AI-ready data by design"** | Homepage secondary tagline | https://neo4j.com/ |

### Neo4j + Databricks Together

| Term | Source | URL |
|------|--------|-----|
| **"Add Graph Intelligence to Your Databricks Lakehouse"** | Neo4j-Databricks webinar | https://go.neo4j.com/WBR-AWR-251204-Neo4j-Databricks-Webinar-EMEA_Registration.html |
| **"Connected Data Lakehouse"** | NODES 2022 session | https://neo4j.com/videos/049-connected-data-lakehouse-neo4j-and-databricks-reference-data-architecture-nodes2022/ |

### Terminology Summary

| Platform | Uses frequently | Does NOT use |
|----------|----------------|-------------|
| **Databricks** | Data Intelligence Platform, lakehouse, structured + unstructured | "Data platform" (generic), "data warehouse" alone |
| **Neo4j** | Connected data, graph intelligence, nodes and relationships | "Relationship data" (as a noun), "connection database" |

---

## Slide Style Conventions

These conventions were applied throughout this editing session. Future edits should follow the same patterns.

- **Fragments over sentences.** Bullets are key phrases (~6-8 words), not full sentences. Detail goes in speaker notes.
- **6x6 ceiling.** No more than 6 lines of content, roughly 6-8 words per line. Fewer is better.
- **Bold term: definition pattern.** Each bullet starts with a bolded key term followed by a colon and short explanation.
- **Arrow flows for pipelines.** Use `→` to show transformation chains (e.g., `cloud storage → lakehouse tables → graph nodes`).
- **No em-dashes (—).** Use colons, semicolons, commas, or split into separate bullets.
- **No prose paragraphs on slides.** If a point needs a paragraph, it belongs in speaker notes.
- **Speaker notes carry the narrative.** Use `<!-- ... -->` for what the presenter says aloud. Slides are visual anchors.
- **Tables for comparisons**, bullets for lists and transformation flows.
- **Platform names bolded on first mention** per slide.

---

## Remaining Work

### Summary slide needs updating

The current Summary references only Spark Connector and Medallion Architecture. It should reflect the four-stage intelligence platform model and the connection patterns.

### "Tables Become Graphs" column header

Still says "Knowledge Graph (Neo4j)." The fraud example is a transaction/fraud graph, not a knowledge graph. Consider changing to "Graph (Neo4j)."

### Cross-Deck Consistency

**HOLD**

`02-power-of-graphrag-slides.md` covers agents and retrieval in depth. The in-depth deck's "The Foundation is in Place" slide provides the forward reference to KG Construction and GraphRAG, which deck 02 picks up.

`01-databricks-neo4j-integration-slides.md` (overview deck, if it exists) should align with the DI/GI framing and four-stage model.
