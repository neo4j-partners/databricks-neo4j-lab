# Lab 1: Concepts and Reference

This is Lab 1 of 5. The graph database you provision here is the foundation for everything that follows: the ETL pipelines in Lab 2 load data into it, Lab 3 runs semantic search against its maintenance manuals, Lab 4 connects it to a multi-agent system, and Lab 5 builds a no-code conversational interface on top of it. Getting Aura running and understanding what the graph contains is the starting point.

## The Aircraft Digital Twin Graph

The workshop builds a knowledge graph representing aircraft digital twins. Five core entity types and the relationships between them capture the structure of an aircraft fleet, its operations, and its maintenance history:

| Entity Type | Examples |
|-------------|----------|
| **Aircraft** | Boeing 737-800, Airbus A320/A321, Embraer E190 |
| **Systems** | Engines, Avionics, Hydraulics |
| **Components** | Turbines, Compressors, Pumps |
| **Flights** | Flight operations with departure/arrival airports |
| **Maintenance Events** | Fault tracking with severity levels |

These entities connect through typed relationships that reflect real-world structure:

```
(Aircraft)-[:HAS_SYSTEM]->(System)-[:HAS_COMPONENT]->(Component)
(Aircraft)-[:OPERATES_FLIGHT]->(Flight)-[:DEPARTS_FROM]->(Airport)
(Component)-[:HAS_EVENT]->(MaintenanceEvent)
```

A question like "Which components caused flight delays for aircraft N95040A?" requires traversing from Aircraft through Flight to Delay, then back through MaintenanceEvent to Component. That multi-hop traversal is what a graph database handles natively, and what would require multiple JOINs in a relational system.

## Neo4j Aura

Neo4j Aura is a fully managed cloud graph database service. It provides the Neo4j graph engine without the operational overhead of running infrastructure: automatic backups, high availability, and deployment across AWS, GCP, and Azure. Each participant provisions their own Aura instance to hold the Aircraft Digital Twin graph. The data loaded in Lab 2 persists in this instance and is queried by notebooks in Labs 3 and 4.

Aura includes capabilities that support AI retrieval pipelines directly. Built-in vector indexes store embeddings alongside graph data, enabling semantic similarity search without a separate vector store. Cypher queries can combine vector search with graph traversal in a single operation, retrieving documents by semantic similarity and then following relationships to pull in structural context. These capabilities come together in Lab 3 (semantic search over maintenance manuals) and Lab 5 (Aura Agents).

## Aura Developer Tools

The Aura console provides three tools you will use throughout the workshop.

**Query Workspace** is a developer environment for writing and executing Cypher queries with syntax highlighting, auto-completion, and saved query collections. You will use this to verify data loads and explore results.

**Explore** (powered by Neo4j Bloom) provides visual graph exploration through an interactive canvas. Search for nodes by label or property, expand their relationships, and discover patterns visually. Natural language search translates questions into graph queries without writing Cypher.

**Dashboards** offer low-code data visualization including bar charts, geographic maps, and 3D graph visualizations for presenting graph data to non-technical stakeholders.
