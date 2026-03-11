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

## LLM Limitations and the Case for Agentic Systems

- **LLMs hallucinate.** They generate plausible answers with no grounding in your actual data
- **LLMs lack domain context.** They don't know your schema, your business rules, or your terminology
- **LLMs cannot access private data.** Enterprise knowledge behind firewalls is invisible to them
- **LLMs are non-deterministic.** The same question can produce different answers each time, and no amount of context eliminates that entirely

RAG and GraphRAG reduce these problems but don't remove them. The path forward is **agentic systems with specialized, tightly scoped context** where each agent operates against a known schema, a known query language, and clear domain instructions.

---

## What GraphRAG Solves and Where Agents Take Over

- **RAG** grounds LLM answers in retrieved content, reducing hallucinations and giving the model access to private data
- **GraphRAG** adds graph structure to retrieval: the answer includes not just relevant text but the entities and relationships surrounding it
- **Both improve accuracy.** Neither can reach everything
- **The fraud graph holds account connections** as `TRANSFERRED_TO` relationships, but the full transaction ledger stays in **Delta Lake**
- **GraphRAG cannot answer** "what is the total transfer volume for accounts in this fraud ring?" because that requires a SQL aggregation over rows that never entered the graph

---

## Three Data Shapes, Two Platforms

| Data Shape | Where It Lives | What It Answers | Covered In |
|---|---|---|---|
| **Structured** (SQL-queryable tables) | Databricks Lakehouse | "How much?" "How often?" Aggregations, trends, distributions | This presentation |
| **Graph** (nodes and relationships) | Neo4j | "How is this connected?" Traversals, patterns, paths | This presentation |
| **Unstructured** (documents, manuals) | Depends on retrieval architecture | "What does the manual say?" Procedures, policies, context | Next presentation |

A fraud ring investigation needs the graph to identify the ring, the lakehouse to compute the financials, and eventually the documents to find the relevant compliance procedures.

---

## Why Specialized Agents, Not One General-Purpose Agent

- **Each data shape has its own query language,** schema conventions, and structure
- **A single agent spread across SQL, Cypher, and vector search** lacks the focused context to generate reliable queries against any of them
- **The schema becomes a constraint, not a suggestion.** When an agent only needs to reason about Delta tables or only about graph relationships, it leverages structure rather than guessing across structures

One agent per data shape. A supervisor to coordinate them.

---

## What Is Databricks Genie?

- **Compound AI system:** not a single LLM, but multiple interacting components specialized for turning natural language into SQL
- **Unity Catalog awareness:** Genie reads table names, descriptions, and primary/foreign key relationships to understand your data before generating a query
- **Column-level context:** column names and descriptions are intelligently filtered so only relevant metadata reaches the model
- **Example SQL queries:** domain experts provide sample queries that Genie selects from when they match the user's question
- **Plain-text instructions:** natural language guidelines that teach Genie domain terminology, business rules, and edge cases
- **Read-only execution:** every generated query is read-only, so Genie can never modify your data

---

## Databricks Genie for Structured Data

- **Genie Spaces:** a curated environment where domain experts select tables, define JOIN relationships, and add up to 100 instructions per space
- **Connect to your tables:** the financial transaction tables from the fraud example
- **Add domain knowledge:** instructions that teach Genie what "suspicious transfer" means, what normal transaction volumes look like, and what a flagged account is
- **Users ask in English:** "What is the total transfer volume for account-1234 in the last 90 days?" becomes SQL, executes against Delta Lake, and returns the answer
- **Trusted Assets:** when a response matches a parameterized example query or SQL function exactly, Genie marks it as "Trusted" so users know the answer came from a verified path

---

## What Is the Neo4j MCP Agent?

- **Graph-specialized agent:** just as Genie is purpose-built for SQL, this agent is purpose-built for Cypher, the query language for graph databases
- **Schema awareness:** the agent inspects the graph schema to learn every node label, relationship type, and property key before generating a single query
- **Structure, not guessing:** because the agent knows that `Account` nodes connect through `TRANSFERRED_TO` relationships, it writes precise traversals instead of hallucinating table names or join conditions
- **Domain instructions:** a system prompt teaches the agent graph-specific terminology, traversal patterns, and what questions the graph is designed to answer
- **Cypher expertise:** the agent generates Cypher the same way Genie generates SQL, each agent mastering the query language that fits its data shape

---

## Neo4j MCP Agent for Graph Queries

- **Schema-first querying:** the agent calls `get-neo4j-schema` to discover the exact node types and relationship types available, then generates Cypher against verified structure instead of guessing
- **Connect to your graph:** the fraud knowledge graph with `Account` nodes and `TRANSFERRED_TO` relationships
- **Add domain context:** system prompt instructions that teach the agent what a flagged account is, how fraud rings are structured, and what traversal depth is appropriate
- **Users ask in English:** "Which accounts are within three hops of the flagged account?" becomes a Cypher traversal, executes against Neo4j, and returns the connected accounts
- **Read-only by default:** agents in this workshop use only `read-neo4j-cypher`, so they can never modify production graph data

---

<!-- _class: small -->
<style scoped>
section { font-size: 22px; }
h2 { font-size: 32px; }
</style>

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

**Single-source questions** go to one agent:
- **"Total transfer volume for account-1234?"** → Genie (SQL aggregation)
- **"Which accounts share a device with account-1234?"** → Neo4j (graph traversal)

**Multi-source questions** get decomposed:
- **"Find the fraud ring and compute total transfer volume for its members"**
  1. Neo4j agent detects the ring via cycle traversal
  2. Genie agent computes transfer totals for the identified accounts
  3. Supervisor synthesizes a single answer

---

## How the Supervisor Decides

- **Agent descriptions:** each sub-agent registers what it can do, and the supervisor matches questions against those descriptions
- **Guidelines:** domain experts add instructions like "questions about paths belong to the graph agent"
- **Aggregation signals:** "total," "average," or "count" route to Genie because they imply SQL aggregation
- **Relationship signals:** "connected to," "within N hops," or "shared device" route to Neo4j because they imply traversal
- **Decomposition:** when both signal types appear, the supervisor breaks it into sub-tasks for each agent
- **Iterative refinement:** if routing is wrong, experts add a guideline and the correction applies immediately

---

## Summary and What Comes Next

**Databricks + Neo4j** gives you the analytical power of the lakehouse and the relationship intelligence of the graph, connected through governed pipelines:

- **Delta Lake governs the data.** Schema enforcement, ACID transactions, and time travel provide the source of truth
- **Neo4j reveals the connections.** Relationship queries, graph algorithms, and path finding run against the connection topology
- **The Spark Connector bridges both directions.** Lakehouse data becomes a graph, and graph insights flow back to Delta tables
- **Genie queries the lakehouse.** Natural language to SQL over financial transaction tables, configured with domain vocabulary
- **The Neo4j MCP agent queries the graph.** Schema-aware Cypher generation over the knowledge graph
- **A supervisor routes questions** to the right platform automatically, decomposing multi-source questions across both

**Next in this series:** unstructured document retrieval completes the three-source architecture. GraphRAG over embedded document chunks, grounded in the same knowledge graph, combined with the structured and graph querying shown here.
