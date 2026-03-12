# Plan: Update `02-power-of-graphrag-slides.md`

## Goal

Deck 02 picks up where Deck 01 ends. Deck 01 closes with "The Foundation is in Place" and a forward reference to Knowledge Graph Construction. Deck 02 should **not** teach how to build a knowledge graph. Instead, it acknowledges KG construction as a separate topic, states what the KG now contains (in the fraud ring domain), and moves directly into retrieval and agent architecture.

---

## Current State of Deck 02

The deck currently opens with LLM limitations, then covers GraphRAG concepts, the three data shapes, specialized agents, Genie, Neo4j MCP Agent, and the multi-agent supervisor. The content is solid but the opening doesn't connect to where Deck 01 left off. There's no bridge slide that says "we built the KG, here's what's in it."

---

## Proposed Slide Flow

### Opening: Bridge from Deck 01

**Replace** the current title slide and reframe the opening to connect to Deck 01's ending.

| # | Slide | Purpose |
|---|-------|---------|
| 1 | **Title: Beyond the Graph** | Keep current title. Subtitle: "Querying Across Both Platforms with AI" |
| 2 | **Where We Left Off** (NEW) | Quick recap: Delta Lake governs structured data, Spark Connector projected connection data into Neo4j, graph insights flow back to Gold tables. The data pipeline is complete. |
| 3 | **The Knowledge Graph Is Built** (NEW) | Bridge slide. States that KG construction (chunking AML policy docs, generating embeddings, extracting entities) is a separate topic covered elsewhere. The key point: **we now have a knowledge graph**. Show what it contains in the fraud domain. |
| 4 | **What the Knowledge Graph Contains** (NEW) | Concrete fraud-domain example of what KG construction added to the graph. Something like: AML policy document chunks as `(:Chunk)` nodes with vector embeddings, extracted entities like `(:Regulation)`, `(:Threshold)`, `(:Procedure)` linked to the chunks they came from, and connected to existing graph entities where applicable. The transaction graph from Deck 01 is now enriched with regulatory knowledge. |

### Core: LLM Limitations → Retrieval → Agents

| # | Slide | Change |
|---|-------|--------|
| 5 | **LLM Limitations and the Case for Agentic Systems** | Keep as-is. This motivates why we need RAG/agents. |
| 6 | **What GraphRAG Solves and Where Agents Take Over** | Keep as-is. Explains the retrieval pattern. |
| 7 | **Three Data Shapes, Two Platforms** | Keep as-is. Key framing slide. Consider updating "Covered In" column — Deck 01 covered structured and graph; this deck covers all three via agents. The "Unstructured" row currently says "Next presentation" but this deck should now own it since the KG is built. |

### Agents

| # | Slide | Change |
|---|-------|--------|
| 8 | **Why Specialized Agents, Not One General-Purpose Agent** | Keep as-is. |
| 9 | **What Is Databricks Genie?** | Keep as-is. |
| 10 | **Databricks Genie for Structured Data** | Keep as-is. |
| 11 | **What Is the Neo4j MCP Agent?** | Keep as-is. |
| 12 | **Neo4j MCP Agent for Graph Queries** | Keep as-is. |
| 13 | **Multi-Agent Supervisor** | Keep as-is. |
| 14 | **How the Supervisor Decides** | Keep as-is. |

### Closing

| # | Slide | Change |
|---|-------|--------|
| 15 | **Summary and What Comes Next** | Update to reflect the three-deck arc. Remove the forward reference to "unstructured document retrieval completes the three-source architecture" since this deck now acknowledges the KG exists. Reframe "what comes next" toward the hands-on labs. |

---

## New Slides to Write

### Slide: "Where We Left Off"

Purpose: 2-3 bullets recapping Deck 01's conclusion. No new concepts.

- **Delta Lake governs the data:** schema-enforced tables, ACID transactions, time travel
- **Connection data lives in the graph:** accounts, transfers, shared attributes as nodes and relationships
- **Graph insights flow back to Gold tables:** cycle detection, PageRank, community scores enrich the lakehouse

### Slide: "The Knowledge Graph Is Built"

Purpose: Acknowledge KG construction happened without teaching it. Frame it as a completed step.

- **Knowledge Graph Construction is its own discipline:** document chunking, embedding generation, entity extraction, graph enrichment
- **We won't cover the build process here.** That's a separate deep-dive
- **What matters now:** the graph is enriched with unstructured knowledge from AML policy documents
- **The fraud graph + regulatory knowledge = a queryable knowledge graph**

### Slide: "What the Knowledge Graph Contains"

Purpose: Show concretely what's in the KG now, in the fraud domain. Could use a small Cypher-style notation or a table.

Example content:

The transaction graph from the data pipeline now includes:

| What was added | Example |
|----------------|---------|
| **Document chunks** with embeddings | AML policy sections as `(:Chunk)` nodes with vector indexes |
| **Extracted entities** | `(:Regulation)`, `(:Threshold)`, `(:Procedure)` nodes |
| **Entity-to-chunk links** | `(:Regulation)-[:MENTIONED_IN]->(:Chunk)` |
| **Cross-domain connections** | `(:Procedure)-[:APPLIES_TO]->(:Account)` where entity resolution matched |

The graph now supports three query patterns: traversal (Cypher), aggregation (SQL via Genie), and semantic search (vector similarity over chunks).

---

## Slides to Update

### "Three Data Shapes, Two Platforms"

Update the "Covered In" column:

| Data Shape | Covered In (current) | Covered In (updated) |
|------------|---------------------|---------------------|
| Structured | This presentation | Deck 01 (data pipeline) + this deck (Genie agent) |
| Graph | This presentation | Deck 01 (Spark Connector) + this deck (Neo4j MCP agent) |
| Unstructured | Next presentation | KG built separately; queried via GraphRAG in this deck |

### "Summary and What Comes Next"

Rewrite the closing paragraph. Instead of "Next in this series: unstructured document retrieval..." close with a reference to the hands-on labs where participants build this themselves.

---

## What NOT to Change

- The agent slides (Genie, Neo4j MCP, Supervisor) are well-structured and match the IMPROVE.md conventions. Leave them alone.
- The LLM limitations slide is a strong opener after the bridge. Don't move it earlier.
- Don't add KG construction details. The whole point is to skip that and say "it's done."

---

## Style Notes (from IMPROVE.md)

- Fragments over sentences, 6x6 ceiling, bold-term-colon pattern
- Speaker notes in `<!-- -->` carry the narrative
- Arrow flows for pipelines, tables for comparisons
- No em-dashes, no prose paragraphs on slides
