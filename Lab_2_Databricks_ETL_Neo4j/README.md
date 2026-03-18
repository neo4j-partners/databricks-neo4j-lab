# Lab 2: Databricks ETL to Neo4j

Load aircraft data from Databricks into Neo4j using the Spark Connector.

> **Background Reading:** For the concepts and architecture behind this lab, see [CONTENT.md](CONTENT.md).

> **Infrastructure:** This lab uses the Vocareum lab environment for the Databricks workspace setup and notebook execution.

**Duration:** ~45 minutes

---

## Notebooks

This lab has two notebooks:

| Notebook | Description | Required For |
|----------|-------------|--------------|
| [`01_aircraft_etl_to_neo4j.ipynb`](01_aircraft_etl_to_neo4j.ipynb) | Core ETL — loads Aircraft, System, and Component nodes using the Spark Connector | Labs 3, 4 |
| [`02_load_neo4j_full.ipynb`](02_load_neo4j_full.ipynb) | Full dataset — adds Sensors, Airports, Flights, Delays, Maintenance Events, and Removals using the Spark Connector | **Lab 4** |

> **Important:** Run **both** notebooks before proceeding. Notebook 01 loads the core aircraft topology needed by all subsequent labs. Notebook 02 loads the complete dataset required by the Neo4j MCP agent in Lab 4 (Compound AI Agents).

---

## Prerequisites

Before starting this lab, ensure you have:

- [ ] Neo4j Aura credentials from Lab 1 (URI, username, password)
- [ ] Vocareum lab environment access

---

## Instructions

Use the Vocareum lab setup to complete the Databricks workspace configuration and run the ETL notebooks.

---

## What You Loaded

For the full data model diagrams, entity counts, and sample aircraft, see [CONTENT.md](CONTENT.md#the-aircraft-digital-twin-data-model).

---

## Troubleshooting

### "Connection refused" or timeout errors

- Verify your Neo4j URI starts with `neo4j+s://` (note the `+s`)
- Check your Neo4j Aura instance is running (green status in console)
- Confirm username and password are correct (no extra spaces)

### "Spark Connector not found" error

- Ensure you're using the workshop compute (not a personal compute)
- The cluster must be in **Dedicated (Single User)** access mode
- Try restarting the compute

### "Path does not exist" for data files

- Verify the DATA_PATH matches your workshop configuration
- Ask your instructor for the correct Volume path

### Duplicate nodes appearing

- The notebook uses Overwrite mode, so re-running should replace data
- If needed, clear your Neo4j database first:
  ```cypher
  MATCH (n) DETACH DELETE n
  ```

### Notebook cells failing

- Run cells in order from top to bottom
- Don't skip the configuration cells
- Check the error message for specific issues

---

## Key Concepts

See [CONTENT.md](CONTENT.md#key-concepts) for a summary of Unity Catalog Volumes, the Spark Connector, and other concepts from this lab.

---

## Next Steps

After completing this lab:
- Continue to [Lab 3 - Semantic Search](../Lab_3_Semantic_Search) to add GraphRAG capabilities over maintenance documentation
- Continue to [Lab 4 - Compound AI Agents](../Lab_4_Compound_AI_Agents) to build a Supervisor Agent with Genie space and Neo4j MCP
- The data you loaded will be queried by AI agents in later labs

---

## Help

- Ask your instructor for assistance
- Check the [Neo4j Spark Connector docs](https://neo4j.com/docs/spark/current/)
- Review the [Cypher Query Language reference](https://neo4j.com/docs/cypher-manual/current/)
