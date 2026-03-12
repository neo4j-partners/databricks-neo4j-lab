# Workshop Slides

Presentation-ready slides formatted for [Marp](https://marp.app/).

## Quick Start

Requires Node.js 22 LTS (`brew install node@22`) and a one-time `npm install` in this directory.

```bash
cd slides
/opt/homebrew/opt/node@22/bin/node ./node_modules/.bin/marp overview-databricks-neo4j --server
```

Opens at http://localhost:8080/. Replace `overview-databricks-neo4j` with any slide deck directory name.

## Export All Presentations

```bash
cd slides
for dir in overview-*/ databricks-*/; do
  /opt/homebrew/opt/node@22/bin/node ./node_modules/.bin/marp "$dir" --pdf --allow-local-files
done
```

## Troubleshooting

**`require is not defined in ES module scope` error?**
- Marp CLI is incompatible with Node.js 25+. Install Node 22 LTS: `brew install node@22`

**Images not showing?**
- Use `--allow-local-files` flag with Marp CLI

---

## Slide Decks

### `overview-databricks-neo4j/`
High-level introduction to the Databricks + Neo4j partnership — the dual-database architecture, why graphs complement lakehouse analytics, and the workshop roadmap.

### `databricks-in-depth/`
Deeper dive into the Databricks + Neo4j integration and the power of GraphRAG — how graph-enhanced retrieval goes beyond traditional RAG.

### `overview-knowledge-graph/`
End-to-end knowledge graph foundations — Neo4j Aura, GenAI limitations, traditional RAG, context and GraphRAG, building knowledge graphs from documents, schema design, chunking strategies, entity resolution, and vectors/semantic search.

### `overview-retrievers/`
GraphRAG retriever patterns — retriever overview, Vector Retriever, Vector + Cypher Retriever, Text2Cypher Retriever, and the bridge from retrievers to agents.

---

## Participant Reference Docs

Condensed reference documents combining multiple slide decks into single-page markdown for easy review.

| Document | Covers |
|----------|--------|
| [Overview & GenAI Foundations](docs/overview-and-genai-foundations.md) | Workshop overview, digital twins, GenAI limitations, traditional RAG, Context ROT, and the GraphRAG solution |
| [Building Knowledge Graphs](docs/building-knowledge-graphs.md) | GraphRAG pipeline, schema design, chunking strategies, entity resolution, and vectors/semantic search |

## Slide Format

All slides use Marp markdown format with pagination, syntax-highlighted code blocks, tables, and two-column layouts. See any slide file for the frontmatter template.

## Additional Resources

- [Marp Documentation](https://marpit.marp.app/)
- [Marp CLI Usage](https://github.com/marp-team/marp-cli)
- [Marp Themes](https://github.com/marp-team/marp-core/tree/main/themes)
- [Creating Custom Themes](https://marpit.marp.app/theme-css)
