# Building the Intelligence Platform — Speaker Notes

## Slide: Building the Intelligence Platform

_Title slide — no speaker notes._

---

## Slide: Databricks & Neo4j: Better Together

Databricks and Neo4j have an official technology partnership. What we wanted to cover today is a quick preview of what that partnership delivers before we get into the technical details.

The foundation is the Spark Connector — Databricks-certified, tested against Databricks runtimes, and supported by Neo4j. It's the primary bridge for moving data between the lakehouse and the graph.

And that data flows both directions. Lakehouse tables map or project into the graph as nodes and relationships. Graph algorithm results — fraud scores, community assignments, centrality metrics — write back to Delta Gold tables for dashboards and ML.

Once the data is in the graph, agent integration is where things get interesting for AI workloads. Neo4j exposes graph queries as MCP tools that Databricks agents can call directly. An investigation agent can route to Genie for SQL analytics and to Neo4j for graph traversal in the same conversation.

Those agents get even more powerful with GraphRAG, which combines vector search with graph traversal. Instead of retrieving isolated text chunks, you retrieve chunks plus their graph neighborhood — the entities, relationships, and context around them. That's what makes answers accurate and grounded.

Tying it all together is graph analytics at scale. Algorithms like PageRank, community detection, and cycle detection run on the graph and surface patterns that are invisible in flat tables — fraud rings, supply chain vulnerabilities, identity clusters.

---

## Slide: Data Intelligence Meets Graph Intelligence

Databricks is the Data Intelligence Platform. It governs and analyzes structured, semi-structured, and unstructured data at scale.

Neo4j is the Graph Intelligence Platform. It makes connections between entities explicit and traversable.

What we wanted to cover today is the framing for the rest of the deck. The next two slides break down what each platform actually does.

---

## Slide: Databricks: The Data Intelligence Platform

Databricks handles structured, semi-structured, and unstructured data. It aggregates transactions and sensor streams, governs documents and images through Unity Catalog, runs SQL against Delta Lake at petabyte scale, and supports ML pipelines from feature engineering through model serving. Schema enforcement, ACID transactions, and time travel provide the foundation.

---

## Slide: Neo4j: The Graph Intelligence Platform

Neo4j makes connections between entities explicit and traversable. Cypher is the query language for graph databases, operating over nodes and relationships. Multi-hop traversals that would require complex recursive SQL run in milliseconds. Pattern matching across connection topologies reveals structures invisible in flat tables.

---

## Slide: The Medallion Architecture

The Medallion Architecture is how Databricks organizes the Data Pipeline stage. Bronze is the raw landing zone: files arrive from cloud storage with no transformation. Silver is the general curation layer: schema enforcement, type casting, column renaming. Customer_ID becomes account_id, Txn_Amount becomes amount. Silver tables are governed and ready for downstream consumers, including the Spark Connector writing to Neo4j.

Gold is where all intelligence converges. Graph algorithm results (cycle detection, PageRank, community scores) write back to Delta as columns in Gold tables. These join with operational data that never left the lakehouse to produce fraud alerts, risk scores, and ML feature tables for case management.

Data flows forward through the layers, graph insights flow back. Silver feeds the graph, Gold captures what the graph discovers. This bidirectional flow is where data intelligence and graph intelligence compound each other's value.

---

## Slide: Building the Intelligence Platform (Four Stages)

Four stages connect Databricks to Neo4j, each building a layer of intelligence. The Data Pipeline is data intelligence: data loads into cloud storage, gets transformed inside the lakehouse, and the Spark Connector batch-loads curated tables as graph nodes and relationships. Knowledge Graph Construction uses the neo4j-graphrag-python Knowledge Graph Builder (SimpleKGPipeline) to chunk regulatory and AML policy documents, generate embeddings, extract entities, and write them back into Neo4j. Data Analytics combines graph insights written back to Delta with lakehouse data for dashboards, reports, and ML features, queried through Unity Catalog JDBC for governed cross-system joins. GraphRAG Retrieval combines vector search with graph traversal via the VectorCypherRetriever, exposed as MCP tools so investigation agents can query the graph and the lakehouse together.

---

## Slide: The Intelligence Platform — Data Flow

The same four stages visualized as a data flow. Stages 1-2 flow left to right (Databricks to Neo4j): Silver tables through the Spark Connector become graph nodes; unstructured docs through the KG Builder become embeddings and entities. Stage 3 reverses: graph insights flow back to Gold tables. Stage 4 spans both: the multi-agent supervisor routes to Genie (SQL) and the Neo4j MCP agent (Cypher).

---

## Slide: Neo4j Connection Patterns by Platform Stage

Each platform stage uses a different connector optimized for its workload. The Data Pipeline uses the Spark Connector for batch DataFrame writes into Neo4j. This is the primary path for bulk loading structured data.

Knowledge Graph Construction uses the Neo4j Python driver directly, not the Spark Connector. The SimpleKGPipeline from neo4j-graphrag-python handles chunking, LLM-based entity extraction, and embedding generation, none of which are Spark operations.

Data Analytics uses both connectors. The Spark Connector provides first-class GDS integration: invoke PageRank, community detection, and other graph algorithms directly, get results as DataFrames for ML features and Gold Delta tables. Neo4j's docs position this as a "graph co-processor" in existing Spark ML workflows. Unity Catalog JDBC adds the governed SQL layer: register Neo4j as a JDBC connection, query graph data via SQL translated to Cypher, join graph results with Delta tables, and connect BI tools like Power BI and Tableau through standard JDBC.

GraphRAG Retrieval uses the Neo4j MCP Server to expose schema inspection and read-only Cypher as agent tools. The Python driver powers the VectorCypherRetriever underneath, combining vector search with graph traversal in a single query.

---

## Slide: Two Data Models, Two Query Languages

_Section title slide — no speaker notes._

---

## Slide: Financial Fraud as a Working Example

We'll use financial fraud to walk through each pipeline stage. Money laundering moves funds through chains of accounts and back to the origin. Each individual transfer looks legitimate in isolation. The circular pattern is only visible when you follow the connections.

This is where graph structure pays off. Detecting A transferred to B transferred to C transferred back to A is a single Cypher pattern match. In SQL, the same detection requires recursive CTEs that self-join the transactions table at each hop, with explicit visited-node tracking to prevent infinite loops. The graph represents the cycle directly; the table has to reconstruct it.

---

## Slide: Fraud Ring — Dual Database Architecture

The lakehouse holds everything: transactions, accounts, devices, addresses. Most of that data stays in Delta. But a subset of it — the accounts, the transfers between them, the shared devices and addresses — forms a network of real-world connections. That's the data you extract into the graph.

This is sometimes called a digital twin: you're representing the real-world connections between entities in a digital model that you can traverse and query. The graph doesn't replace the lakehouse — it's a projection of the connections that matter for investigation. The lakehouse remains the system of record for volumes, aggregates, and history. The graph makes the relationships between entities explicit and traversable.

This diagram shows that dual architecture. Databricks holds the governed tables. Neo4j holds the connected data — the relationships between accounts, devices, and addresses stored explicitly and traversable without joins. Both stay in sync through the Spark Connector.

---

## Slide: Neo4j Graph Components

A graph data schema defines the structure of your graph — the types of nodes, the types of relationships between them, and the properties each carries. Think of it as the equivalent of a relational schema, but instead of tables and foreign keys, you're defining entity types and the named connections between them. In Neo4j, the schema is flexible: you don't have to declare it upfront the way you would with CREATE TABLE, but in practice you design one so your data is consistent and your queries are predictable.

The building blocks are nodes and relationships. A node represents an entity — an account, a person, a device, an address. Nodes carry properties: key-value pairs like account_id, customer_name, or status. In Cypher, you write nodes in parentheses: `(:Account)`. Labels like Account categorize nodes the way table names categorize rows.

A relationship is a named, directed connection between two nodes. It always has a type, a start node, and an end node. Relationships can also carry properties — in the fraud example, a TRANSFERRED_TO relationship holds amount, timestamp, and channel directly on the edge. In Cypher, relationships go in square brackets: `[:TRANSFERRED_TO]`. The arrow gives you direction: `(:Account)-[:TRANSFERRED_TO]->(:Account)`.

The combination of nodes, relationships, and their properties is what makes graph data different from tabular data. The connections aren't implicit in foreign keys that require joins to follow — they're stored directly and traversable in constant time per hop.

---

## Slide: Data Intelligence, Graph Intelligence, or Both?

Each question maps to the platform built to answer it. The third row shows why you need both: Neo4j detects the fraud ring through cycle traversal, Databricks computes transfer totals for the identified accounts. Neither platform can answer that question alone.

Cypher detects the cycle in the graph: a single query finds 2-6 hop loops in milliseconds. The equivalent SQL in the lakehouse requires recursive CTEs with explicit cycle-detection guards. Both platforms contribute, neither can answer alone.

---

## Slide: From the Lakehouse to the Graph

Not everything moves to the graph. Aggregates, metrics, logs, and documents stay in Delta where they belong. Only the subset with connection patterns worth traversing projects into Neo4j. The lakehouse remains the system of record; the graph is a projection of the connections that matter.

Rows become nodes. A row in the accounts table becomes an Account node. Columns like account_id, customer_name, and status become node properties.

Foreign keys become relationships. A column like account.address_id pointing to addresses.id becomes a REGISTERED_AT relationship between the Account node and the Address node. This is the most straightforward mapping: the foreign key that required a JOIN in SQL is now a direct traversal.

Mapping tables dissolve into relationships. A junction table like account_devices doesn't become nodes — the entire table disappears. Each row becomes a USED_DEVICE relationship, with the mapping table's own columns (first_seen, last_seen) as relationship properties. The many-to-many join that required a three-table query in SQL is now a single traversal.

Shared attribute values surface implicit connections. Two accounts with the same SSN have no foreign key between them. Discovering that link in the lakehouse requires a self-join. In the graph, SSN becomes a shared node and both accounts connect to it — the hidden connection is now explicit and traversable without any join. This is often the highest-value mapping because it reveals hidden networks that were invisible in the tabular model.

Self-referential columns become relationship chains. from_account and to_account in the transactions table point to two entities in the same table. In the graph this becomes an Account-to-Account TRANSFERRED_TO relationship. Chains of these are natural traversals in the graph but require recursive CTEs with cycle-detection guards in SQL.

The value compounds as you move down the list. Foreign keys are simple one-hop lookups. Mapping tables eliminate multi-table joins. Shared attributes reveal hidden networks. Self-referential chains replace recursive CTEs. The further down you go, the more the graph pays off relative to SQL.

The practical test: if you'd need three or more self-joins to answer a question, that data probably belongs in the graph. If you're counting, summing, or averaging, it stays in the lakehouse.

---

## Slide: ELT: Lakehouse to Graph

_Section title slide — no speaker notes._

---

## Slide: From Raw Data to Governed Delta Tables

Raw data lands in cloud storage: S3, Azure Data Lake Storage Gen2, or GCS. This is the unprocessed landing zone, not a governed catalog yet.

Databricks processes that raw data into Delta tables. The processing layer is Jobs, Notebooks, or Spark Declarative Pipelines (formerly Delta Live Tables). Auto Loader can incrementally detect and process new files as they arrive.

Delta Lake provides the governance layer: schema enforcement catches malformed account IDs and invalid amounts here, not during the graph load. Column renaming happens at this stage too. Customer_ID becomes account_id, Txn_Amount becomes amount, so graph properties are clean without extra transformation downstream.

Time travel enables recovery from bad loads. If a pipeline run corrupts data, you roll back to the previous version rather than re-ingesting from scratch.

The key point: Delta tables are the interchange format. The Neo4j Spark Connector reads from these governed tables. Everything upstream of this slide is Databricks territory. Everything downstream is the Spark Connector projecting connections into the graph.

---

## Slide: The Neo4j Spark Connector

_No speaker notes._

---

## Slide: Loading the Graph

Each row in the accounts Delta table becomes an Account node. Batched upserts create if new or update if existing, so the load is idempotent. Relationships come second because both endpoints must exist before the connector can match them.

The connector matches existing Account nodes by property values and creates TRANSFERRED_TO connections between them. Transaction details ride on the relationship itself: amount, timestamp, and channel are stored directly on the edge. No separate edge table, no foreign key resolution at query time.

---

## Slide: Design Decision: Relationship Types vs. Properties

The fraud example uses a single relationship type (TRANSFERRED_TO) with transaction details as properties. In other domains you may face the choice between multiple relationship types or a generic type with a property.

Type per connection means each kind of link gets its own relationship type. Neo4j indexes relationship types, so type-based lookups are fast. The tradeoff is a larger type vocabulary to manage.

Generic with property uses a single relationship type and distinguishes via a property value. Simpler schema, but property filters are slower than type lookups at query time.

Default to type per connection when your traversals need to follow specific connection types. Neo4j relationships are directional, so bidirectional flows like transfers require writing in both directions.

---

## Slide: Validation Through Spark Reads

The connector reads from Neo4j just as easily as it writes. Cypher results come back as standard DataFrames, so validation runs in the same Spark environment that built the graph.

Three checks cover the common failure modes. Node counts should match source row counts exactly. Relationship counts should fall within expected ranges for the transaction volume. High-connectivity nodes should reflect known characteristics from the source data, like high-volume accounts with expected transfer counts.

If counts don't match, the most common causes are failed node loads or key value mismatches between DataFrame columns and node properties. The connector silently drops relationships when the MATCH clause can't find the target node.

---

## Slide: Graph Insights Flow Back to the Lakehouse

Graph intelligence flows back as standard DataFrames. Graph-derived metrics become columns in Delta Gold tables, available for dashboards, ML features, and downstream analytics.

Cycle detection identifies accounts involved in circular transaction chains and writes a flag to the fraud alerts table. PageRank scores influential accounts based on transaction flow patterns, producing a risk-scoring column for investigation prioritization. Louvain community detection clusters tightly connected accounts into groups for fraud ring identification. Degree centrality counts how many counterparties an account transacts with, feeding fraud-prediction ML models.

Once in Delta Lake, these insights join with operational data like account histories that never left the lakehouse. This is the Gold layer in action: graph intelligence enriching data intelligence.

---

## Slide: Foundation for Data Intelligence Meets Graph Intelligence

We've walked through the full data pipeline. Raw data landed in Bronze, got cleaned and governed in Silver, and the Spark Connector projected connection data into Neo4j. Graph algorithm results flow back as columns in Gold tables: fraud alerts, risk scores, ML features.

That's the initial Medallion Architecture end to end. Delta Lake governs the data, Neo4j reveals the connections, and the Spark Connector bridges both directions.

So far we've only loaded structured, tabular data. The foundation handles rows and columns well, but the graph can hold more than that. The next stage adds unstructured knowledge: AML policy documents, maintenance manuals, regulatory text. Knowledge Graph Construction chunks those documents, extracts entities, generates embeddings, and writes them into the graph. That's where we're headed next.

---

## Slide: Appendix: Implementation Details

_Section title slide — no speaker notes._

---

## Slide: Debugging: When Relationships Fail to Create

_No speaker notes — content is on the slide itself._

---

## Slide: Appendix: Graph vs. SQL Decision Framework

_Section title slide — no speaker notes._

---

## Slide: When to Query the Graph vs. Stay in the Lakehouse

_No speaker notes — content is on the slide itself._

---

## Slide: Decision Table: SQL vs. Cypher

_No speaker notes — content is on the slide itself._

---

## Slide: Appendix: Cypher vs. SQL Side-by-Side

_Section title slide — no speaker notes._

---

## Slide: The Same Question, Two Languages

_No speaker notes — content is on the slide itself._

---

## Slide: The Same Question in Cypher

_No speaker notes — content is on the slide itself._

---

## Slide: Appendix: Schema Shift — Fraud Edition

_Section title slide — no speaker notes._

---

## Slide: From Transaction Tables to a Fraud Graph

_No speaker notes — content is on the slide itself._

---

## Slide: Modeling Decisions That Matter

_No speaker notes — content is on the slide itself._

---

## Slide: Appendix: Other Fraud Patterns the Graph Enables

_Section title slide — no speaker notes._

---

## Slide: Synthetic Identity Fraud

_No speaker notes — content is on the slide itself._

---

## Slide: First-Party Fraud Rings

_No speaker notes — content is on the slide itself._

---

## Slide: Bust-Out Fraud

_No speaker notes — content is on the slide itself._
