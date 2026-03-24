# Lab 3: Sample Cypher Queries


Copy and paste these queries into the [Neo4j Aura Query interface](https://console.neo4j.io) to explore the Document-Chunk graph and semantic search capabilities built in this lab.

## Cypher Concepts Used

| Concept | What It Does |
|---|---|
| `MATCH (n:Label)` | Find nodes by label — the starting point for most queries |
| `(a)-[:REL]->(b)` | Traverse a relationship between two nodes (direction matters) |
| `OPTIONAL MATCH` | Like a SQL LEFT JOIN — keeps the row even if the pattern has no match |
| `RETURN ... AS alias` | Project properties and rename columns |
| `count()`, `collect()` | Aggregate functions — count rows or gather values into a list |
| `COALESCE(a, b)` | Returns the first non-null value — useful for handling missing optional matches |
| `substring(str, start, len)` | Extract part of a string — handy for previewing long text |
| `ORDER BY ... DESC` | Sort results (ascending by default) |
| `LIMIT n` | Cap the number of returned rows |
| `db.index.fulltext.queryNodes()` | Run a keyword search against a named fulltext index |
| `CALL { ... }` | Subquery block — used to scope intermediate results or call procedures |

---

## Document-Chunk Structure

### View all documents and their chunk counts

```sql
MATCH (d:Document)
OPTIONAL MATCH (d)<-[:FROM_DOCUMENT]-(c:Chunk)
RETURN d.documentId AS DocumentId,
       d.title AS Title,
       d.aircraftType AS AircraftType,
       count(c) AS ChunkCount
```

> **Concepts**: `OPTIONAL MATCH` keeps documents even if they have no chunks yet. `count()` aggregates the matched chunks per document.

### Browse the first few chunks of a document

```sql
MATCH (c:Chunk)-[:FROM_DOCUMENT]->(d:Document)
WHERE c.index IS NOT NULL
RETURN c.index AS ChunkIndex,
       substring(c.text, 0, 120) AS Preview,
       d.documentId AS Document
ORDER BY c.index
LIMIT 10
```

> **Concepts**: `substring()` truncates long text for readable output. `WHERE c.index IS NOT NULL` filters nulls before sorting — always required when using `ORDER BY`.

### Walk the chunk chain

```sql
MATCH (c:Chunk)-[:FROM_DOCUMENT]->(d:Document)
WHERE c.index IS NOT NULL
OPTIONAL MATCH (c)-[:NEXT_CHUNK]->(next:Chunk)
RETURN c.index AS ChunkIndex,
       substring(c.text, 0, 80) AS Preview,
       next.index AS NextChunkIndex
ORDER BY c.index
LIMIT 10
```

> **Concepts**: `OPTIONAL MATCH` on `NEXT_CHUNK` keeps the last chunk in the chain (which has no successor). `WHERE c.index IS NOT NULL` ensures clean sorting. This shows the linked-list structure that preserves reading order.

### Find the first and last chunks

```sql
MATCH (c:Chunk)-[:FROM_DOCUMENT]->(d:Document)
WHERE c.index IS NOT NULL
  AND (NOT EXISTS { (:Chunk)-[:NEXT_CHUNK]->(c) }
       OR NOT EXISTS { (c)-[:NEXT_CHUNK]->(:Chunk) })
RETURN c.index AS ChunkIndex,
       CASE
         WHEN NOT EXISTS { (:Chunk)-[:NEXT_CHUNK]->(c) } THEN 'FIRST'
         ELSE 'LAST'
       END AS Position,
       substring(c.text, 0, 100) AS Preview
ORDER BY c.index
```

> **Concepts**: `EXISTS { pattern }` checks whether a pattern exists in the graph. Negating it finds chain endpoints — the first chunk has no incoming `NEXT_CHUNK`, the last has no outgoing.

---

## Fulltext Keyword Search

> **Prerequisite:** These queries require the `maintenanceChunkText` fulltext index, created in notebook 03.

### Search for a specific term

```sql
CALL db.index.fulltext.queryNodes('maintenanceChunkText', 'V2500')
YIELD node, score
RETURN score,
       node.index AS ChunkIndex,
       substring(node.text, 0, 200) AS Content
ORDER BY score DESC
LIMIT 5
```

> **Concepts**: `db.index.fulltext.queryNodes()` performs keyword search using Lucene scoring. Exact term matches rank highest. Unlike vector search, this finds chunks containing the literal string "V2500".

### Search with multiple keywords

```sql
CALL db.index.fulltext.queryNodes('maintenanceChunkText', 'hydraulic pressure contamination')
YIELD node, score
RETURN score,
       node.index AS ChunkIndex,
       substring(node.text, 0, 200) AS Content
ORDER BY score DESC
LIMIT 5
```

> **Concepts**: Multiple keywords are OR'd together by default — chunks matching more keywords score higher. This is useful for domain-specific terminology where exact terms matter.

---

## Indexes and Schema

### List all indexes

```sql
SHOW INDEXES
```

> **Concepts**: Shows all indexes in the database including the `maintenanceChunkEmbeddings` vector index and `maintenanceChunkText` fulltext index created in notebook 03.

### Verify the fulltext index

```sql
SHOW INDEXES
YIELD name, type, labelsOrTypes, properties
WHERE type = 'FULLTEXT'
RETURN name, labelsOrTypes, properties
```

> **Concepts**: Filters to show only fulltext indexes. Confirms that the `maintenanceChunkText` index covers the `text` property on `Chunk` nodes.

### View the complete graph schema

```sql
CALL db.schema.visualization()
```

> **Concepts**: Introspects the database and returns every node label, relationship type, and how they connect. After Lab 3, you should see Document and Chunk nodes alongside the Aircraft topology from Lab 2.

