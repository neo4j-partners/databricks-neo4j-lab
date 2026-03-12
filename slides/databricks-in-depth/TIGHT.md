# Tightening the Deck for 30 Minutes

## Current Slide Count

**Main deck:** 24 slides (including 2 transition slides)
**Appendix:** 16 slides (not presented)

At ~1.5-2 minutes per slide, the main deck runs 36-48 minutes. Need to cut roughly 6-8 slides.

---

## Repetitiveness

### 1. "What stays, what moves" is said THREE times

The same idea (most data stays in Delta, connection data moves to the graph, foreign keys become relationships) appears on three separate slides:

| Slide | Key phrase |
|-------|-----------|
| **Mapping the Lakehouse to the Graph** (line 122) | "Most data stays in the lakehouse... Foreign keys become relationships" |
| **Tables Become Graphs** (line 130) | Table: FK → `TRANSFERRED_TO` relationship, JOIN → graph traversal |
| **Extracting Connection Data from the Lakehouse** (line 311) | "Most data stays in Delta... Foreign keys become relationships" |

Slides 1 and 3 are nearly identical in content. The audience hears the same point in Act 1, then again at the start of Act 3.

**Suggestion:** Cut "Extracting Connection Data from the Lakehouse" entirely. Its content was already established in Act 1. The ELT section can go straight from "Raw Data to Governed Delta Tables" into "The Neo4j Spark Connector."

### 2. "Foreign keys become relationships" appears three times

- Line 126 (Mapping the Lakehouse to the Graph)
- Line 138 (Tables Become Graphs)
- Line 315 (Extracting Connection Data)

Cutting the third slide (per above) fixes this. The remaining two are close together and serve different purposes (text vs. table), so they're acceptable.

### 3. "Implicit joins become explicit, traversable" appears twice

- Line 126: "implicit joins become explicit, traversable edges"
- Line 141: "What was implicit in table joins becomes explicit and traversable in the graph"

These are on adjacent slides (Mapping the Lakehouse to the Graph → Tables Become Graphs). One is enough.

### 4. Design Decision slide is duplicated

The bullet-point version now lives in the main deck (line 366). The original table version still sits in the appendix (line 496). Same content, two formats.

**Suggestion:** Remove the appendix copy. It was moved, not copied.

### 5. The Foundation is in Place + Building on the Foundation overlap

These two slides (lines 450-488) cover very similar ground:

| Slide | Content |
|-------|---------|
| **The Foundation is in Place** | Bronze landed, Silver fed connector, Gold has insights flowing back |
| **Building on the Foundation** | Governed data in Delta, connection data in graph, insights flowing both directions |

Both say "the pipeline is done, data flows both ways." The second adds the transition line to Knowledge Graph Construction.

**Suggestion:** Merge into one slide. The medallion recap + "Next: Knowledge Graph Construction" is one idea.

### 6. Medallion Architecture defined, then restated

- **The Medallion Architecture** (line 214): defines Bronze/Silver/Gold
- **The Foundation is in Place** (line 450): restates Bronze/Silver/Gold as completed

This is intentional (definition vs. recap), but with the slides far apart, the audience may not connect them. If the two foundation slides merge (per #5), this becomes less of an issue.

---

## Slides That Could Merge

### A. Mapping the Lakehouse to the Graph + Tables Become Graphs

Both explain the same concept (lakehouse concepts → graph concepts). The table on "Tables Become Graphs" is the stronger visual. "Mapping the Lakehouse to the Graph" could be absorbed into its speaker notes.

**Result:** 1 slide instead of 2.

### B. The Intelligence Platform + Connection Patterns by Platform Stage

Both walk through the same four stages. One shows the data flow arrows, the other shows the connectors. These could be a single slide with a two-column table: stage → flow → connector.

**Result:** 1 slide instead of 2.

### C. The Foundation is in Place + Building on the Foundation

Per #5 above.

**Result:** 1 slide instead of 2.

---

## Slides That Could Be Cut

### D. Neo4j Graph Components

This slide teaches Cypher notation (`(parentheses)` are nodes, `[:brackets]` are relationships). It's useful for a Cypher-naive audience but could move to the appendix if time is tight. The notation shows up naturally in later slides anyway.

### E. Extracting Connection Data from the Lakehouse

Per #1 above. Redundant with Act 1 slides.

---

## Potential Result

| Action | Slides saved |
|--------|-------------|
| Merge: Mapping + Tables Become Graphs | 1 |
| Merge: Intelligence Platform + Connection Patterns | 1 |
| Merge: Foundation is in Place + Building on the Foundation | 1 |
| Cut: Extracting Connection Data (redundant) | 1 |
| Cut: Neo4j Graph Components (move to appendix) | 1 |
| Remove: Appendix duplicate of Design Decision | 1 |

**Main deck after changes:** ~18-19 slides, which at 1.5 minutes each is ~28 minutes. Comfortable for 30 minutes with room for questions.

---

## Other Notes from IMPROVE.md

- "Tables Become Graphs" column header still says "Knowledge Graph (Neo4j)" but the fraud example is a transaction graph, not a knowledge graph. Should be "Graph (Neo4j)."
- The appendix Cypher vs. SQL side-by-side (lines 559-625) is strong reference material but the SQL block is 38 lines of code on a single slide, which is unreadable in a presentation. Fine as appendix/handout.
