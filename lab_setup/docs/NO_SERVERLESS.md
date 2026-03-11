# Why Serverless Compute Will Not Work

The primary way Neo4j integrates with Databricks is through the [Neo4j Spark Connector](https://neo4j.com/docs/spark/current/), which acts as a bidirectional bridge that maps Spark DataFrames to Neo4j graph queries for both reading and writing data. The connector requires a **Dedicated (Single User)** cluster. Serverless compute is incompatible for the following reasons:

- **Access mode mismatch** — Serverless compute runs in **Standard** access mode. The Neo4j Spark Connector only supports **Dedicated (Single User)** mode ([Neo4j Spark Connector docs](https://neo4j.com/docs/spark/current/databricks/)).
- **Not possible to install Neo4j Spark Connector** — The Neo4j Spark Connector must be installed as a Maven library (e.g., `org.neo4j:neo4j-connector-apache-spark_2.13:5.3.10_for_spark_3`), which serverless compute does not support.
- **No advanced cluster configuration** — Serverless does not expose settings like access mode, security mode, or single-user assignment that the workshop requires.

## Maven Coordinates and JAR Details

The Neo4j Spark Connector is installed as a Maven library with the following coordinates:

| Field | Value |
|-------|-------|
| **Group ID** | `org.neo4j` |
| **Artifact ID** | `neo4j-connector-apache-spark_2.13` |
| **Version** | `5.3.10_for_spark_3` |
| **Full coordinates** | `org.neo4j:neo4j-connector-apache-spark_2.13:5.3.10_for_spark_3` |

When Databricks resolves this Maven coordinate, it downloads the connector uber JAR and its transitive dependencies:

| JAR | Description |
|-----|-------------|
| `neo4j-connector-apache-spark_2.13-5.3.10_for_spark_3.jar` | Main connector — implements Spark DataSource V2 API for bidirectional Neo4j ↔ DataFrame translation |
| Neo4j Java Driver (`org.neo4j.driver:neo4j-java-driver`) | Bolt protocol driver bundled as a transitive dependency |

The `_2.13` suffix denotes **Scala 2.13** compatibility (matching Databricks Runtime 17.3 LTS ML), and `_for_spark_3` indicates **Spark 3.x/4.x** compatibility.

Serverless compute cannot install Maven libraries, which is why this connector — and by extension the entire Spark-based ETL workflow in Labs 5–6 — requires a Dedicated cluster.

> **Note:** For quick prototyping, the [Neo4j Python driver](https://neo4j.com/docs/python-manual/current/) (`neo4j` pip package) can be installed on serverless compute. However, it does not support Spark DataFrame translation or the bidirectional DataSource API. Query results are returned as Python dictionaries, requiring custom mapping to DataFrames.
