# Lab 4: Concepts and Reference

Lab 4 builds a multi-agent system that combines graph intelligence from Neo4j with lakehouse analytics from Databricks. The architecture routes natural language questions to specialized agents, each mastering one data platform, and synthesizes their answers into a single response. This page covers the concepts behind that architecture: what agents are, how they reason, and why this problem needs two of them with a coordinator on top.

## Agent Fundamentals and the ReAct Pattern

An AI agent is more than a language model answering questions. It perceives its environment (the user's question, available tools, conversation history), reasons about what to do, takes action by calling tools, and returns a response. These four stages run in a loop: after observing the result of one action, the agent can reason again and take another.

This loop is the **ReAct pattern** (Reason + Act). The agent receives a question, reasons about which tool fits, executes it, observes the result, and decides whether to respond or continue with another tool call. A question like "Find aircraft with high vibration and show their maintenance history" triggers multiple cycles: the agent reasons that it needs sensor data first, calls one tool, observes the result, reasons that it now needs maintenance records, calls a second tool, and synthesizes both into a final answer.

Tools are what give agents their capabilities. Each tool has a description that the agent matches against the user's question during the reasoning phase. A tool described as "execute read-only Cypher queries against the graph database" will be selected when the agent encounters a relationship traversal question; a tool described as "query sensor telemetry via SQL" will be selected for time-series aggregations. The quality of these descriptions directly affects routing accuracy.

## Agent Bricks

Databricks Agent Bricks is the platform layer for building and deploying AI agents within the Databricks ecosystem. It provides the scaffolding for defining agent behavior, connecting tools (including Genie spaces and external services), and deploying agents as governed endpoints. In this lab, Agent Bricks hosts the supervisor agent that coordinates between the Genie and Neo4j sub-agents.

Agent Bricks handles the operational concerns that sit outside the agent's reasoning loop: authentication, tool registration, deployment, and monitoring. The agents you build in Parts A and B run as Agent Bricks components, which means they inherit Unity Catalog governance and can be served, versioned, and observed through standard Databricks workflows.

## MCP: Model Context Protocol

MCP (Model Context Protocol) is an open standard that exposes data sources and services as tools that any agent framework can discover and call. Instead of writing custom integration code for each data source, MCP defines a uniform interface: the agent asks what tools are available, receives their descriptions and parameter schemas, and calls them through a standard protocol.

Neo4j exposes its graph intelligence through MCP with two primary tools. **`get-schema`** introspects the live database using APOC, returning a token-efficient representation of every node label, relationship type, and property key. **`read-cypher`** executes read-only Cypher queries with parameterized inputs. Together, these tools give the Neo4j agent everything it needs: schema discovery to understand the graph structure, and query execution to traverse it. Write operations are hidden entirely, so agents can never modify production data.

## Why Two Data Sources?

Aircraft intelligence requires two fundamentally different data shapes. Sensor telemetry (345,600+ hourly readings across 90 days) lives in Delta Lake tables where SQL excels at time-series aggregations, statistical analysis, and fleet-wide comparisons. The Genie space translates natural language into SQL against these tables.

The Neo4j knowledge graph stores the structural relationships of the aircraft fleet: how aircraft connect to systems, systems to components, components to maintenance events, flights to airports, and delays to root causes. Graph traversal answers multi-hop questions ("Which components in the hydraulics system of AC1001 had maintenance events that caused flight delays?") that would require expensive JOIN chains across many relational tables.

No single agent can master both SQL aggregation over sensor telemetry and Cypher traversal over a knowledge graph. The reasoning patterns are different: SQL thinks in rows, filters, and aggregations; Cypher thinks in paths, patterns, and traversals. Combining both schemas and query languages in one prompt dilutes focus and produces queries that mix idioms.

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
