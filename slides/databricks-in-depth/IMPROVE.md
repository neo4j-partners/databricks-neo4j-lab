# Improvement Plan: `01-intro-databricks-neo4j-slides.md`

## Why This Reframing Matters

The original slide 2 title — "Two Data Shapes, Each With a Purpose-Built Engine" — had a factual accuracy problem. Databricks officially handles **structured, semi-structured, and unstructured** data (multiple shapes on its own). Neo4j handles **connected/graph** data. That's three or more data shapes, not two. The "two" framing collapsed Databricks' multi-format capability into one bucket and misrepresented both platforms.

The new framing — **"Data Intelligence Meets Graph Intelligence"** — solves this by shifting from data shapes to **platform capabilities**. It uses each vendor's official branding and frames the pairing as complementary intelligence rather than competing storage formats. This document tracks every slide that needs updating to carry that framing consistently through the deck.

The GraphRAG deck (`02-power-of-graphrag-slides.md`, slide titled "Three Data Shapes, Two Platforms") already correctly identifies three shapes: Structured, Graph, and Unstructured. The in-depth deck should not contradict that framing.

---

## Official Platform Terminology

### Databricks: "The Data Intelligence Platform"

| Term | Source | URL |
|------|--------|-----|
| **"The data and AI company"** | About Us page H1 | https://www.databricks.com/company/about-us |
| **"Databricks Data Intelligence Platform"** | Product page | https://www.databricks.com/product/data-intelligence-platform |
| **"Data and AI for all"** | Platform tagline | https://www.databricks.com/product/data-intelligence-platform |
| **"structured and unstructured data"** | Data Lakehouse product page | https://www.databricks.com/product/data-lakehouse |
| **"structured, semi-structured and unstructured"** | Delta Lake / Data Lakes docs | https://www.databricks.com/discover/data-lakes |
| **"Unified. Open. Scalable."** | Lakehouse architecture pillars | https://www.databricks.com/product/data-lakehouse |
| **"a unified, open analytics platform"** | AWS docs intro | https://docs.databricks.com/aws/en/introduction/ |

**Key quote (Data Lakehouse page):** "One architecture for integration, storage, processing, governance, sharing, analytics and AI. One approach to how you work with structured and unstructured data."

**Key quote (About Us):** "Built on an open lakehouse architecture, the Data Intelligence Platform provides a unified foundation for all data and governance, combined with AI models tuned to an organization's unique characteristics."

### Neo4j: "The World's Leading Graph Intelligence Platform"

| Term | Source | URL |
|------|--------|-----|
| **"The World's Leading Graph Intelligence Platform"** | Homepage hero | https://neo4j.com/ |
| **"The #1 Platform for Connected Data"** | Ebook / legacy marketing | https://neo4j.com/wp-content/themes/neo4jweb/assets/images/Graph_Databases_for_Beginners.pdf |
| **"connected data"** | Primary marketing term | Used across neo4j.com |
| **"relationships are of equal importance to the data itself"** | Graph vs RDBMS docs | https://neo4j.com/docs/getting-started/appendix/graphdb-concepts/graphdb-vs-rdbms/ |
| **"relationships as first-class citizens"** | OGM reference docs | https://neo4j.com/docs/ogm-manual/current/reference/ |
| **"AI-ready data by design"** | Homepage secondary tagline | https://neo4j.com/ |
| **"Graphs + AI: Transform Your Data Into Knowledge"** | GraphSummit 2026 theme | https://neo4j.com/graphsummit/ |
| **"nodes and relationships"** | Getting Started docs | https://neo4j.com/docs/getting-started/whats-neo4j/ |

**Key quote (Why Graph Databases):** "Graph technology is specifically designed to store, uncover, and leverage relationships and context within data."

**Key quote (Graph vs RDBMS):** "JOINs are computed at query time by matching primary and foreign keys... These operations are compute-heavy and memory-intensive, and have an exponential cost."

### Neo4j + Databricks Together

| Term | Source | URL |
|------|--------|-----|
| **"Add Graph Intelligence to Your Databricks Lakehouse"** | Neo4j-Databricks webinar title | https://go.neo4j.com/WBR-AWR-251204-Neo4j-Databricks-Webinar-EMEA_Registration.html |
| **"Connected Data Lakehouse"** | NODES 2022 session | https://neo4j.com/videos/049-connected-data-lakehouse-neo4j-and-databricks-reference-data-architecture-nodes2022/ |
| **"turning governed data into a contextual knowledge asset"** | Webinar description | Same as webinar link above |

### Terminology Summary

| Platform | Uses frequently | Uses occasionally | Does NOT use |
|----------|----------------|-------------------|-------------|
| **Databricks** | Data Intelligence Platform, lakehouse, structured + unstructured | Data and AI company, unified platform | "Data platform" (generic), "data warehouse" alone |
| **Neo4j** | Connected data, graph intelligence, nodes and relationships | Highly connected datasets, knowledge graph | "Relationship data" (as a noun), "connection database" |

---

## Slide-by-Slide Analysis

### Slide 1: Title Slide (lines 30-32)

**DONE**

**Current:**
```
# Databricks + Neo4j
Delta Lake Stores the Records, Neo4j Reveals the Connections
```

**Issue:** "Stores the Records" reduces Databricks to a storage layer. Databricks officially positions itself as a "Data Intelligence Platform" — it governs, analyzes, and runs AI, not just stores. The subtitle doesn't set up the "Data Intelligence Meets Graph Intelligence" framing that immediately follows on slide 2.

**Answer:**
```
# Databricks + Neo4j
Data Intelligence Meets Graph Intelligence
```

---

### Slide 2: "Data Intelligence Meets Graph Intelligence" (lines 36-41)

Already updated. No changes needed.

---

### Slide 3: "What the Graph Looks Like" (lines 45-54)

No changes needed. This slide introduces Neo4j's graph model and is purely educational.

---

### Slide 4: "What Each Platform Answers" (lines 58-66)
**DONE**
**Current:**
```
| | Databricks | Neo4j |
|---|-----------|-------|
| **Data shape** | Rows and columns | Nodes and relationships |
```

**Issues:**
1. The row label **"Data shape"** echoes the old "Two Data Shapes" framing. The GraphRAG deck already acknowledges three shapes (Structured, Graph, Unstructured). Using "Data shape" here implies these are the only two.
2. **"Rows and columns"** describes only Databricks' structured data model. Databricks also handles semi-structured (JSON, Avro) and unstructured (images, PDFs, audio) data.

**Answer — Option A (rename the row):**
```
| **Query model** | SQL over tables | Cypher over nodes and relationships |
```
---

### Slide 5: "Mapping the Lakehouse to the Graph" (lines 70-74)
**DONE**
**Current:**
```
- **Tabular data:** most lakehouse data — aggregates, metrics, logs —
  stays in Delta tables where it belongs
```

**Issue:** "Tabular data" only covers one of Databricks' data types. The lakehouse also stores semi-structured and unstructured data. The slide should acknowledge that all lakehouse data stays unless it has connection patterns worth projecting into the graph.

**Proposed:**
```
- **Most lakehouse data stays in the lakehouse:** structured tables, semi-structured files,
  unstructured documents — governed by Unity Catalog, analyzed by Spark
- **Connection data** is the subset worth projecting into the graph: which accounts transfer
  to which, which entities share addresses, which components belong to which systems
- **Foreign keys to relationships:** connections buried in join tables and foreign keys
  become explicit, traversable graph relationships
```

---

### Slide 6: "Tables Become Graphs" (lines 78-89)

**HOLD**

**Current column headers:**
```
| Lakehouse (Databricks) | Knowledge Graph (Neo4j) |
```

**Issue:** "Knowledge Graph" is a specific Neo4j use case (entity extraction, document enrichment, semantic relationships). The fraud example on this slide is a **transaction graph / fraud graph**, not a knowledge graph. Neo4j's official term for the general case is just "graph" or "graph database."

**Proposed:**
```
| Lakehouse (Databricks) | Graph (Neo4j) |
```

If "Knowledge Graph" is intentional for audience framing, keep it — but note that the GraphRAG deck is the better place for that term, since it's specifically about knowledge graph construction.

---

### Slide 7: "Financial Fraud as a Working Example" (lines 93-99)

No changes needed. Well-written, focused on the use case.

---

### Slide 8: "Fraud Ring — Dual Database Architecture" (lines 103-105)

No changes needed. Image slide.

---

### Slide 9: "Extracting Connection Data from the Lakehouse" (lines 109-113)
**DONE**

**Current:**
```
- **Neo4j** receives the connection subset: only the data with dense
  relationships projects from the lakehouse into the graph
```

**Minor improvement:** "dense relationships" is vague. Neo4j's own term is "connected data."

**Proposed:**
```
- **Neo4j** receives the connected data: only the subset with relationship
  patterns worth traversing projects from the lakehouse into the graph
```

---

### Slides 10-13: Pipeline mechanics (lines 117-152)

No changes needed. These slides describe Spark Connector mechanics and are technically accurate.

---

### Slide 14: "Bidirectional Flow Through the Medallion Architecture" (lines 156-158)

**DONE**

**Current:**
```
The **Medallion Architecture** progressively refines raw data into
business-ready outputs. The bidirectional flow is where the two systems
**compound each other's value**.
```

**Issue:** "The two systems" is generic. This is the natural place to reinforce the DI/GI framing.

**Proposed:**
```
The **Medallion Architecture** progressively refines raw data into
business-ready outputs. The bidirectional flow is where data intelligence
and graph intelligence **compound each other's value**.
```

---

### Slide 15: "Graph Insights Flow Back to the Lakehouse" (lines 168-179)
**DONE**
**Current:**
```
Graph-derived metrics become columns in Delta tables, available across
the entire analytical estate.
```

**Minor improvement:** Could frame as graph intelligence enriching data intelligence.

**Proposed:**
```
Graph intelligence flows back as standard DataFrames. Graph-derived metrics
become columns in Delta tables — available for dashboards, ML features,
and downstream analytics across the entire data intelligence estate.
```

This is optional — the current version is clear and functional.

---

### Slide 16: "Other Ways to Connect Neo4j from Databricks" (lines 183-193)

No changes needed. The table is factual and concise.

---

### Slide 17: "What the Dual Architecture Enables" (lines 197-207)
**DONE**
**Current column headers:**
```
| Use Case | What Databricks Handles | What Neo4j Handles |
```

**Proposed (reinforce DI/GI):**
```
| Use Case | Data Intelligence (Databricks) | Graph Intelligence (Neo4j) |
```

This echoes the framing from slide 2 and reinforces the "two kinds of intelligence" narrative.

---

### Slide 18: Summary (lines 211-220)
**DONE**
**Current closing line:**
```
Together, you get the analytical power of the Lakehouse **and** the
relationship intelligence of the graph, connected through governed
pipelines, not siloed in separate platforms.
```

**Issue:** This is the closing statement of the deck. It should bookend with the "Data Intelligence Meets Graph Intelligence" framing from slide 2.

**Proposed:**
```
Together, data intelligence and graph intelligence compound each other —
connected through governed pipelines, not siloed in separate platforms.
```

---

## Cross-Deck Consistency
**HOLD**
### `01-databricks-neo4j-integration-slides.md` (overview deck)

**Lines 56-62** use the old framing:
```
**Databricks** excels at working with large volumes of structured and
unstructured data — aggregations, time-series analysis, and machine
learning over tables.
```

This should be updated to match the DI/GI framing and include "semi-structured":
```
**Databricks (Data Intelligence Platform)** governs and analyzes structured,
semi-structured, and unstructured data at scale — aggregations, time-series
analysis, and machine learning.

**Neo4j (Graph Intelligence Platform)** makes connections between entities
explicit and traversable — following chains of relationships, finding
patterns, and answering questions about structure.
```

**Line 32** subtitle "The Better Together Value" is generic. Consider aligning with the DI/GI framing.

**Lines 336-345** "What Each Platform Brings" table could use "Data Intelligence" / "Graph Intelligence" column headers.

### `02-power-of-graphrag-slides.md` (GraphRAG deck)

**Line 57** "Three Data Shapes, Two Platforms" — already correctly identifies three shapes. No changes needed. This is the authoritative framing.

**Line 166** uses "analytical power of the lakehouse and the relationship intelligence of the graph" — could align with DI/GI terminology for consistency, but this deck's focus is on agents and retrieval, so the impact is lower priority.

---

## Priority Order

| Priority | Change | Reason |
|----------|--------|--------|
| **High** | Title slide subtitle (slide 1) | First impression; sets the framing for everything |
| **High** | Summary closing line (slide 18) | Last impression; should bookend the framing |
| **High** | "What the Dual Architecture Enables" column headers (slide 17) | High-visibility comparison table |
| **Medium** | "What Each Platform Answers" row label (slide 4) | Avoid "Data shape" terminology |
| **Medium** | "Tables Become Graphs" column header (slide 6) | "Knowledge Graph" is inaccurate for fraud example |
| **Medium** | "Bidirectional Flow" intro text (slide 14) | Reinforce DI/GI at the architectural pivot point |
| **Medium** | "Mapping the Lakehouse to the Graph" first bullet (slide 5) | Acknowledge all three data types |
| **Low** | "Graph Insights Flow Back" intro text (slide 15) | Nice to have, current version works |
| **Low** | "Extracting Connection Data" wording (slide 9) | Minor terminology improvement |
| **Low** | Cross-deck: overview deck framing | Separate deck, lower urgency |
