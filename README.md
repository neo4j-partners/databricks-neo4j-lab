# Build Generative AI & GraphRAG Agents with Neo4j and Databricks

A hands-on workshop for building explainable, context-aware AI applications using Neo4j's graph database platform and Databricks AI/ML capabilities.

## Workshop Overview

This workshop equips participants with practical skills to combine Neo4j's knowledge graphs with Databricks Foundation Models to build GraphRAG and agentic applications.

Participants work with a real-world dataset—SEC 10-K financial filings—to experience how knowledge graphs enhance AI applications with structured context and relationship-aware retrieval.

### What You'll Learn

- Deploy and explore Neo4j Aura, the fully managed cloud graph platform
- Build no-code AI agents with Neo4j Aura Agents
- Implement GraphRAG pipelines using the neo4j-graphrag Python library
- Create multi-agent systems with Databricks AgentBricks
- Invoke Aura Agents programmatically via REST API

## Lab Agenda

### Part 1 - No-Code Getting Started (Beginner Friendly)

| Lab | Description | Time |
|-----|-------------|------|
| [Lab 0 - Sign In](./Lab_0_Sign_In) | Sign into AWS Console and workshop environment | 10 min |
| [Lab 1 - Neo4j Aura Setup](./Lab_1_Aura_Setup) | Provision Neo4j Aura, restore the SEC 10-K knowledge graph, and explore relationships visually | 20 min |
| [Lab 2 - Aura Agents](./Lab_2_Aura_Agents) | Create a no-code AI agent with semantic search and Text2Cypher tools | 30 min |

### Part 2 - GraphRAG with Neo4j (Intermediate)

| Lab | Description | Time |
|-----|-------------|------|
| [Lab 4 - GraphRAG with Neo4j](./Lab_4_GraphRAG) | Build GraphRAG pipelines using neo4j-graphrag with Databricks Foundation Models | 45 min |
| [Lab 5 - AgentBricks Multi-Agent](./Lab_5_AgentBricks) | Create multi-agent systems with Databricks Genie and external MCP servers | 75 min |

### Part 3 - Advanced GraphRAG and Agents (Advanced)

> **Note:** This part of the workshop is designed for all-day sessions or as advanced material that participants can take home and complete on their own infrastructure. It builds on the skills from Parts 1 and 2 and is ideal for those who want to dive deeper into production integration patterns.

| Lab | Description | Time |
|-----|-------------|------|
| [Lab 6 - Advanced RAG](./Lab_6_Advanced_RAG) | Learn Text2Cypher retrieval and automated entity extraction | 45 min |
| [Lab 10 - Aura Agents API](./Lab_10_Aura_Agents_API) | Programmatically invoke Aura Agents via REST API with OAuth2 authentication | 30 min |

## Prerequisites

- AWS account (provided for workshops)
- Neo4j Aura account (SSO or free trial)
- Databricks workspace with Model Serving enabled

## Knowledge Graph Schema

The SEC 10-K filings knowledge graph contains:

```
(AssetManager)-[:OWNS]->(Company)-[:FACES_RISK]->(RiskFactor)
                            |
                            +-[:FILED]->(Document)-[:FROM_DOCUMENT]<-(Chunk)
                            |
                            +-[:HAS_EXECUTIVE]->(Executive)
                            |
                            +-[:PRODUCES]->(Product)
```

**Node Types:** Company, RiskFactor, Document, Chunk, AssetManager, Executive, Product

**Sample Companies:** Apple, Microsoft, NVIDIA, and other major corporations

## Technology Stack

| Component | Technology |
|-----------|------------|
| Graph Database | Neo4j Aura |
| Embeddings | Databricks GTE (databricks-gte-large-en) |
| LLM | Databricks Llama 3.3 70B |
| Vector Search | Neo4j Vector Index |
| Multi-Agent | Databricks AgentBricks |
| MCP Server | Neo4j MCP on Azure Container Apps |

## Configuration

Create a `CONFIG.txt` file in the project root with your credentials:

```ini
# Neo4j Aura
NEO4J_URI=neo4j+s://xxxxxxxx.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password_here

# Databricks Model Serving
DATABRICKS_HOST=https://your-workspace.cloud.databricks.com
DATABRICKS_TOKEN=dapi-your-token-here
```

## Resources

### Neo4j
- [Neo4j Aura Documentation](https://neo4j.com/docs/aura/)
- [neo4j-graphrag Python Library](https://neo4j.com/docs/neo4j-graphrag-python/)
- [Neo4j MCP Server](https://github.com/neo4j/mcp)
- [Cypher Query Language](https://neo4j.com/docs/cypher-manual/current/)

### Databricks
- [Foundation Model APIs](https://docs.databricks.com/aws/en/machine-learning/foundation-model-apis/)
- [AI/BI Genie](https://docs.databricks.com/aws/en/genie/)
- [AgentBricks Multi-Agent Supervisor](https://docs.databricks.com/aws/en/generative-ai/agent-bricks/multi-agent-supervisor)

## Feedback

We appreciate your feedback! Please open an issue on the [GitHub repository](https://github.com/neo4j-partners/databricks-neo4j-lab/issues) for bugs, suggestions, or comments.
