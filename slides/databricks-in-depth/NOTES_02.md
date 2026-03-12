# Activating the Intelligence Platform with GraphRAG — Speaker Notes

## Slide: Activating the Intelligence Platform with GraphRAG

Neo4j has published extensive material on GraphRAG patterns and best practices. What we wanted to cover here is a high-level overview of the core concepts. We will go in-depth on each stage in later presentations.

---

## Slide: Why Agents? LLM Limitations in the Enterprise

LLM gaps are the default in the enterprise — what we wanted to cover is how GraphRAG and agents fill them. Neo4j has detailed resources covering how knowledge graphs address each of these limitations. We will explore those patterns in depth in later sessions; today is the overview.

---

## Slide: From Documents to Searchable Chunks

Embeddings encode the semantic similarity of text, so chunks with related meaning end up close together in vector space. Documents split into chunks, linked back to source — chunks get embedded and indexed for semantic search. Neo4j's GraphRAG documentation covers chunking strategies, overlap tuning, and indexing in detail. What we wanted to cover is the mental model; we will walk through the specifics in a later presentation.

---

## Slide: From Chunks to Graph Structure

Entity extraction pulls structured nodes from chunks, entity resolution deduplicates, and cross-linking connects to the operational graph. For example, an AML policy chunk mentioning "enhanced due diligence for transfers above $10,000" yields a Regulation node, a Threshold node, and a Procedure node — each linked back to that chunk and cross-linked to the account nodes they apply to. Neo4j has rich material on entity extraction pipelines and resolution strategies that make this step production-ready. What we wanted to cover is the conceptual overview — we will dig into those techniques in a later session.

---

## Slide: What the Knowledge Graph Contains

Two layers: KG construction on top, Spark Connector data on the bottom, bridged by APPLIES_TO relationships. Neo4j's documentation on knowledge graph architecture covers schema design patterns for exactly this kind of layered graph. What we wanted to cover is how these layers connect; we will explore schema design choices in a later deep-dive.

---

## Slide: GraphRAG: Graph-Enriched Retrieval

Search finds the starting chunks, graph traversal follows entities and relationships outward, and the agent gets richer context than text search alone. Neo4j has published comprehensive guides on GraphRAG retrieval patterns including vector, hybrid, and graph-enriched search. What we wanted to cover is how graph traversal enriches retrieval; we will go in-depth on retriever configuration and tuning in a later presentation.

---

## Slide: From Retrieval to Agents

_Section title slide — no speaker notes._

---

## Slide: Beyond GraphRAG: Reaching the Lakehouse

GraphRAG covers graph data, but the full transaction ledger stays in Delta Lake. Questions that need SQL aggregations require agents.

---

## Slide: Specialized Agents for Different Data Structures

One agent per platform. Focused context produces reliable queries. A supervisor coordinates them.

---

## Slide: Databricks Genie: Natural Language to SQL

Compound AI system, not a single LLM. Unity Catalog metadata makes it smart. Genie Spaces let domain experts configure tables, instructions, and example queries. Read-only.

---

## Slide: Neo4j Graph Agent: Natural Language to Cypher

Cypher specialist for connected data. Schema-constrained so it writes precise traversals. Read-only.

---

## Slide: How the Graph Agent Reaches Neo4j

Two paths: MCP tools for schema and Cypher execution, Python driver for GraphRAG retrievers. Schema discovery plus system prompt give the agent structure and domain knowledge.

---

## Slide: Neo4j MCP Tools

get-schema for structure discovery, read-cypher for query execution, list-gds-procedures for graph analytics. Write-cypher hidden entirely in read-only mode.

---

## Slide: Multi-Agent Supervisor: Routing to the Right Platform

Reads the question, routes to the right specialist. Decomposes multi-platform questions and synthesizes a single answer.

---

## Slide: The Intelligence Platform Is Active

Deck 01 built the data foundation. This deck added knowledge graph construction, GraphRAG retrieval, and coordinated agents. The labs let you build it yourself.
