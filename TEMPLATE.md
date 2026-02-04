# Neo4j GenAI Hands-On Lab with Databricks Program Template, 2026

## Program Name

Build Generative AI & GraphRAG Agents with Neo4j and Databricks

## Workshop Overview

This workshop equips participants with practical skills to combine Neo4j's graph database platform with Databricks AI/ML capabilities to build explainable, context-aware AI applications using GraphRAG and agentic patterns.

Participants will work with a real-world dataset—SEC 10-K financial filings—to experience how knowledge graphs enhance AI applications with structured context and relationship-aware retrieval.

Through a series of guided exercises, attendees will:

- Deploy and explore Neo4j Aura, the fully managed cloud graph platform
- Build no-code AI agents with Neo4j Aura Agents
- Understand foundational GenAI and retrieval strategies
- Build GraphRAG pipelines using Databricks Foundation Model APIs
- Connect to Neo4j using the Model Context Protocol (MCP) server for standardized graph access
- Create intelligent multi-agent systems with Databricks AgentBricks that coordinate across SQL and graph data sources
- Invoke Aura Agents programmatically via REST API

---

## Lab Agenda

### Part 1 – No-Code Getting Started with Neo4j Aura (Beginner Friendly)

#### Overview

Get hands-on with Neo4j Aura and build your first AI agent without writing any code. You'll provision a cloud graph database, load a real-world knowledge graph of SEC 10-K financial filings, and create an intelligent agent that can answer natural language questions about companies, risk factors, and ownership relationships.

#### Introductions & Lecture — Introduction to Neo4j Aura and Aura Agents

- Neo4j Aura: A fully managed, cloud-native graph database platform
- Neo4j Aura on AWS: Native deployment via AWS Marketplace with seamless integration
- Aura Agents: Build, test, and deploy AI agents grounded in your graph data without writing code

#### Labs

- **Lab 0 – Sign In**: Sign into AWS Console and workshop environment
- **Lab 1 – Neo4j Aura Setup**: Provision Neo4j Aura, restore a pre-built SEC 10-K knowledge graph, and explore relationships using Neo4j Explore
- **Lab 2 – Aura Agents**: Create a no-code AI agent using Neo4j Aura Agents
  - Configure semantic search tools for vector-based retrieval
  - Add Text2Cypher tools for natural language to Cypher translation
  - Test the agent with questions about companies, risks, and ownership

---

### Part 2 – GraphRAG with Neo4j and Databricks (Intermediate)

#### Overview

Move beyond no-code tools and build production-ready GraphRAG pipelines using Python. You'll use the neo4j-graphrag library with Databricks Foundation Models to implement vector search, graph traversal, and LLM-powered generation. Then, create sophisticated multi-agent systems using Databricks AgentBricks that coordinate between SQL data sources and Neo4j graph queries via the Model Context Protocol.

#### Lecture — Neo4j + Generative AI Concepts

- GraphRAG: Graph Retrieval-Augmented Generation and why graphs matter for AI
- Retrieval Patterns: Semantic search, hybrid retrieval, and context-aware generation

#### Lecture — Databricks AgentBricks and Multi-Agent Systems

- Databricks AI/BI Genie: Natural language to SQL for business users
- AgentBricks Multi-Agent Supervisor: Orchestrating specialized agents for complex tasks
- Model Context Protocol (MCP): The open standard for connecting AI agents to external tools and data sources
- Multi-Source Coordination: Combining structured data (Unity Catalog) with graph relationships (Neo4j) in agent systems

#### Labs

- **Lab 4 – GraphRAG with Neo4j**: Build GraphRAG pipelines using the neo4j-graphrag Python library with Databricks Foundation Models for embeddings and text generation
- **Lab 5 – AgentBricks Multi-Agent**: Build a multi-agent system with Databricks AgentBricks
  - Create a Databricks AI/BI Genie space for natural language SQL queries
  - Connect to Neo4j via external MCP server for graph queries
  - Build a Multi-Agent Supervisor that routes questions to the appropriate data source
  - Test cross-system queries combining structured data and graph relationships

---

### Part 3 – Advanced GraphRAG and Agents (Advanced)

#### Overview

Dive deeper into advanced retrieval techniques and production integration patterns. You'll learn to convert natural language directly to Cypher queries using Text2Cypher, automatically extract knowledge graphs from unstructured text, and programmatically invoke your Aura Agents via REST APIs with secure OAuth2 authentication.

> **Optional Section:** This part of the workshop is designed for all-day sessions or as advanced material that participants can take home and complete on their own infrastructure. It builds on the skills from Parts 1 and 2 and is ideal for those who want to dive deeper into production integration patterns.

#### What You'll Learn

- Advanced Retrieval: Text2Cypher and automated entity extraction techniques
- Aura Agents API: Programmatic invocation of Aura Agents via REST API
- OAuth2 Authentication: Secure machine-to-machine authentication with client credentials

#### Labs

- **Lab 6 – Advanced RAG**: Learn advanced retrieval and knowledge graph construction techniques
  - Use Text2Cypher to convert natural language questions directly to Cypher queries
  - Extract entities and relationships automatically from unstructured text
  - Build knowledge graphs programmatically using SimpleKGPipeline
- **Lab 10 – Aura Agents API**: Programmatically invoke your Aura Agent from external applications using REST APIs with OAuth2 authentication
