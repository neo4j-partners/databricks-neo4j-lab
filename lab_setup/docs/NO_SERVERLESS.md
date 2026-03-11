# Why Serverless Compute Will Not Work

The primary way Neo4j integrates with Databricks is through the [Neo4j Spark Connector](https://neo4j.com/docs/spark/current/), which acts as a bidirectional bridge that maps Spark DataFrames to Neo4j graph queries for both reading and writing data. The connector requires a **Dedicated (Single User)** cluster. Serverless compute is incompatible for the following reasons:

- **Access mode mismatch** — Serverless compute runs in **Standard** access mode. The Neo4j Spark Connector only supports **Dedicated (Single User)** mode ([Neo4j Spark Connector docs](https://neo4j.com/docs/spark/current/databricks/)).
- **Not possible to install Neo4j Spark Connector** — The Neo4j Spark Connector must be installed as a Maven library (e.g., `org.neo4j:neo4j-connector-apache-spark_2.13:5.3.10_for_spark_3`), which serverless compute does not support.
- **No advanced cluster configuration** — Serverless does not expose settings like access mode, security mode, or single-user assignment that the workshop requires.

> **Note:** For quick prototyping, the [Neo4j Python driver](https://neo4j.com/docs/python-manual/current/) (`neo4j` pip package) can be installed on serverless compute. However, it does not support Spark DataFrame translation or the bidirectional DataSource API. Query results are returned as Python dictionaries, requiring custom mapping to DataFrames.
