# Lab 1: Concepts and Reference

This is Lab 1 of 5. The graph database you provision here is the foundation for everything that follows: the ETL pipelines in Lab 2 load data into it, Lab 3 runs semantic search against its maintenance manuals, Lab 4 connects it to a multi-agent system, and Lab 5 builds a no-code conversational interface on top of it. Getting Aura running and understanding what the graph contains is the starting point.

## Graph Databases

A graph database models data as nodes and relationships. Nodes represent entities. Relationships represent the connections between them. Both carry properties, which are key-value pairs that describe their attributes.

The notation follows a visual convention. Parentheses denote nodes, brackets denote relationships:

```
(:Component {name, type})-[:HAS_EVENT {date, severity}]->(:MaintenanceEvent)
```

Each Component node carries properties like name and type. Each HAS_EVENT relationship carries details like date and severity. The relationship is directional, typed, and stored as a first-class element alongside the nodes it connects.

Where relational databases represent connections implicitly through foreign keys and join tables, graphs make them explicit and traversable. Questions that require following chains of connections become single traversal patterns rather than nested JOINs or recursive CTEs.

## Neo4j Aura

Neo4j Aura is a fully managed cloud graph database service. It provides the Neo4j graph engine without the operational overhead of running infrastructure: automatic backups, high availability, and deployment across AWS, GCP, and Azure. Each participant provisions their own Aura instance to hold the Aircraft Digital Twin graph. The data loaded in Lab 2 persists in this instance and is queried by notebooks in Labs 3 and 4.

Cypher is the query language for interacting with Neo4j. It uses a pattern-matching syntax that mirrors the visual structure of nodes and relationships, making graph queries readable as descriptions of the data they retrieve:

```cypher
MATCH (a:Aircraft)-[:HAS_SYSTEM]->(s:System)-[:HAS_COMPONENT]->(c:Component)
WHERE a.tail_number = 'N95040A'
RETURN s.name, c.name
```

The query reads like the pattern it matches: start at an Aircraft node, follow HAS_SYSTEM to a System, then HAS_COMPONENT to a Component. Cypher handles multi-hop traversals and path-finding operations natively.

Aura provides capabilities beyond the core graph engine that support AI retrieval pipelines directly. Built-in vector indexes store embeddings alongside graph data, enabling semantic similarity search without a separate vector store. Cypher queries can combine vector search with graph traversal in a single operation, retrieving documents by semantic similarity and then following relationships to pull in structural context. Graph Data Science algorithms like PageRank and community detection run directly within Aura for analytical workloads. These capabilities come together in Lab 3 (semantic search over maintenance manuals) and Lab 5 (Aura Agents).

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

A question like "Which components caused flight delays for aircraft N95040A?" requires traversing from Aircraft through Flight to Delay, then back through MaintenanceEvent to Component. That multi-hop traversal is what the graph handles natively.

## Aura Developer Tools

The Aura console provides three tools you will use throughout the workshop.

**Query Workspace** is a developer environment for writing and executing Cypher queries with syntax highlighting, auto-completion, and saved query collections. You will use this to verify data loads and explore results.

**Explore** (powered by Neo4j Bloom) provides visual graph exploration through an interactive canvas. Search for nodes by label or property, expand their relationships, and discover patterns visually. Natural language search translates questions into graph queries without writing Cypher.

**Dashboards** offer low-code data visualization including bar charts, geographic maps, and 3D graph visualizations for presenting graph data to non-technical stakeholders.
