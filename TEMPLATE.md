# Neo4j GenAI Hands-On Lab with Databricks Program Template, 2026

## Program Name

Build AI Agents and Knowledge Graphs with Neo4j and Databricks

## Workshop Overview

This workshop equips participants with practical skills to combine Neo4j's graph database platform with Databricks AI/ML capabilities to build production-ready AI agents that combine the power of graph databases with modern cloud platforms.

Participants will work with a comprehensive Aircraft Digital Twin dataset to experience how knowledge graphs enhance AI applications with structured context and relationship-aware retrieval.

Through a series of guided exercises, attendees will:

- Deploy and explore Neo4j Aura, the fully managed cloud graph platform
- Load data into Neo4j using the Spark Connector
- Build multi-agent systems with Databricks AgentBricks that coordinate across SQL and graph data sources
- Connect to Neo4j using the Model Context Protocol (MCP) server for standardized graph access
- Build GraphRAG pipelines using Databricks Foundation Model APIs
- Add semantic search capabilities with vector embeddings

---

## Lab Agenda

### Phase 1 – Setup (Beginner Friendly)

#### Overview

Get connected to all workshop resources and set up your Neo4j Aura database.

#### Labs

- **Lab 0 – Sign In**: Sign into Databricks and workshop environment
- **Lab 1 – Neo4j Aura Setup**: Provision Neo4j Aura and save connection credentials for later labs

---

### Phase 2 – Databricks ETL & Semantic Search (Intermediate)

#### Overview

Load aircraft data into Neo4j, then add semantic search capabilities — chunk maintenance documentation, generate vector embeddings, and build GraphRAG retrievers that blend similarity search with graph traversal.

#### Lecture — Neo4j + Generative AI Concepts

- GraphRAG: Graph Retrieval-Augmented Generation and why graphs matter for AI
- Retrieval Patterns: Semantic search, hybrid retrieval, and context-aware generation

#### Labs

- **Lab 5 – Databricks ETL to Neo4j**: Load Aircraft Digital Twin data into Neo4j using the Spark Connector
  - Load core aircraft topology (Aircraft, System, Component) via Spark Connector
  - Load full dataset (Sensors, Airports, Flights, Delays, Maintenance Events, Removals) via Spark Connector
  - Validate with Cypher queries and explore in Neo4j Aura
- **Lab 6 – Semantic Search**: Build GraphRAG pipelines over maintenance documentation
  - Load the A320-200 Maintenance Manual into Neo4j as Document/Chunk nodes
  - Generate embeddings using Databricks Foundation Model APIs (BGE-large)
  - Create a vector index for similarity search
  - Build GraphRAG retrievers combining vector search with graph traversal
  - Compare standard vector retrieval vs. graph-enhanced retrieval results

---

### Phase 3 – Multi-Agent Analytics (Intermediate-Advanced)

#### Overview

Build a multi-agent supervisor that combines the Databricks Lakehouse with the Neo4j knowledge graph — two purpose-built systems for two fundamentally different types of data.

#### Lecture — Databricks AgentBricks and Multi-Agent Systems

- Databricks AI/BI Genie: Natural language to SQL for business users
- AgentBricks Multi-Agent Supervisor: Orchestrating specialized agents for complex tasks
- Model Context Protocol (MCP): The open standard for connecting AI agents to external tools and data sources
- Multi-Source Coordination: Combining structured data (Unity Catalog) with graph relationships (Neo4j) in agent systems

#### Labs

- **Lab 7 – AgentBricks Multi-Agent**: Build a multi-agent system with Databricks AgentBricks
  - Create a Databricks AI/BI Genie space for natural language sensor analytics
  - Connect to Neo4j via external MCP server for graph queries
  - Build a Multi-Agent Supervisor that routes questions to the appropriate data source
  - Test cross-system queries combining sensor telemetry and graph relationships
