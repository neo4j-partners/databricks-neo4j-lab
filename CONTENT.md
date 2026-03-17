# Building the Intelligence Platform

Data Intelligence Meets Graph Intelligence

## Databricks and Neo4j: Better Together

Databricks is the Data Intelligence Platform. It governs and analyzes structured, semi-structured, and unstructured data at scale. Neo4j is the Graph Intelligence Platform. It makes connections between entities explicit and traversable. Together they form a complete intelligence platform: Databricks handles volume and governance, Neo4j handles topology and traversal.

The integration rests on four pillars: bi-directional data pipelines through the Databricks-certified Spark Connector, graph analytics that surface patterns invisible in flat tables, GraphRAG retrieval that grounds AI responses in structured knowledge, and agent integration that lets AI systems query both platforms through natural language.

## Databricks: Volume and Governance

In this architecture, Databricks provides the governed data foundation. Delta Lake stores operational data as open lakehouse tables. Unity Catalog governs access across data and AI assets. Databricks SQL handles aggregation workloads at petabyte scale, including time-series analysis and fleet-wide statistical comparisons. The Lakehouse is the system of record and the analytical engine for everything that stays in rows and columns.

## Neo4j: Topology and Traversal

Neo4j makes the structural relationships between entities explicit and directly traversable. The graph captures how entities connect, what paths exist between them, and which communities form. Graph algorithm results write back to the Lakehouse as enrichment columns in Gold tables.

## From the Lakehouse to the Graph

Not everything moves to the graph. Aggregates, metrics, logs, and documents stay in Delta Lake where they belong. Only the subset with connection patterns worth traversing projects into Neo4j.

The mapping follows a consistent pattern. Rows become nodes, with columns as node properties. Foreign keys become relationships, and mapping tables dissolve into relationships with properties of their own. When two entities share an attribute value, that shared value becomes a node connecting them, making the implicit relationship explicit. Self-referential columns like from_account and to_account in a transactions table become traversable relationship chains.

The lakehouse remains the system of record. The graph is a projection of the connections that matter. The Medallion Architecture organizes how that projection happens in practice.

## The Medallion Architecture

Databricks organizes data through progressive refinement across three layers. Bronze is the raw landing zone, where files arrive from cloud storage with no transformation. Silver curates that raw data into governed tables through schema enforcement, type casting, and column renaming. The Spark Connector reads from Silver tables and writes nodes and relationships into Neo4j. Gold is where all intelligence converges. Graph algorithm results like cycle detection, PageRank, and community scores write back to Delta as columns in Gold tables, joining with operational data that never left the Lakehouse.

Data flows forward through the layers, graph insights flow back. Silver feeds the graph, Gold captures what the graph discovers.

## From Data Pipeline to Agents

Four stages connect Databricks to Neo4j, each building on the Medallion Architecture.

**ELT Data Pipeline.** Governed Silver Delta tables project into graph nodes and relationships via the Spark Connector. This is the primary path for bulk loading structured data.

**Knowledge Graph Construction.** Unstructured documents (maintenance manuals, regulatory text, policy documents) are chunked, embedded, and entity-extracted using the neo4j-graphrag-python SimpleKGPipeline. The results write into Neo4j as searchable chunks linked to extracted entities.

**Data Analytics.** Graph insights flow back to Gold Delta tables for dashboards and ML. The Spark Connector provides first-class GDS integration: PageRank, community detection, and other graph algorithms run directly and return results as DataFrames.

**GraphRAG Retrieval and Agents.** Agents query both platforms through vector search, Cypher, and SQL. The Neo4j MCP Server exposes schema inspection and read-only Cypher as agent tools. A multi-agent supervisor routes questions to the right specialist.

## Neo4j Connection Patterns by Platform Stage

Each stage uses a different connector optimized for its workload.

| Stage | Connector | Purpose |
|-------|-----------|---------|
| Data Pipeline | Neo4j Spark Connector | Batch DataFrame writes into Neo4j |
| Knowledge Graph Construction | neo4j-graphrag-python (Python driver) | Chunking, entity extraction, embedding generation |
| Data Analytics | Spark Connector + Unity Catalog JDBC | GDS algorithm results as DataFrames; governed SQL via JDBC |
| GraphRAG Retrieval / Agent | Neo4j MCP Server + Python driver | Schema inspection, read-only Cypher, vector search |

## The Data Intelligence Platform

Databricks processes transactions, sensor streams, and clickstreams at petabyte scale. Databricks SQL handles aggregation workloads, from simple totals and averages to time-series analysis and fleet-wide statistical comparisons. Unity Catalog provides unified governance across data and AI assets. Delta Lake provides the open storage layer with schema enforcement and ACID transactions.

The AI stack builds on the governed foundation. AI/BI Genie translates natural language into governed SQL for conversational analytics. Mosaic AI provides model training and serving. Agent Bricks hosts compound AI systems that coordinate queries across multiple data sources.

## The Graph Intelligence Platform

Cypher, the graph query language, matches patterns across nodes and relationships. A multi-hop traversal that follows three relationship types is a single query, not a chain of JOINs. Pattern matching extends to variable-length paths, shortest path computation, and subgraph detection.

AuraDB provides the managed cloud runtime. Graph Data Science adds algorithmic capabilities: PageRank scores influence, community detection clusters tightly connected groups, and similarity algorithms surface hidden connections. GraphRAG layers vector search on top of graph traversal, combining semantic similarity with structural context in a single retrieval step. Aura Agent turns the knowledge graph into a conversational interface.

## Data Intelligence, Graph Intelligence, or Both?

Each platform answers a different shape of question. SQL handles aggregation, computing totals, averages, and distributions across large datasets. Cypher handles traversal, following variable-depth hops and matching patterns across multiple relationship types.

| Question | Platform |
|----------|----------|
| Total transfer volume by account | Databricks (SQL aggregation) |
| Accounts within three hops of a flagged account | Neo4j (graph traversal) |
| Find the fraud ring, compute its total volume | Both |

The rule of thumb: counting things stays in SQL. Following connections moves to the graph. Most real-world questions need both platforms working together.

## Workshop Roadmap

The five labs progress from foundational setup through increasingly sophisticated AI patterns.

**Lab 1: Neo4j Aura Setup.** Stand up a Neo4j Aura instance and load the aircraft digital twin graph. Explore the topology with Cypher: aircraft, systems, components, sensors, flights, maintenance events, and the relationships connecting them.

**Lab 2: Databricks ETL.** Use the Neo4j Spark Connector to move data from Databricks Lakehouse tables into the knowledge graph. What was implicit in foreign keys and table joins becomes explicit, traversable structure in Neo4j.

**Lab 3: GraphRAG Semantic Search.** Chunk maintenance manuals, generate embeddings, and store them as graph-connected nodes in Neo4j. Vector search finds relevant text; graph traversal enriches results with the aircraft, systems, and components each document describes.

**Lab 4: Compound AI Agents.** Build a multi-agent system with a Supervisor Agent that routes questions to specialized sub-agents. A Genie space agent handles numeric aggregations and time-series queries over Lakehouse tables via natural language to SQL. A Neo4j MCP agent handles relationship traversals and structural queries over the knowledge graph via Cypher. The supervisor decides where each question belongs, or calls both agents in sequence when a question spans both domains.

**Lab 5: Aura Agents.** Use Neo4j's Create with AI capability to build graph-native agents directly within Aura.
