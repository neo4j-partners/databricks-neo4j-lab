# Restructuring Plan (Final)

## Structure: 20 Slides

### Section 1: Building the Intelligence Platform (7 slides)

| # | Slide | Notes |
|---|-------|-------|
| 1 | Title: Databricks + Neo4j | Keep |
| 2 | Data Intelligence Meets Graph Intelligence | Keep |
| 3 | Databricks: The Data Intelligence Platform | Keep |
| 4 | Neo4j: The Graph Intelligence Platform | Keep |
| — | `# Building the Intelligence Platform` (transition) | Moved here |
| 5 | The Intelligence Platform | Moved up |
| 6 | Connection Patterns by Platform Stage | Moved up |
| 7 | The Medallion Architecture | Moved up |

### Section 2: Lakehouse X Graph (5 slides)

| # | Slide | Notes |
|---|-------|-------|
| — | `# Lakehouse X Graph` (transition) | New |
| 8 | Financial Fraud as a Working Example | Modified: remove Cypher/SQL bullets |
| 9 | Fraud Ring — Dual Database Architecture | Keep (image) |
| 10 | Neo4j Graph Components | Moved from Act 1 |
| 11 | Different Data, Different Query Patterns | Modified: add Cypher/SQL bullets |
| 12 | From the Lakehouse to the Graph | New: merged Mapping + Tables Become Graphs |

### Section 3: ELT: Lakehouse to Graph (8 slides)

| # | Slide | Notes |
|---|-------|-------|
| — | `# ELT: Lakehouse to Graph` (transition) | Keep |
| 13 | From Raw Data to Governed Delta Tables | Keep |
| 14 | The Neo4j Spark Connector | Keep |
| 15 | Loading the Graph | Keep |
| 16 | Design Decision: Relationship Types vs. Properties | Keep |
| 17 | Validation Through Spark Reads | Keep |
| 18 | Graph Insights Flow Back to the Lakehouse | Keep |
| 19 | The Foundation is in Place | Merged with Building on the Foundation |

### Removed

| Slide | Reason |
|-------|--------|
| Extracting Connection Data from the Lakehouse | Redundant with new "From the Lakehouse to the Graph" |
| Building on the Foundation | Merged into "The Foundation is in Place" |
| Appendix: Design Decision (table version) | Duplicate of main deck bullet version |

### Other fixes

- "Tables Become Graphs" column header: "Knowledge Graph (Neo4j)" → "Graph (Neo4j)" (absorbed into combined slide)
- Duplicate "implicit joins become explicit" removed (absorbed into combined slide)
