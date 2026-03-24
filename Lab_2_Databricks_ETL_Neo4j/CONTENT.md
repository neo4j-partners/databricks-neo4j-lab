# Lab 2: Concepts and Reference

In this lab you move data from Databricks Lakehouse into Neo4j using the Spark Connector. The Lakehouse holds aircraft fleet data as governed Delta tables; by the end, that same data will exist as a traversable graph of aircraft, systems, components, sensors, flights, and maintenance events.

## From the Lakehouse to the Graph

Not everything moves to the graph. Aggregates, metrics, logs, and documents stay in Delta where they belong. Only the subset with connection patterns worth traversing projects into Neo4j. The Lakehouse remains the system of record; the graph is a projection of the connections that matter.

The mapping from tables to graph follows a few recurring patterns, and the value compounds as the mappings get more structural.

**Rows become nodes.** A row in the accounts table becomes an Account node, with columns like account_id, customer_name, and status as node properties.

**Foreign keys become relationships.** A column like `account.address_id` pointing to `addresses.id` becomes `(:Account)-[:REGISTERED_AT]->(:Address)`. These are straightforward one-hop lookups that SQL also handles well.

**Mapping tables become relationships.** A junction table like `account_devices` doesn't become nodes. Each row becomes a `USED_DEVICE` relationship with `first_seen` and `last_seen` as relationship properties. The mapping table disappears entirely.

**Shared attributes become shared nodes.** Two accounts sharing the same SSN have no foreign key between them. Discovering that link in the Lakehouse requires a self-join. In the graph, SSN becomes a shared node and both accounts connect to it, making the hidden connection explicit and traversable.

**Self-referential columns become chains.** `from_account` and `to_account` in a transactions table point to two entities in the same table. In the graph this becomes a `TRANSFERRED_TO` relationship. Chains of these are natural traversals in the graph but require recursive CTEs in SQL.

Foreign keys are simple one-hop lookups. Mapping tables eliminate multi-table joins. Shared attributes reveal hidden networks. Self-referential chains replace recursive CTEs. The further down the list, the more the graph pays off relative to SQL.

## ELT: Lakehouse to Graph

Raw data lands in cloud storage (S3, ADLS Gen2, GCS) as the unprocessed landing zone. Databricks processes that raw data into Delta tables via Jobs, Notebooks, or Spark Declarative Pipelines. Delta Lake enforces schema and rejects bad data at ingestion: column renaming, type casting, and validation happen here so that graph properties are clean without extra transformation downstream. Delta tables are the interchange format; the Neo4j Spark Connector reads from these governed tables.

### The Neo4j Spark Connector

The Spark Connector is the officially supported bridge between Databricks and Neo4j. It turns Lakehouse rows into graph nodes and relationships, and pulls graph data back into DataFrames for analytics or ML. It supports batch and incremental loading patterns.

**Node loading** maps DataFrame columns to node properties. Each row becomes a node via batched upserts (create if new, update if existing), making the load idempotent. The connector uses `labels` and `node.keys` options to control which label the node gets and which property serves as its unique identifier. Nodes load first because both endpoints must exist before relationships can be created.

**Relationship loading** matches existing nodes by property values and creates the specified relationship type between them. Transaction details or operational metadata ride as properties on the relationship itself; no separate edge table, no foreign key resolution at query time.

### Design Decision: Relationship Types vs. Properties

A common modeling choice: use one relationship type per connection kind (`:TRANSFERRED_TO`, `:SHARED_DEVICE`) with indexed type lookups and faster traversal, or use a generic type with a property (`:CONNECTED {type: "transfer"}`) for a simpler schema but slower property filters. Default to type per connection when traversals follow specific connection types. Neo4j relationships are directional, so bidirectional flows require writing in both directions.

### Validation

The connector reads from Neo4j just as easily as it writes, returning Cypher results as standard DataFrames. Three checks cover the common failure modes: node counts should match source row counts, relationship counts should fall within expected ranges, and high-connectivity nodes should reflect known patterns from the source data. If counts don't match, the most common causes are failed node loads or key value mismatches. The connector silently drops relationships when the MATCH clause can't find the target node.

## Graph Insights Flow Back to the Lakehouse

Graph intelligence flows back as standard DataFrames. Graph-derived metrics become columns in Delta Gold tables, available for dashboards, ML features, and downstream analytics. Cycle detection identifies entities involved in circular chains. PageRank scores influential nodes for risk prioritization. Louvain community detection clusters tightly connected entities into groups. Degree centrality counts connections as ML features. Once in Delta Lake, these insights join with operational data that never left the Lakehouse. This is the Gold layer in action: graph intelligence enriching data intelligence.

## Databricks Compute and Notebooks

In Databricks, **compute** refers to a managed cluster of virtual machines that provides the Spark runtime needed to execute code. Your workshop compute comes pre-configured with Apache Spark, the Neo4j Spark Connector, and the Python packages required by the lab notebooks.

A **notebook** is an interactive document of cells containing Python, SQL, or markdown. You run cells sequentially, and each cell displays its output inline. Notebooks are the primary interface for the ETL work in this lab.

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
