# Hands-On Lab: Neo4j and Databricks

Build AI Agents and Knowledge Graphs with Neo4j and Databricks.

This hands-on workshop teaches you how to build production-ready AI agents that combine the power of graph databases with modern cloud platforms. You'll work with a comprehensive Aircraft Digital Twin dataset, learning to load data into Neo4j, query it with natural language, and build multi-agent systems that intelligently route questions to the right data source.

## Overview

Participants work through lab exercises in Databricks and Neo4j Aura, using Databricks as the notebook environment for ETL, multi-agent orchestration, and semantic search.

### Data Overview

The workshop uses a comprehensive **Aircraft Digital Twin** dataset that models a complete aviation fleet over 90 operational days. The data is split across two platforms, each chosen for the workload it handles best:

- **Databricks Lakehouse** stores the **time-series sensor telemetry** — 345,600+ hourly readings across 90 days. Columnar storage and SQL make the Lakehouse ideal for aggregations, trend analysis, and statistical comparisons over large volumes of timestamped data.
- **Neo4j Aura** stores the **richly connected relational data** — aircraft topology, component hierarchies, maintenance events, flights, delays, and airport routes. A graph database handles multi-hop relationship traversals natively, avoiding the expensive JOINs a tabular database would require for queries like "Which components caused flight delays?"

Together the dataset includes:

- **20 Aircraft** with tail numbers, models, and operators
- **80 Systems** (Engines, Avionics, Hydraulics) per aircraft
- **320 Components** (Turbines, Compressors, Pumps, etc.)
- **160 Sensors** with monitoring metadata
- **345,600+ Sensor Readings** (hourly telemetry over 90 days)
- **800 Flights** with departure/arrival information
- **300 Maintenance Events** with fault severity and corrective actions
- **12 Airports** in the route network

### Key Technologies

| Technology | Purpose |
|------------|---------|
| **Neo4j Aura** | Graph database for storing aircraft relationships |
| **Databricks** | Notebooks, Unity Catalog |
| **AI/BI Genie** | Natural language analytics over Unity Catalog tables |
| **AgentBricks** | No-code multi-agent supervisor combining multiple data sources |
| **GraphRAG** | Graph-enhanced retrieval combining vector search with graph traversal |
| **Neo4j Spark Connector** | ETL from Databricks to Neo4j |
| **Model Context Protocol (MCP)** | Standard for connecting AI models to data sources |

---

## Lab Structure

### Phase 1: Setup

*Get connected to all workshop resources.*

| Lab | Description | Time |
|-----|-------------|------|
| [Lab 0 - Sign In](./Lab_0_Sign_In) | Access workshop resources | 10 min |
| [Lab 1 - Neo4j Aura Setup](./Lab_1_Aura_Setup) | Save connection credentials | 20 min |

---

### Phase 2: Databricks ETL & Multi-Agent Analytics

*Load aircraft data into Neo4j and build a multi-agent supervisor that combines the Databricks Lakehouse with the Neo4j knowledge graph.*

| Lab | Description | Time |
|-----|-------------|------|
| [Lab 5 - Databricks ETL to Neo4j](./Lab_5_Databricks_ETL_Neo4j) | Load Aircraft Digital Twin data into Neo4j using the Spark Connector and Python driver | 45 min |
| [Lab 6 - AgentBricks](./Lab_6_AgentBricks) | Build a multi-agent supervisor combining Genie Space (sensor analytics) + Neo4j MCP (graph queries) | 75 min |

---

### Phase 3: Semantic Search & GraphRAG

*Add semantic search capabilities to the knowledge graph — chunk maintenance documentation, generate vector embeddings, and build GraphRAG retrievers.*

| Lab | Description | Time |
|-----|-------------|------|
| [Lab 7 - Semantic Search](./Lab_7_Semantic_Search) | Load maintenance manual, generate embeddings, build GraphRAG retrievers | 45 min |

---

## Sample Queries

### Aircraft Topology
```cypher
// What systems does aircraft N95040A have?
MATCH (a:Aircraft {tail_number: 'N95040A'})-[:HAS_SYSTEM]->(s:System)
RETURN a.tail_number, s.name, s.type
```

### Maintenance Analysis
```cypher
// Find aircraft with critical maintenance events
MATCH (a:Aircraft)-[:HAS_SYSTEM]->(s:System)-[:HAS_COMPONENT]->(c:Component)
      -[:HAS_EVENT]->(m:MaintenanceEvent {severity: 'Critical'})
RETURN a.tail_number, s.name, c.name, m.fault, m.reported_at
ORDER BY m.reported_at DESC
```

### Flight Operations
```cypher
// Find delayed flights and their causes
MATCH (a:Aircraft)-[:OPERATES_FLIGHT]->(f:Flight)-[:HAS_DELAY]->(d:Delay)
RETURN a.tail_number, f.flight_number, d.cause, d.minutes
ORDER BY d.minutes DESC
LIMIT 10
```

---

## Prerequisites

- **Laptop** with a modern web browser
- **Network Access** to Databricks and Neo4j Aura
- Neo4j Aura account (SSO or free trial)
- Databricks workspace with Model Serving enabled
- No local software installation required

---

## Knowledge Graph Schema

The Aircraft Digital Twin dataset includes:
- **Nodes**: Aircraft, System, Component, Sensor, Airport, Flight, Delay, MaintenanceEvent, Removal, Document, Chunk
- **Relationships**: HAS_SYSTEM, HAS_COMPONENT, HAS_SENSOR, HAS_EVENT, OPERATES_FLIGHT, DEPARTS_FROM, ARRIVES_AT, HAS_DELAY, AFFECTS_SYSTEM, AFFECTS_AIRCRAFT, HAS_REMOVAL, REMOVED_COMPONENT, FROM_DOCUMENT, NEXT_CHUNK

## Technology Stack

| Component | Technology |
|-----------|------------|
| Graph Database | Neo4j Aura |
| Embeddings | Databricks BGE-large (databricks-bge-large-en) |
| LLM | Databricks Llama 3.3 70B |
| Vector Search | Neo4j Vector Index |
| Multi-Agent | Databricks AgentBricks |
| ETL | Neo4j Spark Connector |

## Configuration

Each notebook has a **Configuration** cell at the top where you enter your Neo4j credentials:

```python
NEO4J_URI = "neo4j+s://xxxxxxxx.databases.neo4j.io"
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "your_password_here"
```

Databricks notebooks use Foundation Model APIs (MLflow deployments client) which handle authentication automatically when running in Databricks.

## Resources

### Neo4j
- [Neo4j Aura Documentation](https://neo4j.com/docs/aura/)
- [neo4j-graphrag Python Library](https://neo4j.com/docs/neo4j-graphrag-python/)
- [Neo4j MCP Server](https://github.com/neo4j/mcp)
- [Neo4j Spark Connector](https://neo4j.com/docs/spark/current/)
- [Cypher Query Language](https://neo4j.com/docs/cypher-manual/current/)

### Databricks
- [Foundation Model APIs](https://docs.databricks.com/aws/en/machine-learning/foundation-model-apis/)
- [AI/BI Genie](https://docs.databricks.com/aws/en/genie/)
- [AgentBricks Multi-Agent Supervisor](https://docs.databricks.com/aws/en/generative-ai/agent-bricks/multi-agent-supervisor)
- [Databricks Unity Catalog](https://docs.databricks.com/en/data-governance/unity-catalog/)

## Feedback

We appreciate your feedback! Please open an issue on the [GitHub repository](https://github.com/neo4j-partners/databricks-neo4j-lab/issues) for bugs, suggestions, or comments.
