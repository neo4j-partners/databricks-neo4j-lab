# Workshop Slides

This folder contains presentation-ready slides extracted from the workshop lessons. All slides are formatted for [Marp](https://marp.app/), a markdown presentation tool.

## 📖 Participant Reference Docs

Condensed reference documents combining multiple slide decks into single-page markdown for easy review.

| Document | Covers |
|----------|--------|
| [Overview & GenAI Foundations](docs/overview-and-genai-foundations.md) | Workshop overview, digital twins, GenAI limitations, traditional RAG, Context ROT, and the GraphRAG solution |
| [Building Knowledge Graphs](docs/building-knowledge-graphs.md) | GraphRAG pipeline, schema design, chunking strategies, entity resolution, and vectors/semantic search |

---

## 📊 Available Presentations

All slides are organized by lab module for easy navigation.

### Lab 1: Neo4j Aura & Aura Agents (Slides 1-6) 🆕

**01. Neo4j Aura Overview** (3.5 KB) 🆕
   - What is Neo4j Aura
   - Cloud Graph Database Benefits
   - Value for AI/GenAI Applications
   - Getting Started

**02. The GenAI Promise and Its Limits** (4.2 KB) 🆕
   - What Generative AI Does Well
   - The Three Core Limitations
   - Hallucination, Knowledge Cutoff, Relationship Blindness
   - The Solution: Providing Context

**03. Traditional RAG: Chunking and Vector Search** (5.5 KB) 🆕
   - How Traditional RAG Works
   - Why Chunking Matters
   - Common Chunking Strategies
   - What is a Vector / What are Embeddings
   - The Smart Librarian Analogy
   - Without Vectors vs With Vectors
   - Similarity Search

**04. Context and the Limits of Traditional RAG** (4.5 KB) 🆕
   - The Power of Context
   - The Problem with Traditional RAG
   - What Traditional RAG Misses
   - Questions RAG Can't Answer
   - The GraphRAG Solution

**05. The SEC Filings Knowledge Graph** (3.5 KB) 🆕
   - SEC 10-K Filings Example
   - From PDF to Graph
   - What the Graph Enables
   - Your Pre-Built Knowledge Graph
   - Processing Pipeline Preview

**06. Aura Agents** (6.5 KB) 🆕
   - No-Code GraphRAG Platform
   - Three-Tool Architecture (Cypher Templates, Similarity Search, Text2Cypher)
   - Tool Selection and Reasoning
   - Agent Configuration
   - Testing and Deployment
   - Bridge to Code-Based Implementation

### Lab 2: Microsoft Foundry & MCP (Slides 1-3)

**01. What is an AI Agent** (4.0 KB)
   - Evolution of AI Assistants
   - Agent Components (Perception, Reasoning, Action, Response)
   - Tools and How Agents Choose Them
   - The ReAct Pattern
   - Multi-Tool Examples

**02. What is MCP (Model Context Protocol)** (3.5 KB)
   - The Tool Integration Problem
   - MCP as "USB for AI Tools"
   - MCP Architecture (Host, Client, Server)
   - Neo4j MCP Server
   - Benefits of Standardization

**03. Microsoft Foundry** (5.0 KB)
   - Evolution: Azure AI Studio → Microsoft Foundry
   - Foundry by the Numbers (11,000+ models, 1,400+ connectors)
   - Key Components (Foundry Models, Model Router, Agent Service, Foundry IQ)
   - MCP Tool Catalogue
   - Enterprise Governance (Control Plane)

### Lab 5: Building Knowledge Graphs (Slides 1-7)

**01. The GenAI Promise and Its Limits** (4.2 KB)
   - What Generative AI Does Well
   - The Three Core Limitations
   - Hallucination, Knowledge Cutoff, Relationship Blindness
   - The Solution: Providing Context

**02. Context and RAG** (4.5 KB)
   - Importance of Context
   - Retrieval Augmented Generation (RAG)
   - How RAG Works
   - The Problem with Traditional RAG
   - The GraphRAG Solution

**03. Building Knowledge Graphs** (11 KB) ⭐ **Largest**
   - Complete GraphRAG Pipeline
   - EDGAR SEC Filings Processing
   - Entity Extraction
   - Schema-Driven Knowledge Graphs
   - Structured Data Integration

**04. Schema Design** (4.7 KB)
   - Schema Purpose & Benefits
   - Node and Relationship Definitions
   - Pattern Specifications
   - Iterative Schema Development
   - Balancing Flexibility and Structure

**05. Chunking Strategies** (5.1 KB)
   - Chunk Size Optimization
   - Large vs Small Chunk Trade-offs
   - FixedSizeSplitter Configuration
   - Chunk Overlap Strategies
   - Impact on Entity Extraction
   - Best Practices by Document Type

**06. Entity Resolution** (6.3 KB)
   - Entity Duplication Problem
   - Default Resolution Strategies
   - Post-Processing Resolvers (Spacy, FuzzyMatch)
   - Conservative vs Aggressive Resolution
   - Best Practices and Testing

**07. Vectors** (4.8 KB)
   - Vector Fundamentals
   - Embeddings & Similarity
   - Vector Search in Neo4j
   - Document Chunking

### Lab 7: GraphRAG Retrievers (Slides 1-4)

**01. Retrievers Overview** (5.2 KB)
   - What is GraphRAG?
   - Benefits of GraphRAG
   - Retriever Types Overview

**02. Vector Retriever** (6.0 KB)
   - Vector Retriever Fundamentals
   - How Vector Search Works (5-step process)
   - Components: Embedder, Vector Index, Similarity, Top-K
   - Configuration and Code Examples
   - Best Practices and Use Cases

**03. Vector + Cypher Retriever** (8.9 KB)
   - Hybrid Retrieval (Semantic + Graph)
   - Two-Step Process Explained
   - Custom Retrieval Query Patterns
   - OPTIONAL MATCH Usage
   - Advanced Traversals and Metadata

**04. Text2Cypher Retriever** (8.1 KB)
   - Natural Language to Cypher Conversion
   - Schema's Critical Role
   - LLM Query Generation Process
   - Modern Cypher Syntax Best Practices
   - Complex Query Handling

### Lab 7: Intelligent Agents (Slides 1-5)

**01. From Retrievers to Agents** (3.7 KB)
   - What are Agents?
   - Agents vs Retrievers
   - Agent Reasoning & Tools

**02. Microsoft Agent Framework** (3.6 KB)
   - Building Agents with Microsoft Agent Framework
   - AzureAIClient Setup
   - Schema Tools
   - Agent Architecture
   - Tool Definition as Python Functions

**03. Building Your Agent** (8.9 KB)
   - Single-Tool to Multi-Tool Progression
   - Schema Tool, Vector Tool, Text2Cypher Tool
   - How Agents Decide Which Tool to Use
   - Agent Instructions and Streaming

**04. Agent Design Patterns** (11.8 KB)
   - Tool Selection Process
   - Progressive Enhancement Pattern
   - Tool Specialization Principles
   - Design Patterns (Naming, Docstrings, Composition)
   - Anti-Patterns to Avoid
   - The GraphRAG "Sweet Spot" (3 Tools)

**05. Congratulations** (2.0 KB)
   - Workshop Summary
   - What You Built
   - Next Steps

## 🚀 How to Use These Slides

### Running Slides

Requires Node.js 22 LTS (`brew install node@22`) and a one-time `npm install` in this directory.

```bash
cd slides
/opt/homebrew/opt/node@22/bin/node ./node_modules/.bin/marp overview-databricks-neo4j --server
```

Opens at http://localhost:8080/. Replace `overview-databricks-neo4j` with any slide deck directory name.

## 📝 Slide Format

All slides use Marp markdown format:

```markdown
---
marp: true
theme: default
paginate: true
---

# Slide Title

Content here

---

# Next Slide

More content
```

### Features Included

✅ **Pagination** - Automatic slide numbering
✅ **Images** - All images linked to `../images/`
✅ **Code Blocks** - Syntax-highlighted Cypher and Python
✅ **Tables** - Comparison and decision matrices
✅ **Two-Column Layouts** - Where appropriate
✅ **Consistent Styling** - Professional appearance

## 🎨 Customizing Theme

To use a different Marp theme, change the YAML frontmatter:

```markdown
---
marp: true
theme: gaia
paginate: true
backgroundColor: #fff
---
```

Available themes:
- `default` - Clean, professional
- `gaia` - Colorful, modern
- `uncover` - Minimalist, centered

Or create your own custom theme!

## 📊 Presentation Order

### For Full Workshop (5 hours):

**Part 1: GenAI Fundamentals (90 min)**
1. Slide 01: What is Generative AI (15 min)
2. Slide 02: LLM Limitations (15 min)
3. Slide 03: Context (10 min)
4. Slide 04: Building the Graph (20 min)
5. Slide 05: Schema Design (10 min)
6. Slide 06: Chunking Strategies (10 min)
7. Slide 07: Entity Resolution (10 min)

**Part 2: Vectors & Full Scale (40 min)**
8. Slide 08: Vectors (20 min)
9. Slide 09: Working with Full Datasets (20 min)

**Part 3: GraphRAG Retrievers (90 min)**
10. Slide 10: GraphRAG Explained (15 min)
11. Slide 11: What is a Retriever (15 min)
12. Slide 12: Vector Retriever (15 min)
13. Slide 13: Vector + Cypher Retriever (20 min)
14. Slide 14: Text2Cypher Retriever (15 min)
15. Slide 15: Choosing the Right Retriever (10 min)

**Part 4: Intelligent Agents (90 min)**
16. Slide 16: What is an Agent (10 min)
17. Slide 17: Microsoft Agent Framework (15 min)
18. Slide 18: Simple Schema Agent (15 min)
19. Slide 19: Vector Graph Agent (15 min)
20. Slide 20: Text2Cypher Agent (15 min)
21. Slide 21: Multi-Tool Agent Design (10 min)
22. Slide 22: Aura Agents (10 min)

### For Short Workshop (2.5 hours):

**Essential Slides:**
1. Slide 01: What is Generative AI (10 min)
2. Slide 02: LLM Limitations (10 min)
3. Slide 04: Building the Graph (15 min)
4. Slide 08: Vectors (15 min)
5. Slide 11: What is a Retriever (15 min)
6. Slide 15: Choosing the Right Retriever (10 min)
7. Slide 16: What is an Agent (10 min)
8. Slide 18: Simple Schema Agent (15 min)
9. Slide 21: Multi-Tool Agent Design (10 min)
10. Slide 22: Aura Agents (10 min)

### For Theory-Only Session (1.5 hours):

**Conceptual Overview:**
1. Slide 01: What is Generative AI (10 min)
2. Slide 02: LLM Limitations (10 min)
3. Slide 05: Schema Design (10 min)
4. Slide 08: Vectors (15 min)
5. Slide 10: GraphRAG Explained (10 min)
6. Slide 11: What is a Retriever (10 min)
7. Slide 15: Choosing the Right Retriever (10 min)
8. Slide 16: What is an Agent (10 min)
9. Slide 21: Multi-Tool Agent Design (10 min)

## 🖼️ Images

All slides reference images in the `../images/` directory. Make sure the images folder is at the same level as the graphacademy folder:

```
neo4j-and-azure-lab/
├── images/              ← Images here
└── graphacademy/
    └── slides/          ← Slides here
```

## 💡 Tips for Presenting

1. **Test beforehand** - Run through slides before presenting
2. **Use presenter mode** - Marp CLI has a presenter mode with notes
3. **Adjust timing** - Each slide deck has suggested duration
4. **Interactive demos** - Pause slides for hands-on exercises in labs
5. **Export PDFs** - Create backup PDFs in case of technical issues
6. **Know your audience** - Use short vs full workshop timing based on audience

## 🔧 Troubleshooting

**`require is not defined in ES module scope` error?**
- Marp CLI is incompatible with Node.js 25+. Install Node 22 LTS: `brew install node@22`

**Images not showing?**
- Use `--allow-local-files` flag with Marp CLI

## 📦 Export All Presentations

```bash
cd slides
for dir in overview-*/; do
  /opt/homebrew/opt/node@22/bin/node ./node_modules/.bin/marp "$dir" --pdf --allow-local-files
done
```

## 📚 Additional Resources

- [Marp Documentation](https://marpit.marp.app/)
- [Marp CLI Usage](https://github.com/marp-team/marp-cli)
- [Marp Themes](https://github.com/marp-team/marp-core/tree/main/themes)
- [Creating Custom Themes](https://marpit.marp.app/theme-css)
- [GraphAcademy Lessons](../README.md) - Corresponding lesson content

## 🎯 Quick Start

```bash
cd slides
/opt/homebrew/opt/node@22/bin/node ./node_modules/.bin/marp overview-databricks-neo4j --server
```

---

## 📈 Slide Statistics

**Total Presentations:** 25
**Total Slide Pages:** ~300 individual slides
**Format:** Marp Markdown
**Status:** ✅ Ready to present

### Lab Breakdown
- **Lab 1:** 6 presentations (Neo4j Aura, GenAI Limits, Traditional RAG, GraphRAG Limits, SEC Filings Graph, Aura Agents)
- **Lab 2:** 3 presentations (What is an Agent, MCP, Microsoft Foundry)
- **Lab 5:** 7 presentations (GenAI Fundamentals, Knowledge Graphs)
- **Lab 7:** 4 presentations (GraphRAG Retrievers)
- **Lab 7:** 5 presentations (Intelligent Agents)

### New Slides Added (December 3, 2025)
- 01: What is an AI Agent (lab-2-foundry)
- 02: What is MCP (lab-2-foundry)
- 03: Microsoft Foundry (lab-2-foundry)

**Latest Update:** Added Lab 2 slides covering AI Agents, MCP, and Microsoft Foundry
**Version:** 2.2 (December 3, 2025)
