# Content Plan: Enriching Labs with Slide Material

## Goal

Update the CONTENT.md files in Labs 1-5 with brief, high-level summaries drawing from the slide decks in `slides/`. Each CONTENT.md should be 1-2 pages — summarized, not exhaustive. The goal is to encapsulate the best of the slide material, not capture all of it. README.md files (step-by-step instructions) stay as-is.

Additionally, create a new **root-level CONTENT.md** for workshop-wide framing (GenAI limitations, workshop roadmap, Context ROT).

## Guiding Principles

- **1-2 pages per lab** — each lab is ~30 minutes hands-on, so the conceptual companion should be a quick read
- **Summarize, don't replicate** — distill slide content into key takeaways
- **Audience has graph background** — no need to explain graph fundamentals or domain-specific aircraft details
- **Each CONTENT.md opens with a "where you are" paragraph** connecting to the workshop arc: LLM limitations → RAG → GraphRAG → Agents

---

## New: Root-Level CONTENT.md

**Purpose:** Workshop-wide framing that sets up the "why" before participants touch anything.

**Source slides:**
- `overview-knowledge-graph/02-genai-and-limitations-slides.md` — LLM hallucination, knowledge cutoff, relationship blindness
- `overview-knowledge-graph/04-context-and-rag-slides.md` — Context ROT research finding
- `overview-databricks-neo4j/01-databricks-neo4j-integration-slides.md` — Databricks+Neo4j partnership overview, workshop roadmap

**Content to include:**
- GenAI limitations (hallucination, knowledge cutoff, relationship blindness) and how the workshop addresses each
- Context ROT finding — irrelevant context actively degrades LLM quality (highlight/callout)
- Workshop roadmap: Labs 1-5 arc from graph setup → ETL → GraphRAG → agents
- High-level Databricks+Neo4j partnership framing

---

## Lab-by-Lab Plan

### Lab 1: Aura Setup

**Current CONTENT.md covers:** Aircraft Digital Twin overview, why graphs, Aura basics, developer tools.

**Source slides:**
| Slide Deck | What to Pull |
|---|---|
| `overview-knowledge-graph/01-neo4j-aura-overview-slides.md` | Aura as managed service, built-in AI capabilities (vector indexes, graph traversal, Cypher), developer tools (Query Workspace, Explore, Dashboards) |

**Changes:**
- Keep existing content but tighten to 1-2 pages
- Remove graph algorithm descriptions (centrality, community detection, etc.) — participants don't use them
- GenAI limitations and "why this workshop" content moves to the root-level CONTENT.md
- Add brief "where you are" opener

---

### Lab 2: Databricks ETL to Neo4j

**Current CONTENT.md covers:** Databricks compute, notebooks, graph structure (core + extended), Spark Connector basics.

**Source slides:**
| Slide Deck | What to Pull |
|---|---|
| `databricks-in-depth/01-intro-databricks-neo4j-slides.md` | Medallion Architecture (Bronze/Silver/Gold), dual database strategy, SQL vs. Cypher side-by-side, fraud use case |
| `overview-databricks-neo4j/01-databricks-neo4j-integration-slides.md` | Building knowledge graphs from lakehouse data via Spark Connector |

**Changes:**
- Add **Medallion Architecture** overview (Bronze → Silver → Gold) — a key concept for understanding where data sits in the pipeline
- Add **Dual Database Architecture** section — high-level concept of how graph maps to lakehouse tables (as slides present it)
- Add **SQL vs. Cypher comparison** for a multi-hop query (the 3-hop side-by-side from slides)
- Include **fraud use case** alongside aircraft as background on different use cases for graph+lakehouse
- Keep high-level — audience has graph background, no need for domain-specific aircraft explanations

---

### Lab 3: Semantic Search

**Current CONTENT.md covers:** Knowledge graph structure, Document/Chunk model, embeddings, Databricks Foundation Model APIs, retrievers (Vector, VectorCypher), GraphRAG basics.

**Source slides (consolidated — do not expand each):**
| Slide Deck | What to Pull |
|---|---|
| `overview-knowledge-graph/03-traditional-rag-slides.md` | RAG workflow summary |
| `overview-knowledge-graph/05-building-knowledge-graphs-slides.md` | SimpleKGPipeline overview |
| `overview-knowledge-graph/06-schema-design-slides.md` | Three schema modes (brief) |
| `overview-knowledge-graph/07-chunking-slides.md` | Chunking trade-offs (brief) |
| `overview-knowledge-graph/08-entity-resolution-slides.md` | Entity resolution concept (very high level) |
| `overview-retrievers/01-retrievers-overview-slides.md` | Retriever decision framework |
| `overview-retrievers/02-vector-retriever-slides.md` | Vector retriever summary |
| `overview-retrievers/03-vector-cypher-retriever-slides.md` | "Chunk as anchor" concept |

**Changes:**
- Add brief **"From RAG to GraphRAG"** narrative — traditional RAG → its limits → GraphRAG solution (Context ROT detail lives in root-level doc)
- Add **schema design** mention — three modes, why the workshop uses User-Provided
- Add **chunking trade-offs** — larger vs. smaller chunks, one paragraph
- Add **entity resolution** at very high level — key part of building a graph for GraphRAG, connecting unstructured content to entities
- Add **retriever comparison** — Vector vs. VectorCypher decision framework (skip Text2Cypher — not used in Lab 3 notebooks)
- Consolidate existing content to stay within 1-2 pages

---

### Lab 4: Compound AI Agents

**Current CONTENT.md covers:** Why two data sources, Genie + Lakehouse, Neo4j for relationships, multi-agent supervisor, query routing, sensor domain knowledge, sample questions.

**Source slides:**
| Slide Deck | What to Pull |
|---|---|
| `overview-retrievers/08-from-retrievers-to-agents-slides.md` | Agent fundamentals (Perception → Reasoning → Action → Response), ReAct pattern |
| `databricks-in-depth/02-power-of-graphrag-slides.md` | MCP concept, Neo4j MCP tools, supervisor pattern |

**Changes:**
- **Lead with Agent Fundamentals and the ReAct pattern** — this should be how the section opens, drawing from the "from retrievers to agents" slides
- Add **Agent Bricks overview** — what Databricks Agent Bricks is, how it enables building and deploying multi-agent systems, and how it fits into the Databricks platform
- Add **MCP (Model Context Protocol) explanation** — what it is, why it matters, how Neo4j exposes tools through it
- **Remove sensor domain knowledge** from CONTENT.md (lines 57-92) — this is Genie configuration data, not conceptual background. It already exists in PART_A.md Step 4 as the instructions users paste into the Genie space. The CONTENT.md reference link from PART_A.md (line 92) will need to be updated or removed
- Skip deployment alternatives (MCP server vs. MLflow) — out of scope
- Keep multi-agent architecture overview, query routing strategy, sample questions
- Consolidate to 1-2 pages

**Action item:** Remove the sensor domain knowledge sections from CONTENT.md. Update the reference in PART_A.md line 92 (`See [CONTENT.md](CONTENT.md#aircraft-sensor-domain-knowledge) for an explanation of these values.`) — either remove this link or make the explanation self-contained in PART_A.

---

### Lab 5: Aura Agents

**Current CONTENT.md covers:** What Aura Agents are, "Create with AI" workflow, three tool types (Cypher Templates, Similarity Search, Text2Cypher), confabulation risk.

**Source slides:**
| Slide Deck | What to Pull |
|---|---|
| `overview-knowledge-graph/01-neo4j-aura-overview-slides.md` | Aura Agents within the broader Aura platform |

**Changes:**
- Keep it simple: just an overview of what Aura Agents are
- Current CONTENT.md is largely sufficient — trim to 1-2 pages if needed
- No Lab 4 vs. Lab 5 comparison, no security section, no tool decision framework, no MCP discussion

---

## Cross-Cutting Notes

### Slide content NOT being used
- Graph algorithms deep dive — skip
- Neo4j in Unity Catalog via JDBC federation — skip
- Text2Cypher retriever detail — skip (not in Lab 3 notebooks)
- Deployment alternatives — skip

### Fraud use case
The financial fraud use case from `databricks-in-depth/01` will be included in Lab 2 as a second example of graph+lakehouse use cases alongside aircraft.

### Reference docs in `slides/docs/`
The two condensed reference docs overlap with what we're adding. Use them as source material for summarizing; don't link to them from lab content.

---

## Remaining Question

1. **PART_A.md Genie instructions reference:** PART_A.md line 92 currently says `See [CONTENT.md](CONTENT.md#aircraft-sensor-domain-knowledge) for an explanation of these values.` Once we remove the sensor domain knowledge from CONTENT.md, should we:
   - (a) Remove this link entirely (the instructions are self-explanatory as-is), or
   - (b) Add a brief inline explanation in PART_A.md (e.g., a short paragraph before the instructions block explaining why these specific values matter for the Genie)?

---

## Deliverables Summary

| Deliverable | Action |
|---|---|
| Root-level `CONTENT.md` | **Create new** — workshop framing, GenAI limitations, Context ROT, roadmap |
| Lab 1 `CONTENT.md` | **Trim** — remove workshop-level content, tighten to 1-2 pages |
| Lab 2 `CONTENT.md` | **Enrich** — add Medallion Architecture, dual DB strategy, SQL/Cypher comparison, fraud use case |
| Lab 3 `CONTENT.md` | **Consolidate** — add RAG→GraphRAG narrative, schema/chunking/entity resolution summaries, retriever comparison |
| Lab 4 `CONTENT.md` | **Restructure** — lead with agents/ReAct, add Agent Bricks overview, add MCP explanation, remove sensor domain knowledge |
| Lab 4 `PART_A.md` | **Minor edit** — update or remove CONTENT.md reference link (line 92) |
| Lab 5 `CONTENT.md` | **Minor trim** — keep as simple Aura Agents overview, tighten if needed |
