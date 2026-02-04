# Lab 5: Databricks AgentBricks - Genie & Multi-Agent Systems

Build intelligent multi-agent systems using Databricks AgentBricks that combine natural language SQL querying with graph-based relationship discovery.

## Overview

This lab introduces Databricks AI/BI Genie and AgentBricks Multi-Agent Supervisor through a hands-on financial services use case. You'll create agents that can answer complex business questions by coordinating across multiple data sources.

### What You'll Build

```
                    ┌─────────────────────────────────┐
                    │    Multi-Agent Supervisor       │
                    │    "Financial Intelligence"     │
                    └─────────────────────────────────┘
                                   │
                    ┌──────────────┴──────────────┐
                    │                             │
                    ▼                             ▼
        ┌─────────────────────┐       ┌─────────────────────┐
        │   Genie Space       │       │  External MCP       │
        │   Agent             │       │  Server Agent       │
        │                     │       │                     │
        │   Natural Language  │       │   Graph Queries     │
        │   → SQL Queries     │       │   → Cypher          │
        └─────────────────────┘       └─────────────────────┘
                    │                             │
                    ▼                             ▼
        ┌─────────────────────┐       ┌─────────────────────┐
        │   Unity Catalog     │       │   Neo4j Aura        │
        │   Tables            │       │   Knowledge Graph   │
        │                     │       │                     │
        │   • Customer data   │       │   • Ownership       │
        │   • Company reports │       │   • Relationships   │
        │   • Market analysis │       │   • Risk patterns   │
        └─────────────────────┘       └─────────────────────┘
```

### Use Cases

The multi-agent system enables questions like:

| Question Type | Agents Used | Example |
|---------------|-------------|---------|
| Data Lookup | Genie | "What is Maria Rodriguez's risk tolerance?" |
| Relationship Query | Neo4j MCP | "Which asset managers own tech companies?" |
| Combined Analysis | Both | "Find conservative investors and their managers' other holdings" |

---

## Lab Structure

This lab is divided into two parts that build on each other:

### [Part A: Databricks Genie Space](./PART_A.md)

Create an AI/BI Genie space for natural language querying of financial data.

**Topics Covered:**
- What is Databricks AI/BI Genie
- Creating and configuring a Genie space
- Adding sample questions and instructions (best practices)
- Testing natural language to SQL translation
- Understanding Genie's thinking steps

**Time:** ~30 minutes

### [Part B: Multi-Agent with External MCP Server](./PART_B.md)

Build a Multi-Agent Supervisor that coordinates Genie with a Neo4j graph database via external MCP server.

**Topics Covered:**
- Model Context Protocol (MCP) fundamentals
- External MCP server integration via Unity Catalog
- Creating Multi-Agent Supervisor
- Configuring agent descriptions for routing
- Testing cross-system queries
- Monitoring and iteration

**Time:** ~45 minutes

---

## Prerequisites

### Required Access
- Databricks workspace with serverless SQL warehouse
- Unity Catalog enabled
- Mosaic AI Agent Bricks Preview enabled

### Pre-Configured Resources (Provided by Administrator)

| Resource | Description |
|----------|-------------|
| Unity Catalog Tables | Customer profiles, company reports, investment strategies, market analysis |
| Neo4j MCP Server | Deployed to Azure Container Apps with HTTP connection |
| Unity Catalog Connection | `neo4j_mcp` HTTP connection with MCP enabled |

---

## Learning Objectives

By completing this lab, you will be able to:

1. **Create Genie Spaces** - Configure natural language interfaces for structured data
2. **Apply Best Practices** - Add sample questions and instructions to improve accuracy
3. **Understand MCP** - Explain how Model Context Protocol enables agent tool use
4. **Build Multi-Agent Systems** - Coordinate multiple specialized agents
5. **Design Agent Routing** - Write effective descriptions for task delegation
6. **Test Complex Queries** - Validate cross-system data synthesis

---

## Key Concepts

### AI/BI Genie

Databricks Genie enables business users to ask questions about data in natural language. It:
- Translates questions into SQL queries
- Executes against Unity Catalog tables
- Returns results with reasoning explanations
- Supports stateful follow-up conversations

### Model Context Protocol (MCP)

MCP is an open standard for connecting AI agents to external tools and data sources. It provides:
- Uniform tool discovery and invocation
- Protocol-level abstraction from implementation details
- Support for various transports (stdio, HTTP, SSE)

### AgentBricks Multi-Agent Supervisor

A no-code framework for building coordinated agent systems that:
- Routes questions to appropriate specialized agents
- Manages context across agent interactions
- Synthesizes responses from multiple sources
- Supports up to 10 subagents per supervisor

---

## Architecture Reference

### Data Flow

```
User Question
      │
      ▼
┌─────────────────────────────────────────────────────────────────┐
│                    MULTI-AGENT SUPERVISOR                        │
│                                                                  │
│   1. Analyze question intent                                     │
│   2. Select appropriate agent(s)                                 │
│   3. Coordinate execution                                        │
│   4. Synthesize response                                         │
└─────────────────────────────────────────────────────────────────┘
                    │
       ┌────────────┴────────────┐
       │                         │
       ▼                         ▼
┌─────────────────┐    ┌─────────────────┐
│  GENIE SPACE    │    │  EXTERNAL MCP   │
│                 │    │  SERVER         │
│  NL → SQL       │    │  NL → Cypher    │
└─────────────────┘    └─────────────────┘
       │                         │
       ▼                         ▼
┌─────────────────┐    ┌─────────────────┐
│ Unity Catalog   │    │ Neo4j Aura      │
│ (SQL Warehouse) │    │ (via Azure MCP) │
└─────────────────┘    └─────────────────┘
```

### Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| Orchestration | AgentBricks Multi-Agent Supervisor | Agent coordination |
| SQL Interface | AI/BI Genie | Natural language to SQL |
| Graph Interface | Neo4j MCP Server | Natural language to Cypher |
| SQL Storage | Unity Catalog | Governed structured data |
| Graph Storage | Neo4j Aura | Knowledge graph |
| MCP Hosting | Azure Container Apps | Serverless MCP endpoint |

---

## Quick Reference

### Genie Space Configuration

```
Name: Financial Services Analyst
Tables: customer_profiles, company_reports, investment_strategies, market_analysis
Warehouse: Serverless SQL
```

### Multi-Agent Supervisor Configuration

| Agent | Type | Connection | Purpose |
|-------|------|------------|---------|
| `financial_data_agent` | Genie Space | Financial Services Analyst | SQL queries |
| `neo4j_graph_agent` | External MCP | neo4j_mcp | Graph queries |

### Test Questions

**Genie Only:**
- "What customers have aggressive risk tolerance?"
- "Show quarterly revenue for Global Finance Corp"

**Neo4j Only:**
- "Which asset managers own multiple companies?"
- "Find shared risk factors between Apple and Microsoft"

**Multi-Agent:**
- "Find conservative investors and what other companies their managers invest in"
- "Compare customer portfolios with their connected company financials"

---

## Resources

### Databricks Documentation
- [AI/BI Genie Overview](https://docs.databricks.com/aws/en/genie/)
- [Curate Effective Genie Spaces](https://docs.databricks.com/aws/en/genie/best-practices)
- [AgentBricks Multi-Agent Supervisor](https://docs.databricks.com/aws/en/generative-ai/agent-bricks/multi-agent-supervisor)
- [External MCP Servers](https://docs.databricks.com/aws/en/generative-ai/mcp/external-mcp)
- [Genie Conversation API](https://docs.databricks.com/aws/en/genie/conversation-api)

### Neo4j Resources
- [Neo4j MCP Server](https://github.com/neo4j/mcp)
- [Cypher Query Language](https://neo4j.com/docs/cypher-manual/current/)

### Protocol Specifications
- [Model Context Protocol](https://modelcontextprotocol.io/)

---

## Next Steps

**Congratulations!** You've completed Part 2 of the workshop.

For advanced material (all-day sessions or self-paced learning), continue with **Part 3 - Advanced GraphRAG and Agents**:

- **[Lab 6 - Advanced RAG](../Lab_6_Advanced_RAG)**: Learn Text2Cypher retrieval and automated entity extraction
- **[Lab 10 - Aura Agents API](../Lab_10_Aura_Agents_API)**: Programmatically invoke Aura Agents via REST API
