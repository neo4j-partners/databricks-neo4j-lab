---
marp: true
theme: default
paginate: true
---

<style>
section {
  --marp-auto-scaling-code: false;
}

li {
  opacity: 1 !important;
  animation: none !important;
  visibility: visible !important;
}

/* Disable all fragment animations */
.marp-fragment {
  opacity: 1 !important;
  visibility: visible !important;
}

ul > li,
ol > li {
  opacity: 1 !important;
}
</style>

# Activating the Intelligence Platform

Knowledge graphs, retrieval, and agents across both platforms

---

## Why Agents? LLM Limitations in the Enterprise

- **Hallucination:** plausible answers with no grounding in your data
- **No domain context:** no knowledge of your schema, rules, or terminology
- **No access to private data:** enterprise knowledge behind firewalls is invisible
- **Non-deterministic:** same question, different answers each time

<!--
Each of these is a real problem for enterprise use. Hallucination
means the model generates confident answers that aren't grounded
in your actual data. It doesn't know your schema, your business
rules, or your domain terminology. Enterprise data behind firewalls
is completely invisible to it. And even with perfect context, the
same question can produce different answers each time.

RAG and GraphRAG reduce these problems but don't remove them. The
path forward is agentic systems with specialized, tightly scoped
context: each agent operates against a known schema, a known query
language, and clear domain instructions. That's what we'll build
in this deck.
-->

---

## The Knowledge Graph Is Built

- **Data pipeline complete:** Spark Connector projected Delta tables into graph nodes and relationships
- **KG construction complete:** AML policy docs chunked, embedded, entity-extracted into the graph
- **Building the KG is its own topic:** we focus on what it enables, not how it was built
- **The graph now holds** structured connections and regulatory knowledge

<!--
The previous deck built the data pipeline: governed Delta tables
projected into Neo4j via the Spark Connector. That gave us account
nodes, transfer relationships, and shared-attribute connections.

Knowledge Graph Construction is the next stage in the intelligence
platform. It takes unstructured AML policy documents, chunks them,
generates embeddings, extracts entities, and writes everything into
the graph. We're not covering the build process here. That's its
own deep-dive.

What matters for this deck: the graph is enriched with both
structured transaction data and regulatory knowledge. That's the
foundation we'll query with agents.
-->

---

## From Documents to Searchable Chunks

- **Documents split into Chunk nodes** with raw text, linked to source via `FROM_DOCUMENT`
- **Chunks link to each other** via `NEXT_CHUNK` to preserve document order
- **Embedding models** convert chunk text into vectors that capture semantic meaning
- **"Circular transfer" matches "round-trip fund movement"** — same meaning, different words
- **Vector index** searches by semantic similarity, not keyword matching

<!--
The first half of Knowledge Graph Construction turns unstructured
documents into searchable graph nodes. Documents get split into
fixed-size pieces, typically 500 to 1000 characters, with overlap
so context isn't lost at boundaries. Each chunk becomes a Chunk
node storing the raw text as a property, linked back to its
Document node via FROM_DOCUMENT and to adjacent chunks via
NEXT_CHUNK.

An embedding model converts each chunk's text into a vector. Chunks
with similar meaning end up close together in vector space,
regardless of the exact words used. A vector index enables fast
similarity search: "circular transfer pattern" and "round-trip
fund movement" match by meaning even though they share no keywords.

At this point the graph has searchable text but no structure to
traverse. The next step adds that.
-->

---

## From Chunks to Graph Structure

- **An LLM reads each chunk** and extracts entities: regulations, thresholds, procedures
- **Entities become graph nodes** linked to source chunks via `FROM_CHUNK`
- **Entity resolution** deduplicates: same regulation in 5 chunks = 1 node, 5 links
- **Cross-linking** connects extracted entities to the existing operational graph

<!--
Chunks give you searchable text, but the graph needs structured
nodes to traverse. Entity extraction bridges that gap.

An LLM reads each chunk and identifies structured entities:
regulations, monetary thresholds, compliance procedures. These
become graph nodes with typed properties, linked back to the
chunks they were extracted from via FROM_CHUNK. That link is
provenance: you can always trace an entity back to the text it
came from.

Entity resolution handles deduplication. The same regulation
mentioned across five different chunks becomes one node with
five links, not five separate nodes. Cross-linking connects
extracted entities to the existing operational graph, so a
procedure that applies to a specific account type links directly
to those account nodes.

This is the "graph" half of GraphRAG. After vector search finds
relevant chunks, graph traversal follows the entities and
relationships surrounding those chunks to gather richer context.
Without entity extraction, there's nothing to traverse.
-->

---

## What the Knowledge Graph Contains

```
  (:Document) ---> (:Chunk {embedding}) ---> [Vector Index]
                          |
                    entity extraction
                          |
                          v
            (:Regulation)   (:Threshold)   (:Procedure)
                                 |
                           [:APPLIES_TO]
                                 v
            (:Account) --[:TRANSFERRED_TO]--> (:Account)
```

<!--
This diagram shows the two layers of the knowledge graph and how
they connect. Documents become chunks with embeddings that feed a
vector index for semantic search. Entity extraction pulls structured
nodes from those chunks. Cross-linking connects extracted entities
to the operational transaction graph built by the data pipeline.

The top half is what Knowledge Graph Construction adds. The bottom
is what the Spark Connector built in the data pipeline. The
APPLIES_TO relationship bridges them.
-->

---

## GraphRAG: Graph-Enriched Retrieval

```
  User Question
       |
       v
  Vector / Fulltext Search ---> matching (:Chunk) nodes
       |
       v
  Graph Traversal ---> entities, relationships, connected chunks
       |
       v
  Graph-Enriched Context ---> agent / LLM
```

- **Search finds the starting points:** chunks closest in meaning to the question
- **Graph traversal enriches:** follows entities and relationships from those chunks
- **Agents receive richer context** than text search alone

<!--
This is the core GraphRAG retrieval pattern. Vector or fulltext
search finds the chunks most relevant to the user's question.
That's standard RAG. What GraphRAG adds is the second step:
graph traversal from those chunks through the entities and
relationships surrounding them.

When search returns a chunk about "enhanced due diligence for
high-value transfers," graph traversal follows the extracted
entities to find the specific regulations, thresholds, and
procedures connected to that chunk, plus any operational graph
nodes those entities link to. The agent receives all of this
as context, not just the chunk text.

This is why the entity extraction step matters. Without extracted
entities linked to chunks and cross-linked to the operational
graph, there's nothing for the graph traversal to follow. You'd
just have text search.
-->

---

## Beyond GraphRAG: Reaching the Lakehouse

- **GraphRAG reaches graph data:** grounded answers with entities and relationships from the knowledge graph
- **The lakehouse holds the rest:** transaction volumes, aggregations, trends in Delta tables
- **GraphRAG can't compute SQL:** "total transfer volume for this fraud ring?" lives in the lakehouse
- **To span both platforms,** we need more than retrieval

<!--
GraphRAG grounds LLM answers in retrieved content and enriches
them with graph context: entities, relationships, connected
chunks. This is a real improvement over plain text search.

But GraphRAG can only reach data in the graph. The fraud graph
holds account connections as TRANSFERRED_TO relationships, but
the full transaction ledger stays in Delta Lake. GraphRAG cannot
answer "what is the total transfer volume for accounts in this
fraud ring?" because that requires a SQL aggregation over rows
that never entered the graph. To answer questions that span both
platforms, we need agents.
-->

---

## GraphRAG + Agents

- **Databricks Lakehouse:** structured data, queried with SQL by a dedicated agent
- **Neo4j:** graph data and document chunks, queried with Cypher by a dedicated agent
- **Each platform has its own query language,** schema, and structure
- **One agent per platform.** A supervisor to coordinate them.

<!--
GraphRAG handles graph retrieval. But the lakehouse needs its own
agent that speaks SQL, and the graph needs an agent that speaks
Cypher. Each platform has its own query language, schema
conventions, and structure. A single agent spread across both
can't maintain the focused context needed to generate reliable
queries against either.

When an agent only needs to reason about Delta tables, the schema
becomes a constraint that guides generation rather than a
suggestion it might ignore. Same for graph relationships. Focused
agents produce reliable queries by mastering one platform each.

The architecture: one agent per platform, a supervisor to
coordinate them. That's what we build next.
-->

---

## Databricks Genie: Natural Language to SQL

- **Compound AI system:** turns natural language into governed SQL
- **Purpose-built for tabular data:** optimized for SQL generation against rows and columns
- **Lakehouse and federated sources:** queries any data registered in Unity Catalog
- **Users ask in English:** "Total transfer volume for account-1234?" becomes SQL and executes
- **Read-only execution:** generated queries can never modify your data

<!--
Genie is not a single LLM. It's a compound AI system with multiple
interacting components specialized for natural language to SQL.

Genie queries any data registered in Unity Catalog: managed tables,
external tables, foreign tables from federated sources like
Snowflake, PostgreSQL, and BigQuery, plus views and materialized
views. Unity Catalog provides the metadata that makes Genie smart:
table names, column descriptions, primary/foreign key relationships.
Column-level context is intelligently filtered so only relevant
metadata reaches the model.

Domain experts configure Genie Spaces: curated sets of tables with
JOIN definitions, up to 100 plain-text instructions teaching domain
terminology and business rules, and example SQL queries that Genie
selects from when they match the user's question. When a response
matches a parameterized example query exactly, Genie marks it as
"Trusted" so users know the answer came from a verified path.

Every generated query is read-only, so Genie can never modify
your data.
-->

---

## Neo4j Graph Agent: Natural Language to Cypher

- **Graph-specialized agent:** turns natural language into Cypher traversals
- **Purpose-built for connected data:** optimized for paths, patterns, and multi-hop relationships
- **Schema-aware:** inspects every node label, relationship type, and property key before querying
- **Users ask in English:** "Which accounts are within three hops?" becomes a Cypher traversal
- **Read-only by default:** generated queries can never modify production data

<!--
Just as Genie is purpose-built for SQL against tabular data, this
agent is purpose-built for Cypher against connected data. It
understands graph patterns: paths, multi-hop traversals, cycle
detection, shared-attribute matching.

Because the agent knows that Account nodes connect through
TRANSFERRED_TO relationships, it writes precise traversals instead
of hallucinating table names or join conditions. The graph's
schema becomes a constraint that guides generation, not a
suggestion to ignore.

Every generated query is read-only, so the agent can never modify
production graph data.
-->

---

## Accessing the Knowledge Graph

- **MCP (Model Context Protocol):** exposes `get-schema`, `read-cypher`, and `list-gds-procedures` as agent tools
- **Python driver:** powers GraphRAG retrievers (VectorCypherRetriever) for semantic search
- **Agent context:** schema discovery + system prompt give the agent graph structure and domain knowledge

<!--
The agent accesses Neo4j through two paths. MCP exposes graph
intelligence as standard agent tools: get-schema for structure
discovery, read-cypher for query execution, and list-gds-procedures
for graph analytics when GDS is installed.

The Python driver provides a separate path for GraphRAG retrievers
like VectorCypherRetriever, which combines vector similarity search
with graph traversal in a single query.

Agent context comes from two sources working together. Schema
discovery via get-schema auto-inspects the graph structure using
APOC introspection so the agent knows every node label, relationship
type, and property key. The system prompt adds domain knowledge:
what a flagged account is, how fraud rings are structured, what
traversal depth is appropriate. Together they ensure the agent
queries against verified schema with domain-appropriate patterns.
-->

---

## Neo4j MCP Tools

- **`get-schema`:** APOC introspection, auto-discovers structure, token-efficient for LLMs
- **`read-cypher`:** read-only Cypher with parameterized inputs
- **`list-gds-procedures`:** discovers graph analytics (PageRank, community detection) when GDS is installed
- **Read-only mode:** `write-cypher` hidden entirely, agents can never modify production data

<!--
get-schema introspects the live database using APOC, sampling
nodes and relationships to discover the full graph structure.
The result is post-processed into a token-efficient JSON
representation optimized for LLM consumption: property types
without verbose metadata, relationships reduced to direction
and target labels, nulls and empties stripped.

read-cypher executes read-only Cypher statements with optional
parameterized inputs. In read-only mode, write-cypher is hidden
entirely so agents can never modify production data.

list-gds-procedures discovers available Graph Data Science
algorithms: centrality, community detection, similarity, path
finding. Only exposed when the GDS library is installed. This
lets agents run PageRank, community detection, and other
analytics directly.
-->

---

## Multi-Agent Supervisor: Routing to the Right Platform

A **supervisor agent** sits above both specialists and routes questions based on their nature.

```
                    User Question
                         |
                         v
                +--- Supervisor ---+
                |                  |
                v                  v
        Genie Space Agent    Neo4j MCP Agent
        (Lakehouse / SQL)    (Graph / Cypher)
```

<!--
The supervisor doesn't answer questions itself. It reads the
question, determines which data shape it targets, and routes to
the right specialist agent. If the question spans multiple data
shapes, it decomposes the question and sends sub-tasks to each
agent, then synthesizes a single answer.
-->

---

## The Intelligence Stack Is Complete

- **Deck 01 built the data layer:** governed Delta tables ↔ graph nodes and relationships via the Spark Connector
- **This deck built the intelligence layer:** Knowledge Graph Construction enriched the graph with unstructured knowledge; GraphRAG retrieves it; specialized agents query both platforms
- **A supervisor coordinates:** questions route to the right platform automatically; multi-source questions decompose across both
- **Next:** the hands-on labs — load data, build the graph, configure Genie Spaces, and wire up the multi-agent supervisor yourself

<!--
The first deck built the data foundation: raw data landed in
Bronze, got cleaned and governed in Silver, and the Spark
Connector projected connection data into Neo4j. Graph algorithm
results flowed back as columns in Gold tables. That gave us the
pipeline.

This deck built the intelligence layer on top of that pipeline.
Knowledge Graph Construction took unstructured AML policy
documents and turned them into structured graph nodes: chunks
with embeddings, extracted entities cross-linked to the
operational graph. GraphRAG combines vector search with graph
traversal so agents receive richer context than text search
alone.

Specialized agents master one platform each: Genie speaks SQL
against the lakehouse, the Neo4j MCP agent speaks Cypher against
the graph. A supervisor routes questions to the right specialist
and decomposes multi-source questions across both.

The full stack is now in place: governed data, enriched knowledge
graph, semantic retrieval, and coordinated agents. The hands-on
labs let you build this yourself.
-->
