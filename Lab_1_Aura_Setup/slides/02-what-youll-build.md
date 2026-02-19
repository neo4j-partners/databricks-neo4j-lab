# What You'll Build

## The Knowledge Graph

Your database will contain an Aircraft Digital Twin dataset:

| Entity Type | Examples |
|-------------|----------|
| **Aircraft** | Boeing 737-800, Airbus A320/A321, Embraer E190 |
| **Systems** | Engines, Avionics, Hydraulics |
| **Components** | Turbines, Compressors, Pumps |
| **Flights** | Flight operations with departure/arrival |
| **Maintenance Events** | Fault tracking with severity |

## Relationships

```
(Aircraft)-[:HAS_SYSTEM]->(System)-[:HAS_COMPONENT]->(Component)
(Aircraft)-[:OPERATES_FLIGHT]->(Flight)-[:DEPARTS_FROM]->(Airport)
(Component)-[:HAS_EVENT]->(MaintenanceEvent)
```

---

[← Previous](01-intro.md) | [Next: Why Graph Databases? →](03-why-graphs.md)
