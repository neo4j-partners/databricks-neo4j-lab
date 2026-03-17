# Neo4j + Databricks Workshop

## Build AI Agents and Knowledge Graphs

Welcome to the hands-on workshop! You'll build production-ready AI agents that combine graph databases with Databricks AI/ML.

---

## Lab Progression

| Lab | Topic | Type |
|-----|-------|------|
| **Lab 0** | Sign in to Databricks | Setup |
| **Lab 1** | Neo4j Aura Setup | Setup (browser) |
| **Lab 2** | Databricks ETL to Neo4j | Notebooks |
| **Lab 3** | Semantic Search | Notebooks |
| **Lab 4** | Compound AI Agents | Notebooks + UI |
| **Lab 5** | Aura Agents | Notebooks + UI |

---

## Architecture

**Dual Database Strategy:**
- **Databricks Lakehouse** — Time-series sensor telemetry (345K+ readings)
- **Neo4j Aura** — Graph relationships (aircraft topology, maintenance, flights)

**Multi-Agent Supervisor:**
- User question → AgentBricks Supervisor
  - → **Genie Agent** (sensor analytics via SQL)
  - → **Neo4j MCP Agent** (graph queries via Cypher)

---

## Getting Started

1. Open the Databricks workspace (left pane)
2. Navigate to **Lab_2_Databricks_ETL_Neo4j** → `01_aircraft_etl_to_neo4j`
3. Attach to your assigned cluster
4. Follow the notebook instructions

## Need Help?

- Raise your hand for instructor assistance
- Check the lab README files in each folder for detailed instructions

## Neo4j Credentials

Your Neo4j Aura credentials will be provided during Lab 1. Store them in Databricks Secrets as instructed in the notebook.
