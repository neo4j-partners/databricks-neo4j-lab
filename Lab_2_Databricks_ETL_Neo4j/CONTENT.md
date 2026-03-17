# Lab 2: Concepts and Reference

In this lab you move data from Databricks Lakehouse into Neo4j using the Spark Connector. The Lakehouse holds aircraft fleet data as governed Delta tables; by the end, that same data will exist as a traversable graph of aircraft, systems, components, sensors, flights, and maintenance events. This section covers the architectural concepts behind that pipeline.

## The Medallion Architecture

Databricks organizes data through progressive refinement across three layers. **Bronze** is the raw landing zone: files arrive from cloud storage with no transformation. **Silver** is the curation layer: schema enforcement, type casting, and column renaming produce clean, governed tables ready for downstream consumers. **Gold** is where analytical outputs live: business-ready aggregates, ML features, and metrics enriched by insights from other systems.

Data flows forward through the layers. In this lab, the Spark Connector reads from Silver tables and writes nodes and relationships into Neo4j. In later stages of a production pipeline, graph algorithm results (community scores, centrality metrics, cycle detection flags) flow back into Gold tables, joining with operational data that never left the Lakehouse. Silver feeds the graph; Gold captures what the graph discovers.

## Dual Database Architecture

Not all data moves to the graph. Aggregates, time-series telemetry, and high-volume sensor readings stay in Delta where distributed SQL handles them well. Only the subset with connection patterns worth traversing projects into Neo4j. The Lakehouse remains the system of record; the graph is a projection of the relationships that matter.

The mapping from tables to graph follows a few recurring patterns. Rows become nodes: a row in the `aircraft` table becomes an `Aircraft` node with columns as properties. Foreign keys become relationships: `system.aircraft_id` pointing to `aircraft.id` becomes `(:Aircraft)-[:HAS_SYSTEM]->(:System)`. Mapping tables dissolve into relationships entirely. Self-referential columns (like `from_account` and `to_account` in a transactions table) become relationship chains that are natural traversals in the graph but require recursive CTEs in SQL.

The value compounds as the mappings get more structural. Foreign keys are simple one-hop lookups that SQL also handles well. Shared attributes surface implicit connections. Self-referential chains replace recursive CTEs. The further down the list, the more the graph pays off.

## SQL vs. Cypher: A Side-by-Side

Consider a fraud investigation question: find all accounts within three hops of a flagged account through shared devices or addresses.

**SQL** requires manually coding each hop as a separate CTE with explicit joins across two link tables:

```sql
WITH hop1 AS (
    SELECT DISTINCT ad2.account_id
    FROM account_devices ad1
    JOIN account_devices ad2
      ON ad1.device_id = ad2.device_id AND ad1.account_id != ad2.account_id
    WHERE ad1.account_id = 'account-1234'
    UNION
    SELECT DISTINCT aa2.account_id
    FROM account_addresses aa1
    JOIN account_addresses aa2
      ON aa1.address_id = aa2.address_id AND aa1.account_id != aa2.account_id
    WHERE aa1.account_id = 'account-1234'
),
hop2 AS ( ... ),   -- same pattern, joining from hop1
hop3 AS ( ... )    -- same pattern, joining from hop2
SELECT account_id FROM hop1 UNION
SELECT account_id FROM hop2 UNION
SELECT account_id FROM hop3;
```

**Cypher** expresses the same traversal in three lines:

```cypher
MATCH (flagged:Account {account_id: 'account-1234'})
      -[:USED_DEVICE|REGISTERED_AT*1..3]-
      (connected:Account)
WHERE connected <> flagged
RETURN DISTINCT connected.account_id
```

Adding a fourth hop means another CTE block in SQL. In Cypher, it means changing `*1..3` to `*1..4`. The graph query mirrors the shape of the problem: follow connections outward to a variable depth. SQL reconstructs that shape through iterative self-joins.

This distinction drives the dual database strategy. Aggregation questions ("total transfer volume by account") belong in SQL. Traversal questions ("which accounts are reachable from a flagged account?") belong in Cypher. Most real investigations need both platforms working together.

## Financial Fraud: Another Graph + Lakehouse Pattern

The aircraft digital twin is one instance of a broader pattern. Financial fraud detection follows the same dual database architecture. Money laundering moves funds through chains of accounts and back to the origin. Each individual transfer looks legitimate in isolation; the circular pattern is only visible when you follow the connections.

In the Lakehouse, fraud data lives across `accounts`, `transactions`, `devices`, and junction tables like `account_devices`. In the graph, those become `(:Account)-[:TRANSFERRED_TO]->(:Account)` chains, shared `(:Device)` and `(:Address)` nodes, and `(:SSN)` nodes that surface hidden identity overlaps. Community detection algorithms identify tightly connected clusters, and those cluster assignments write back to Gold tables for case management. The pipeline shape is the same: Silver tables feed the graph, graph insights enrich Gold.

## Databricks Compute and Notebooks

In Databricks, **compute** refers to a managed cluster of virtual machines that provides the Spark runtime needed to execute code. Your workshop compute comes pre-configured with Apache Spark, the Neo4j Spark Connector, and the Python packages required by the lab notebooks.

A **notebook** is an interactive document of cells containing Python, SQL, or markdown. You run cells sequentially, and each cell displays its output inline. Notebooks are the primary interface for the ETL work in this lab.

## The Neo4j Spark Connector

The Spark Connector is the bridge between Databricks and Neo4j. It reads DataFrames from governed Delta tables and writes them as graph nodes and relationships. The load follows a strict order: nodes first via batched upserts (create if new, update if existing), then relationships, because both endpoints must exist before the connector can match them.

**Node loading** maps DataFrame columns to node properties. The connector uses `labels` and `node.keys` options to control which label the node gets and which property serves as its unique identifier. **Relationship loading** uses a `keys` strategy to match existing nodes by property values, then creates the specified relationship type between them. Transaction details or operational metadata ride as properties on the relationship itself.

## What You're Loading

**Notebook 01** builds the core aircraft topology:

```
(Aircraft) -[:HAS_SYSTEM]-> (System) -[:HAS_COMPONENT]-> (Component)
```

This loads 20 aircraft, 80 systems (engines, avionics, hydraulics), and 320 components (fans, compressors, turbines, pumps).

**Notebook 02** adds operational and maintenance data on top of that topology: sensors attached to systems, flights operated by aircraft, delays on flights, maintenance events affecting components, and component removals. This brings in approximately 160 sensors, 800 flights, 300 delays, 300 maintenance events, and 60 removals across 12 airports.

## Key Concepts

1. **Unity Catalog Volumes** store files accessible from notebooks
2. **Nodes first, relationships second** ensures endpoints exist before connections are created
3. **Cypher queries from Databricks** verify data loaded correctly by checking node and relationship counts against source row counts
