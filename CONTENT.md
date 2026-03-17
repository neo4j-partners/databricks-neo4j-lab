# Building the Intelligence Platform

Data Intelligence Meets Graph Intelligence

## Databricks and Neo4j: Better Together

Databricks is the Data Intelligence Platform. It governs and analyzes structured, semi-structured, and unstructured data at scale. Neo4j is the Graph Intelligence Platform. It makes connections between entities explicit and traversable. Together they form a complete intelligence platform: Databricks handles volume and governance, Neo4j handles topology and traversal.

The integration rests on four pillars: bi-directional data pipelines through the Databricks-certified Spark Connector, graph analytics that unlock hidden patterns at scale, GraphRAG retrieval that grounds AI responses in structured knowledge, and agent integration that lets AI systems query both platforms through natural language.

## Databricks: The Data Intelligence Platform

In this architecture, Databricks provides the governed data foundation. Delta Lake stores operational data as open lakehouse tables. Unity Catalog governs access across data and AI assets. Databricks SQL handles aggregation workloads at petabyte scale, including time-series analysis and fleet-wide statistical comparisons. AI/BI Genie translates natural language into governed SQL, and Agent Bricks hosts the multi-agent systems that coordinate queries across both platforms.

## Neo4j: The Graph Intelligence Platform

Neo4j stores the connections that flat tables obscure. Cypher queries traverse multi-hop relationships in milliseconds, matching patterns across nodes and the edges connecting them. AuraDB runs the graph as a managed service. Graph Data Science provides algorithms like PageRank and community detection that write results back to the Lakehouse. GraphRAG combines vector search with graph traversal for enriched retrieval, and Aura Agent enables conversational interfaces built directly on the knowledge graph.

## The Medallion Architecture

Databricks organizes data through progressive refinement across three layers. Bronze is the raw landing zone: files arrive from cloud storage with no transformation. Silver is the curation layer: schema enforcement, type casting, and column renaming produce clean, governed tables. The Spark Connector reads from Silver tables and writes nodes and relationships into Neo4j. Gold is where all intelligence converges: graph algorithm results like cycle detection, PageRank, and community scores write back to Delta as columns in Gold tables, joining with operational data that never left the Lakehouse.

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

## Two Data Models, Two Query Languages

SQL and Cypher answer different shapes of questions. SQL handles aggregation over rows and columns, computing totals, averages, and distributions across large datasets. Cypher handles traversal across connection topologies, following variable-depth hops and matching patterns that span multiple relationship types.

Consider financial fraud detection as a concrete example. Money laundering moves funds through chains of accounts and back to the origin. Each individual transfer looks legitimate in isolation. The circular pattern is only visible when you follow the connections. Detecting the cycle in SQL requires recursive CTEs that self-join the transactions table at each hop. In Cypher, the same detection is a single pattern match.

Most real-world questions need both platforms working together.

| Question | Platform |
|----------|----------|
| Total transfer volume by account | Databricks (SQL aggregation) |
| Accounts within three hops of a flagged account | Neo4j (graph traversal) |
| Find the fraud ring, compute its total volume | Both |

The rule of thumb: counting things stays in SQL. Following connections moves to the graph.

## Workshop Roadmap

The five labs progress from foundational setup through increasingly sophisticated AI patterns.

**Lab 1: Neo4j Aura Setup.** Stand up a Neo4j Aura instance and load the aircraft digital twin graph. Explore the topology with Cypher: aircraft, systems, components, sensors, flights, maintenance events, and the relationships connecting them.

**Lab 2: Databricks ETL.** Use the Neo4j Spark Connector to move data from Databricks Lakehouse tables into the knowledge graph. What was implicit in foreign keys and table joins becomes explicit, traversable structure in Neo4j.

**Lab 3: GraphRAG Semantic Search.** Chunk maintenance manuals, generate embeddings, and store them as graph-connected nodes in Neo4j. Vector search finds relevant text; graph traversal enriches results with the aircraft, systems, and components each document describes.

**Lab 4: Compound AI Agents.** Build a multi-agent system with a Supervisor Agent that routes questions to specialized sub-agents. A Genie space agent handles numeric aggregations and time-series queries over Lakehouse tables via natural language to SQL. A Neo4j MCP agent handles relationship traversals and structural queries over the knowledge graph via Cypher. The supervisor decides where each question belongs, or calls both agents in sequence when a question spans both domains.

**Lab 5: Aura Agents.** Use Neo4j's Create with AI capability to build graph-native agents directly within Aura.
