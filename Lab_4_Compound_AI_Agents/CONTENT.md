# Lab 4: Concepts and Reference

Lab 3 built a knowledge graph from maintenance documentation and enabled semantic search over it. GraphRAG grounds LLM answers in retrieved content enriched with graph context: entities, relationships, connected chunks. But GraphRAG can only reach data in the graph. The full sensor telemetry ledger (345,600+ hourly readings across 90 days) stays in Delta Lake. GraphRAG cannot answer "what is the average EGT for aircraft N95040A?" because that requires SQL aggregation over rows that never entered the graph. To answer questions that span both platforms, the architecture needs agents.

## Agent Fundamentals and the ReAct Pattern

An AI agent is more than a language model answering questions. It perceives its environment (the user's question, available tools, conversation history), reasons about what to do, takes action by calling tools, and returns a response. These four stages run in a loop: after observing the result of one action, the agent can reason again and take another.

This loop is the **ReAct pattern** (Reason + Act). The agent receives a question, reasons about which tool fits, executes it, observes the result, and decides whether to respond or continue with another tool call. A question like "Find aircraft with high vibration and show their maintenance history" triggers multiple cycles: the agent reasons that it needs sensor data first, calls one tool, observes the result, reasons that it now needs maintenance records, calls a second tool, and synthesizes both into a final answer.

Tools are what give agents their capabilities. Each tool has a description that the agent matches against the user's question during the reasoning phase. The quality of these descriptions directly affects routing accuracy.

## Agent Bricks

Databricks Agent Bricks is the platform layer for building and deploying AI agents within the Databricks ecosystem. It provides the scaffolding for defining agent behavior, connecting tools (including Genie spaces and external services), and deploying agents as governed endpoints. Agent Bricks handles the operational concerns that sit outside the agent's reasoning loop: authentication, tool registration, deployment, and monitoring. The agents you build in this lab run as Agent Bricks components, inheriting Unity Catalog governance.

## Specialized Agents for Different Data Structures

Two schemas, two query languages, and two sets of conventions in one prompt dilute focus. An agent that only knows about graph structure writes precise graph queries; an agent that knows about both starts mixing idioms. SQL thinks in rows, filters, and aggregations. Cypher thinks in paths, patterns, and traversals. A generalist agent spread across both produces queries that mix these idioms, like attempting a JOIN where a traversal belongs.

The architecture separates concerns: one agent per platform, a supervisor to coordinate them.

### Databricks Genie: Natural Language to SQL

Genie is a compound AI system, not a single LLM. It turns natural language into governed SQL, purpose-built for tabular data. Genie queries any data registered in Unity Catalog: managed tables, external tables, foreign tables from federated sources, and views. Unity Catalog provides the metadata that makes Genie effective: table names, column descriptions, primary and foreign key relationships.

Domain experts configure Genie Spaces: curated sets of tables with JOIN definitions, plain-text instructions teaching domain terminology and business rules, and example SQL queries that Genie selects from when they match the user's question. When a response matches a parameterized example query exactly, Genie marks it as "Trusted." Every generated query is read-only.

### Neo4j Graph Agent: Natural Language to Cypher

The Neo4j agent is purpose-built for connected data: paths, multi-hop traversals, cycle detection, shared-attribute matching. It inspects every node label, relationship type, and property key before querying, so the graph's schema becomes a constraint that guides generation rather than a suggestion to ignore. Every generated query is read-only.

The agent accesses Neo4j through MCP (Model Context Protocol), an open standard that exposes data sources as tools any agent framework can discover and call. Neo4j exposes three MCP tools:

- **`get-schema`** introspects the live database using APOC, returning a token-efficient representation of every node label, relationship type, and property key.
- **`read-cypher`** executes read-only Cypher queries with parameterized inputs.
- **`list-gds-procedures`** discovers available graph algorithms (PageRank, community detection, similarity) when GDS is installed.

Write operations are hidden entirely, so agents can never modify production data.

## Multi-Agent Architecture

A supervisor agent sits above both specialists and routes questions based on their nature.

```
User Question
     |
     v
Multi-Agent Supervisor (Agent Bricks)
     |
     +---> "sensor readings?" ---> Genie Space ---> Unity Catalog (Lakehouse)
     |        time-series              SQL           345,600+ sensor readings
     |        aggregations
     |
     +---> "relationships?" ---> Neo4j MCP Agent ---> Knowledge Graph (Aura)
     |        topology               Cypher            8 node types, 13 relationships
     |        maintenance
     |
     +---> "both needed?" ---> Sequential calls to both agents
                               |
                               v
                         Synthesized Response
```

The supervisor does not answer questions itself. It reads the question, determines which data shape it targets, and routes to the right specialist. For questions that span both platforms, it decomposes the question into sub-tasks, sends each to the appropriate agent, and synthesizes a single answer.

## Query Routing Strategy

| Question Type | Route To | Example |
|---------------|----------|---------|
| Time-series aggregations | Genie | "What's the average EGT over the last 30 days?" |
| Statistical analysis | Genie | "Show sensors with readings above 95th percentile" |
| Trend analysis | Genie | "Compare fuel flow rates between 737 and A320" |
| Relationship traversals | Neo4j | "Which components are connected to Engine 1?" |
| Pattern matching | Neo4j | "Find all aircraft with maintenance delays" |
| Topology exploration | Neo4j | "Show the system hierarchy for N95040A" |
| Combined analytics | Both | "Find aircraft with high vibration AND recent maintenance events" |

## Sample Questions

### Genie Agent (Sensor Analytics)
- "What is the average EGT temperature for aircraft N95040A?"
- "Show daily vibration trends for Engine 1 over the last month"
- "Which sensors have readings above their 95th percentile?"
- "Compare fuel flow rates between Boeing and Airbus aircraft"

### Neo4j Agent (Graph Relationships)
- "Which systems does aircraft AC1001 have?"
- "Show all maintenance events affecting Engine 1"
- "Find flights that were delayed due to maintenance"
- "What components are in the hydraulics system?"

### Multi-Agent (Combined Queries)
- "Find aircraft with high EGT readings and show their recent maintenance history"
- "Which engines have above-average vibration, and what components were recently serviced?"
- "Compare sensor trends for aircraft that had delays versus those that didn't"
