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

# Beyond the Graph

Querying Across Both Platforms with AI

---

## LLM Limitations and the Case for Multi-Agent Systems

- **LLMs hallucinate:** plausible answers with no grounding in your data
- **LLMs lack domain context:** no knowledge of your schema, rules, or terminology
- **LLMs cannot access private data:** enterprise knowledge behind firewalls is invisible
- **LLMs are non-deterministic:** same question, different answers each time

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

## Document Chunking

- **Documents are too large to search:** a 50-page AML policy manual is not a useful result
- **Split into fixed-size chunks** with overlap to preserve context at boundaries
- **Each chunk becomes a graph node** linked to its source document
- **Chunk size is a tradeoff:** too small loses context, too large loses precision

<!--
When a user asks "What AML procedures apply to circular transfers?"
the system doesn't search whole documents. It searches chunks and
returns the most relevant sections.

Documents get split into fixed-size pieces, typically 500 to 1000
characters, with overlap so context isn't lost at the boundaries.
Each chunk becomes a Chunk node in the graph, linked back to its
source Document node. Chunks also link to each other in sequence,
so you can walk forward and backward through the original document
from any search result.

Chunk size is a real tradeoff. Too small and each chunk lacks
enough context to be useful on its own. Too large and search
results are imprecise, returning pages of text when you only
needed a paragraph.
-->

---

## Embeddings: Searching by Meaning

- **Keyword search fails on synonyms:** "circular transfer" won't match "round-trip fund movement"
- **Embedding models** convert text to vectors; similar meaning = close in vector space
- **Each chunk gets a vector** stored on its node, indexed for similarity search
- **Semantic search:** find chunks closest in meaning to the question, not matching keywords

<!--
Keyword search breaks down when the question and the answer use
different words. "Circular transfer pattern" and "round-trip fund
movement" describe the same thing, but keyword search won't
connect them.

An embedding model converts each chunk's text into a vector, a
list of numbers representing its meaning. Chunks with similar
meaning end up close together in this vector space, regardless
of the exact words used. The same model converts the user's
question into the same space, so similarity search finds the
closest chunks by meaning.

Each chunk node gets its embedding vector stored as a property,
and a vector index enables fast similarity search across all
chunks. This is the "vector search" half of GraphRAG. It's how
the system finds relevant content without requiring exact keyword
matches.
-->

---

## Entity Extraction: Structure from Text

- **Chunks are unstructured text.** The graph needs structured nodes to traverse
- **An LLM reads each chunk** and extracts entities: regulations, thresholds, procedures
- **Entities become graph nodes** linked to source chunks and cross-linked to existing graph
- **Entity resolution** deduplicates: same regulation in 5 chunks = 1 node, 5 links

<!--
Chunks give you searchable text, but the graph needs structured
nodes to traverse. Entity extraction bridges that gap.

An LLM reads each chunk and identifies structured entities:
regulations, monetary thresholds, compliance procedures. These
become graph nodes with typed properties, linked back to the
chunks they were extracted from. That link is provenance: you
can always trace an entity back to the text it came from.

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

## What Is the Neo4j MCP Agent?

- **Graph-specialized agent:** purpose-built for Cypher, just as Genie is for SQL
- **Schema awareness:** inspects every node label, relationship type, and property key
- **Structure, not guessing:** knows `Account` connects through `TRANSFERRED_TO`, writes precise traversals
- **Domain instructions:** system prompt teaches traversal patterns and graph-specific terminology
- **Cypher expertise:** generates Cypher the way Genie generates SQL

<!--
Just as Genie is purpose-built for SQL, this agent is purpose-built
for Cypher, the query language for graph databases. It inspects the
graph schema to learn every node label, relationship type, and
property key before generating a single query.

Because the agent knows that Account nodes connect through
TRANSFERRED_TO relationships, it writes precise traversals instead
of hallucinating table names or join conditions. A system prompt
teaches it graph-specific terminology, traversal patterns, and what
questions the graph is designed to answer.
-->

---

## Neo4j MCP Agent for Graph Queries

- **Schema-first querying:** calls `get-neo4j-schema`, generates Cypher against verified structure
- **Connect to your graph:** `Account` nodes and `TRANSFERRED_TO` relationships
- **Add domain context:** flagged accounts, fraud ring structure, appropriate traversal depth
- **Users ask in English:** "Which accounts are within three hops?" becomes a Cypher traversal
- **Read-only by default:** only `read-neo4j-cypher`, never modifies production data

<!--
The agent calls get-neo4j-schema to discover the exact node types
and relationship types available, then generates Cypher against
verified structure instead of guessing. You connect it to the fraud
knowledge graph with Account nodes and TRANSFERRED_TO relationships.

System prompt instructions teach the agent what a flagged account
is, how fraud rings are structured, and what traversal depth is
appropriate. Users ask in English: "Which accounts are within three
hops of the flagged account?" becomes a Cypher traversal, executes
against Neo4j, and returns the connected accounts.

Agents in this workshop use only read-neo4j-cypher, so they can
never modify production graph data.
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

## Supervisor Routing in Action

**Single-source questions** go to one agent:
- **"Total transfer volume for account-1234?"** → Genie (SQL aggregation)
- **"Which accounts share a device with account-1234?"** → Neo4j (graph traversal)

**Multi-source questions** get decomposed:
- **"Find the fraud ring and compute total transfer volume for its members"**
  1. Neo4j agent detects the ring via cycle traversal
  2. Genie agent computes transfer totals for the identified accounts
  3. Supervisor synthesizes a single answer

<!--
Single-source questions are straightforward. "Total transfer
volume" signals SQL aggregation, so it routes to Genie. "Which
accounts share a device" signals graph traversal, so it routes
to Neo4j.

Multi-source questions are where the supervisor earns its keep.
"Find the fraud ring and compute total transfer volume" requires
both platforms. The supervisor decomposes it: Neo4j detects the
ring via cycle traversal, Genie computes transfer totals for the
identified accounts, and the supervisor synthesizes a single
answer from both results.
-->

---

## How the Supervisor Decides

- **Agent descriptions:** sub-agents register capabilities, supervisor matches against them
- **Guidelines:** domain experts add routing rules ("path questions go to the graph agent")
- **Aggregation signals:** "total," "average," "count" route to Genie
- **Relationship signals:** "connected to," "within N hops" route to Neo4j
- **Decomposition:** both signal types present, supervisor splits into sub-tasks
- **Iterative refinement:** wrong routing, add a guideline, correction applies immediately

<!--
The supervisor decides routing through several mechanisms. Each
sub-agent registers a description of what it can do, and the
supervisor matches incoming questions against those descriptions.

Domain experts add guidelines like "questions about paths belong
to the graph agent." Keyword signals help too: "total," "average,"
or "count" imply SQL aggregation and route to Genie. "Connected
to," "within N hops," or "shared device" imply traversal and
route to Neo4j.

When both signal types appear in a single question, the supervisor
decomposes it into sub-tasks for each agent. If routing is wrong,
experts add a guideline and the correction applies immediately
without retraining.
-->

---

## What Each Platform Brings

**Databricks + Neo4j** connects data intelligence with graph intelligence through governed pipelines and specialized agents:

- **Data stays governed:** Delta Lake is the source of truth, Spark Connector projects connections into Neo4j
- **Each data shape gets a specialist:** Genie for SQL, Neo4j MCP for Cypher, GraphRAG for semantic search
- **A supervisor coordinates:** questions route automatically, multi-source questions decompose across both
- **Intelligence compounds:** graph insights enrich the lakehouse, lakehouse data feeds the graph, agents query both

**Next:** the hands-on labs. Load data via the Spark Connector, query the graph, configure Genie Spaces, and wire up the multi-agent supervisor yourself.

<!--
This is the synthesis, not a restatement. The key insight is that
data intelligence and graph intelligence compound each other's
value when connected through governed pipelines.

Delta Lake stays the source of truth. The Spark Connector projects
connection data into Neo4j. Each data shape gets a specialist agent
that masters the right query language for its structure. A supervisor
coordinates them so users ask questions in English and get answers
from whichever platform can answer them.

The hands-on labs let you build this yourself: load data via the
Spark Connector, query the graph with Cypher, configure Genie Spaces
with domain vocabulary, and wire up the multi-agent supervisor.
-->
