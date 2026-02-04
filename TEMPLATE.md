# Neo4j GenAI Hands-On Lab with AWS Program Template, 2026

## Program Name

Build Generative AI & GraphRAG Agents with Neo4j and Amazon Bedrock

## Workshop Overview

This workshop equips participants with practical skills to combine Neo4j graph databases with AWS Amazon Bedrock GenAI capabilities to build explainable, context-aware AI applications using GraphRAG and agentic patterns.

Through a series of guided exercises, attendees will:

- Deploy and explore Neo4j knowledge graphs
- Understand foundational GenAI and retrieval strategies
- Build AI agents and RAG pipelines using AWS Bedrock
- Programmatically invoke agents and integrate with applications

---

## Lab Agenda

### Part 1 – No-Code Getting Started (Beginner Friendly)

#### Introductions & Lecture — Introduction to Neo4j Aura and Aura Agents

- What Neo4j Aura is
- How it's deployed & managed on AWS (Native graph platform, AWS Marketplace integration)

#### Labs

| Lab | Description |
|-----|-------------|
| **Lab 0 – Sign In** | Sign into AWS Console and workshop environment |
| **Lab 1 – Neo4j Aura Setup** | Provision Neo4j via AWS Marketplace, restore pre-built knowledge graph, explore graph using visual tools |
| **Lab 2 – Aura Agents** | Use Neo4j Aura Agents (no-code), configure semantic search & Text2Cypher tools |


---

### Part 2 – Intro to Bedrock & GraphRAG (Intermediate)

#### Lecture — Neo4j + Generative AI Concepts

- What is GraphRAG (Graph Retrieval-Augmented Generation)
- Patterns for semantic & hybrid retrieval

#### Labs

| Lab | Description |
|-----|-------------|
| **Lab 4 – Intro to Bedrock and Agents** | Launch SageMaker Studio, clone workshop repo and setup Bedrock configs, build basic LangGraph AI agent that calls AWS Bedrock |
| **Lab 5 – GraphRAG with Neo4j** | Load and create embeddings using Amazon Titan, create vector indexes in Neo4j, build GraphRAG pipelines using hybrid retrieval strategies |

---

### Part 3 – Advanced Agents & API Integration (Advanced)

#### What You'll Learn

- Programmatic invocation of no-code Aura Agents
- REST API and OAuth2 integration patterns
- Using Model Context Protocol (MCP) servers for agent-based apps

#### Labs

| Lab | Description |
|-----|-------------|
| **Lab 6 – Aura Agents API** | Build a programmatic client to invoke Aura Agent via REST, implement OAuth2 client credentials flow |
| **Lab 7 – Neo4j MCP Agent** | Integrate MCP server tools with AWS AgentCore Gateway, build LangGraph agent with natural language access to the Neo4j graph |
