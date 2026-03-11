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

## What GraphRAG Solves and Where It Stops

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

## Databricks Genie for Structured Data

**Genie** translates natural language into SQL against governed Delta tables. No SQL knowledge required from the end user.

1. **Connect Genie to your tables:** the financial transaction tables from the fraud example
2. **Add domain knowledge:** plain-text instructions that teach Genie what "suspicious transfer" means, what normal transaction volumes look like, what a flagged account is
3. **Users ask in English:** "What is the total transfer volume for account-1234 in the last 90 days?" becomes SQL, executes against Delta Lake, and returns the answer

Domain experts configure **Genie Spaces** with curated table sets, sample queries, and up to 100 instructions per space.

---

## Neo4j MCP Agent for Graph Queries

**Model Context Protocol (MCP)** lets AI agents use external tools. Neo4j acts as an MCP server, giving agents the ability to query the knowledge graph directly.

1. **Inspect the schema:** the agent learns what node types and relationship types exist
2. **Generate Cypher:** the agent writes a query against verified structure, not guessed table names
3. **Execute and return:** results come back as structured data the agent can reason over

"Which accounts are within three hops of the flagged account?" The agent discovers the `Account` nodes and `TRANSFERRED_TO` relationships from the schema, then generates and runs the traversal.

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

## Multi-Agent Routing in the Fraud Domain

**"What is the average transaction amount for flagged accounts?"**
→ Supervisor sends to the **Genie agent:** numeric aggregation over the transaction ledger

**"Which accounts are reachable within three hops of account-1234?"**
→ Supervisor sends to the **Neo4j agent:** variable-depth graph traversal

**"Find accounts in circular transaction chains and show their total transfer volumes"**
→ Supervisor calls **both agents in sequence:**
  1. Neo4j agent runs cycle detection to identify the ring
  2. Genie agent queries the transaction ledger for volume totals scoped to those accounts
  3. Supervisor combines the structural pattern with the financial evidence

No Cypher or SQL knowledge required from the investigator.

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
