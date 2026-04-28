Flights connect airports through intermediate Flight nodes — there are no direct Airport-to-Airport relationships in the base graph. The Cypher aggregation projection builds a virtual weighted Airport graph, where edge weight equals the number of flights on each route.

### Explore airport traffic before projecting

```sql
MATCH (f:Flight)-[:DEPARTS_FROM]->(ap:Airport)
WITH ap, count(f) AS Departures
OPTIONAL MATCH (f2:Flight)-[:ARRIVES_AT]->(ap)
RETURN ap.iata     AS IATA,
       ap.city     AS City,
       Departures,
       count(f2)   AS Arrivals
ORDER BY Departures DESC
```

> **Concepts**: `OPTIONAL MATCH` keeps airports with zero arrivals. This gives a traffic baseline before running centrality — useful to know whether algorithm rankings align with raw volume.

### Top routes by flight frequency

```sql
MATCH (f:Flight)-[:DEPARTS_FROM]->(dep:Airport),
      (f)-[:ARRIVES_AT]->(arr:Airport)
RETURN dep.iata AS Origin,
       arr.iata AS Destination,
       count(f) AS Flights
ORDER BY Flights DESC
LIMIT 15
```

> **Concepts**: Identifies the highest-frequency routes — these will dominate the PageRank calculation because weight equals flight count.

### Build the weighted airport route projection (Cypher aggregation)

```sql
CALL gds.graph.drop('airport-routes', false) YIELD graphName;

MATCH (dep:Airport)<-[:DEPARTS_FROM]-(f:Flight)-[:ARRIVES_AT]->(arr:Airport)
WITH dep, arr, count(f) AS flight_count
RETURN gds.graph.project(
    'airport-routes',
    dep,
    arr,
    {
        sourceNodeLabels: ['Airport'],
        targetNodeLabels: ['Airport'],
        relationshipType: 'FLIES_TO',
        relationshipProperties: {weight: flight_count}
    },
    {undirectedRelationshipTypes: ['FLIES_TO']}
)
```

> **Concepts**: Cypher aggregation projection uses `RETURN gds.graph.project(...)` (a function, not a procedure). The `MATCH` pattern traverses through Flight nodes to build a virtual Airport-to-Airport graph. `undirectedRelationshipTypes: ['FLIES_TO']` treats every route bidirectionally — A→B and B→A are equivalent for centrality purposes.

### Stream PageRank — which airports are most influential?

```sql
CALL gds.pageRank.stream('airport-routes', {
    maxIterations: 20,
    dampingFactor: 0.85,
    relationshipWeightProperty: 'weight'
})
YIELD nodeId, score
WHERE score > 0
RETURN gds.util.asNode(nodeId).iata AS IATA,
       gds.util.asNode(nodeId).city AS City,
       round(score, 4)              AS PageRank
ORDER BY PageRank DESC
```

> **Concepts**: PageRank scores an airport by both the volume of connections and the importance of the airports it connects to. Importance is recursive: an airport gains a high score not just by having many routes, but by being connected to other high-scoring airports. A regional hub with direct routes to three major international hubs will outrank a spoke with routes to ten small regional airports — the quality of connections matters as much as the count. `relationshipWeightProperty: 'weight'` means high-frequency routes carry more influence than low-frequency ones, so a daily non-stop between two cities matters more than a once-weekly connection. `dampingFactor: 0.85` is the standard value (probability of following a link vs. jumping randomly).

### Write PageRank and Louvain community to Airport nodes

```sql
CALL gds.pageRank.write('airport-routes', {
    writeProperty: 'pagerank_score',
    maxIterations: 20,
    relationshipWeightProperty: 'weight'
})
YIELD nodePropertiesWritten;

CALL gds.louvain.write('airport-routes', {
    writeProperty: 'community_id',
    relationshipWeightProperty: 'weight'
})
YIELD communityCount, nodePropertiesWritten
```

> **Concepts**: `write` mode persists results as node properties, making them queryable from any Cypher client and visible in the graph visualization. Each statement runs sequentially using the same `airport-routes` projection.

### Airports ranked by PageRank with community (after write)

```sql
MATCH (ap:Airport)
WHERE ap.pagerank_score IS NOT NULL
RETURN ap.iata                     AS IATA,
       ap.city                     AS City,
       round(ap.pagerank_score, 4) AS PageRank,
       ap.community_id             AS Community
ORDER BY PageRank DESC
```

> **Concepts**: Once written, scores are plain node properties — queryable without any active projection. `IS NOT NULL` ensures only enriched Airport nodes appear.

### Maintenance delays departing from the top PageRank airport

```sql
MATCH (ap:Airport)
WHERE ap.pagerank_score IS NOT NULL
WITH ap ORDER BY ap.pagerank_score DESC LIMIT 1
MATCH (ap)<-[:DEPARTS_FROM]-(f:Flight)-[:HAS_DELAY]->(d:Delay {cause: 'Maintenance'})
RETURN ap.iata         AS Airport,
       ap.city         AS City,
       f.flight_number AS Flight,
       d.minutes       AS DelayMinutes
ORDER BY DelayMinutes DESC
LIMIT 20
```

> **Concepts**: Two-step pattern: first find the top airport by PageRank using `WITH ap ORDER BY ... LIMIT 1`, then traverse outward to flights with maintenance-caused delays. This joins graph topology (centrality) with operational data (delays) in a single Cypher query.
