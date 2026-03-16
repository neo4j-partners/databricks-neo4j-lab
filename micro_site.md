# Micro Site Proposal: Lab Walkthrough

## Open Questions

1. **Where do the lab notebooks live?** The actual notebooks are uploaded to `/Shared/databricks-neo4j-lab/` in the Databricks workspace. Should each lab page in the site tell participants what to do in those notebooks step by step, or are we writing the notebook content directly into the site as AsciiDoc? (i.e., is the site a companion guide that says "open notebook X and run cell Y" or is it self-contained?)

Don't link to the location  and just say run Lab_3_Databricks_ETL_Neo4j/01_aircraft_etl_to_neo4j.ipynb  ..... then run Lab_3_Databricks_ETL_Neo4j/02_load_neo4j_full.ipynb  etc.

2. **Lab 0 — keep or skip?** Lab 0 is just "sign in to Databricks and Neo4j." Should it be its own page or folded into the top of Lab 1 as a prerequisites section?

skip

3. **Left sidebar navigation.** The current site hides the left nav sidebar via CSS. With multiple lab pages, should we re-enable the sidebar so participants can jump between labs? Or keep the single-column layout and rely on a table of contents at the top of each page?


yes -renable

4. **Slides — where do they go?** The current site has three slide pages (Value Proposition, Architecture Deep Dive, GraphRAG). Should these stay as separate nav entries, get folded into the relevant lab pages as embedded content, or move to an appendix section?

separate nav enteries and the bottom 

5. **Screenshots and images.** Do we want screenshots of the Databricks UI, Neo4j Browser, and Genie space for each lab? If so, do those already exist somewhere or do they need to be captured?

Just use existing screenshots and images that are already in the readmes. and copy the images into the sites directory.

6. **Lab numbering.** The labs are numbered sequentially (Lab 1, Lab 3, Lab 4, Lab 5). The site should use the same numbering.

that was fixed. review and be sure it was done correctly.

7. **Neo4j Aura setup in Lab 1.** Is Neo4j Aura pre-provisioned by an admin for participants, or does each participant create their own instance? This changes how much detail Lab 1 needs.


Neo4j Aura is pre-provisioned and setup is out of scope for the site docs. 
---

## What We're Doing

Turning the site from a single landing page with embedded slides into a multi-page walkthrough that guides participants through every lab from start to finish. Each lab gets its own page. The participant opens the site, starts at Lab 1, and follows the pages in order.

## Proposed Site Structure

```
Home (landing page — trimmed-down version of the current index.adoc)
├── Lab 1: Neo4j Aura Setup
├── Lab 3: ETL with the Neo4j Spark Connector
│     ├── Notebook 1 — Core graph (aircraft, systems, components)
│     └── Notebook 2 — Full dataset (flights, airports, maintenance, delays)
├── Lab 4: GraphRAG Semantic Search
│     ├── Notebook 1 — Text chunking and embeddings
│     ├── Notebook 2 — Vector and full-text indexes
│     └── Notebook 3 — Entity extraction (operating limits)
├── Lab 5: Compound AI Agents
│     ├── Part 1 — Genie space for sensor analytics
│     ├── Part 2 — Neo4j MCP Agent
│     └── Part 3 — Supervisor Agent
└── Slides (appendix or folded into labs, depending on Q4 above)
```

## What Each Page Covers

**Home** — Short welcome, the dual-database problem statement, architecture diagram, and a "start Lab 1" link. Remove the detailed prerequisites and duration table from the current page — those details belong in the individual lab pages.

**Lab 1: Neo4j Aura Setup** — Walk through creating (or connecting to) a Neo4j Aura instance. Verify the connection. Briefly explore the empty graph. By the end, the participant has a running Neo4j instance and knows the URI, username, and password they'll use for the rest of the workshop.

**Lab 3: ETL with the Neo4j Spark Connector** — Explain the dual-database strategy (why some data goes to Neo4j and some to Databricks). Walk through the two notebooks: first the core aircraft/systems/components graph, then the full dataset (flights, airports, maintenance, delays, removals). Show what the graph looks like in Neo4j Browser after each notebook. Explain how the Spark Connector translates rows and foreign keys into nodes and relationships.

**Lab 4: GraphRAG Semantic Search** — Explain what GraphRAG adds on top of the structured graph. Walk through chunking maintenance manuals, generating embeddings, creating vector and full-text indexes, and extracting operating-limit entities. Show example semantic search queries and how the results trace back to source documents.

**Lab 5: Compound AI Agents** — Explain the multi-agent architecture. Walk through setting up the Genie space for SQL-based sensor analytics, configuring the Neo4j MCP agent (HTTP connection, OAuth2, MCP tools), and deploying the Supervisor Agent that routes between them. Show example questions and which agent handles each one.

## What Changes in the Repo

- **New AsciiDoc pages** under `site/modules/ROOT/pages/` — one per lab, plus possibly sub-pages for notebook breakdowns.
- **Updated `nav.adoc`** — new navigation tree with lab entries.
- **Updated `index.adoc`** — slimmed down to a landing page with links to labs.
- **Updated `site-extra.css`** — re-enable the left sidebar (if we go that direction per Q3).
- **New images** — screenshots and diagrams as needed (per Q5).
- No changes to `lab_setup/`, the CLI tools, or any Python code.
