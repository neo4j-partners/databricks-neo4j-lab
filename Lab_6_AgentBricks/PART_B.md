# Lab 6 Part B: Multi-Agent with External MCP Server

In this part, you will create an agent using a pre-deployed Neo4j MCP server, then build a Multi-Agent Supervisor that coordinates both the Genie space (from Part A) and the Neo4j graph database to answer complex questions spanning structured data and graph relationships.

## Prerequisites

- Completed **Part A** (Databricks Genie space created)
- Pre-configured Unity Catalog HTTP connection to Neo4j MCP server (provided by your administrator)
- Access to AgentBricks Multi-Agent Supervisor

Your administrator has already:
1. Deployed the Neo4j MCP server to Azure Container Apps
2. Created a Unity Catalog HTTP connection (`neo4j_mcp`) with MCP enabled
3. Configured bearer token authentication via Databricks secrets

## Learning Objectives

By completing this part, you will:

1. Understand how external MCP servers integrate with Databricks
2. Test the Neo4j MCP connection and available tools
3. Create a Multi-Agent Supervisor with multiple subagent types
4. Configure agent descriptions for effective task routing
5. Test cross-system queries that combine SQL and graph data

---

## Part 1: Understanding the External MCP Server

### What is the Model Context Protocol?

The Model Context Protocol (MCP) is an open standard that enables AI agents to connect to external data sources and tools through a uniform interface. Instead of embedding database logic directly into your AI application, MCP provides a clean abstraction where agents can discover available tools and invoke them as needed.

### Neo4j MCP Server Architecture

The pre-deployed Neo4j MCP server runs on Azure Container Apps and provides:

```
┌─────────────────────────────────────┐      ┌──────────────────────────────────┐
│         DATABRICKS                   │      │         AZURE                    │
│                                      │      │                                  │
│   ┌─────────────────────────────┐    │      │   ┌──────────────────────────┐   │
│   │  Unity Catalog              │    │      │   │  Azure Container Apps    │   │
│   │  HTTP Connection            │────┼──────┼──▶│  Neo4j MCP Server        │   │
│   │  (MCP-enabled)              │    │      │   │  + Auth Proxy            │   │
│   └─────────────────────────────┘    │      │   └──────────────────────────┘   │
│              ▲                       │      │              │                   │
│              │                       │      │              ▼                   │
│   ┌──────────┴──────────────────┐    │      │   ┌──────────────────────────┐   │
│   │  AgentBricks / Notebooks    │    │      │   │  Neo4j Aura              │   │
│   │  (Multi-Agent Supervisor)   │    │      │   │  Graph Database          │   │
│   └─────────────────────────────┘    │      │   └──────────────────────────┘   │
└──────────────────────────────────────┘      └──────────────────────────────────┘
```

### Available MCP Tools

The Neo4j MCP server exposes these read-only tools:

| Tool | Description | Use Case |
|------|-------------|----------|
| `get-schema` | Retrieve database schema (labels, relationships, properties) | Understanding the graph structure |
| `read-cypher` | Execute read-only Cypher queries | Querying graph relationships |

---

## Part 2: Verify the MCP Connection

Before building the multi-agent system, verify that the MCP connection is working.

### Step 1: Navigate to Connections

1. In the Databricks sidebar, click **Catalog**
2. Click the gear icon, then **Connect** > **Connections**
3. Find the connection named `neo4j_mcp` (or the name provided by your administrator)

### Step 2: Verify Connection Details

Confirm the connection shows:
- **Type:** HTTP
- **Is MCP:** Yes (checkmark)
- **Authentication:** Bearer Token

### Step 3: Test with a Notebook (Optional)

Create a new notebook and test the connection:

```python
# List available MCP tools
result = spark.sql("""
    SELECT http_request(
      conn => 'neo4j_mcp',
      method => 'POST',
      path => '/',
      headers => map('Content-Type', 'application/json'),
      json => '{"jsonrpc":"2.0","method":"tools/list","params":{},"id":1}'
    )
""")
display(result)
```

```python
# Get the Neo4j schema
result = spark.sql("""
    SELECT http_request(
      conn => 'neo4j_mcp',
      method => 'POST',
      path => '/',
      headers => map('Content-Type', 'application/json'),
      json => '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"get-schema","arguments":{}},"id":2}'
    )
""")
display(result)
```

You should see the graph database schema with node labels like `Customer`, `Company`, `AssetManager`, and relationships like `OWNS`, `FACES_RISK`, etc.

---

## Part 3: Create the Multi-Agent Supervisor

Now you'll create a supervisor that coordinates both data sources:
- **Genie Space**: SQL queries against structured financial data
- **External MCP Server**: Graph queries against Neo4j relationships

### Step 1: Navigate to AgentBricks

1. In the Databricks sidebar, click **Agents**
2. Find the **Multi-Agent Supervisor** tile
3. Click **Build**

### Step 2: Configure the Supervisor

**Name:** `Financial Intelligence Coordinator` (add your initials to make it unique)

**Description:**
```
A multi-agent system that coordinates SQL-based financial data analysis through Genie
with graph-based relationship discovery through Neo4j. Answers complex questions
requiring both structured data lookups and relationship traversal.
```

### Step 3: Add the External MCP Server Agent

1. Under **Configure Agents**, click **Add Agent**
2. Select **External MCP Server** as the type
3. Select your Unity Catalog connection (`neo4j_mcp`) from the dropdown

**Agent Configuration:**
- **Agent Name:** `neo4j_graph_agent`
- **Describe the content:**
```
Queries the Neo4j knowledge graph to discover relationships between entities.
Use for questions about:
- How entities are connected (e.g., "Who owns which companies?")
- Relationship patterns (e.g., "What risks do companies share?")
- Graph traversals (e.g., "Find all paths between X and Y")
- Network analysis (e.g., "Which asset managers have overlapping portfolios?")

Available tools: get-schema (view graph structure), read-cypher (execute graph queries)
```

### Step 4: Add the Genie Space Agent

1. Click **Add Agent** again
2. Select **Genie Space** as the type
3. Select your `Financial Services Analyst` Genie space from Part A

**Agent Configuration:**
- **Agent Name:** `financial_data_agent`
- **Describe the content:**
```
Queries structured financial data in Unity Catalog tables using natural language to SQL.
Use for questions about:
- Customer demographics and profiles (names, IDs, income, risk tolerance)
- Company financial metrics and quarterly reports
- Investment strategy details and recommendations
- Market analysis data and sector trends

Best for: precise data lookups, aggregations, filtering by specific values
```

### Step 5: Review Agent Configuration

Your supervisor should now show two agents configured:

| Agent | Type | Data Source | Best For |
|-------|------|-------------|----------|
| `neo4j_graph_agent` | External MCP Server | Neo4j Graph | Relationship queries, patterns |
| `financial_data_agent` | Genie Space | Unity Catalog Tables | Data lookups, aggregations |

### Step 6: Add Supervisor Instructions

Click to expand advanced settings and add routing instructions:

```
You are a financial intelligence coordinator that combines structured data analysis
with graph-based relationship discovery.

Routing guidelines:
1. Questions about customer details, income, or demographics → financial_data_agent
2. Questions about company financials or quarterly metrics → financial_data_agent
3. Questions about relationships or connections → neo4j_graph_agent
4. Questions about "who owns what" or ownership patterns → neo4j_graph_agent
5. Questions about shared risks or common factors → neo4j_graph_agent

For complex questions requiring both agents:
- First gather base data from financial_data_agent
- Then explore relationships with neo4j_graph_agent
- Synthesize a comprehensive answer from both sources

Always explain which data source(s) provided the answer.
```

### Step 7: Create the Agent

Click **Create Agent** and wait for the supervisor to be provisioned (this may take several minutes).

---

## Part 4: Test the Multi-Agent System

Test your supervisor with questions that exercise different routing patterns.

### Single-Agent Queries

**SQL Data (Genie):**
```
What is Maria Rodriguez's annual income and risk tolerance?
```
Expected: Routes to `financial_data_agent`, returns customer profile data.

**Graph Relationships (Neo4j):**
```
Which asset managers own shares in technology companies?
```
Expected: Routes to `neo4j_graph_agent`, executes Cypher traversal.

### Cross-System Queries

**Combined Analysis:**
```
Find customers with conservative risk tolerance and show which companies
their preferred asset managers also invest in.
```
Expected: Supervisor coordinates both agents - gets customer data from Genie,
then queries relationship patterns from Neo4j.

**Network Discovery:**
```
Maria Rodriguez invests through BlackRock. What other companies does BlackRock
own, and what are their latest quarterly revenues?
```
Expected: Uses Neo4j to find ownership relationships, then Genie to get financial data.

### Observe Agent Coordination

For each test:
1. Note which agent(s) the supervisor invoked
2. Review the reasoning shown in the response
3. Verify data accuracy against your source systems

---

## Part 5: Monitoring and Iteration

### View Agent Activity

1. In your supervisor, click the **Monitoring** tab
2. Review recent conversations and agent invocations
3. Identify questions where routing could be improved

### Refine Agent Descriptions

Based on monitoring feedback:
- Update agent descriptions to be more specific
- Add examples of question types each agent handles best
- Clarify boundaries between agents

### Add Training Examples

In the **Examples** tab:
1. Add sample questions with expected agent routing
2. Provide expert feedback on responses
3. The supervisor learns from these examples over time

---

## Understanding the Architecture

### Why Two Data Systems?

| System | Strengths | Limitations |
|--------|-----------|-------------|
| **Unity Catalog (Genie)** | Fast aggregations, precise filtering, standard SQL | Limited relationship queries |
| **Neo4j (MCP)** | Complex traversals, pattern matching, network analysis | Not optimized for aggregations |

By combining both, you get:
- **SQL efficiency** for data retrieval and filtering
- **Graph power** for relationship discovery and path analysis
- **AI coordination** that routes questions to the best data source

### Data Flow

```
User Question
      │
      ▼
┌─────────────────────────────┐
│  Multi-Agent Supervisor     │
│  (Analyzes question intent) │
└─────────────────────────────┘
      │
      ├──────────────────────────────────────┐
      │                                      │
      ▼                                      ▼
┌─────────────────────┐          ┌─────────────────────┐
│  Genie Space Agent  │          │  Neo4j MCP Agent    │
│  (SQL Generation)   │          │  (Cypher Generation)│
└─────────────────────┘          └─────────────────────┘
      │                                      │
      ▼                                      ▼
┌─────────────────────┐          ┌─────────────────────┐
│  Unity Catalog      │          │  Neo4j Graph DB     │
│  Tables             │          │  (Azure MCP Server) │
└─────────────────────┘          └─────────────────────┘
      │                                      │
      └──────────────────┬───────────────────┘
                         │
                         ▼
              ┌─────────────────────────────┐
              │  Synthesized Response       │
              │  (Combined insights)        │
              └─────────────────────────────┘
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| MCP connection not showing | Verify connection has "Is MCP" enabled in settings |
| Agent timeout | Check MCP server health via notebook test |
| Wrong agent selected | Improve agent descriptions with more specific use cases |
| Incomplete answers | Add supervisor instructions for multi-agent coordination |

---

## Summary

In this part, you:

| Step | Accomplishment |
|------|----------------|
| **Part 1** | Understood external MCP server architecture |
| **Part 2** | Verified the Neo4j MCP connection |
| **Part 3** | Created a Multi-Agent Supervisor with Genie + MCP agents |
| **Part 4** | Tested cross-system queries with agent coordination |
| **Part 5** | Learned monitoring and iteration patterns |

Your multi-agent system can now intelligently route questions to the appropriate data source and synthesize answers from both structured tables and graph relationships.

## Next Steps

- Experiment with more complex multi-hop queries
- Add additional subagents (Unity Catalog functions, Knowledge Assistants)
- Explore the Genie and MCP APIs for programmatic access

## Resources

- [External MCP Servers in Databricks](https://docs.databricks.com/aws/en/generative-ai/mcp/external-mcp)
- [Unity Catalog HTTP Connections](https://docs.databricks.com/aws/en/query-federation/http)
- [AgentBricks Multi-Agent Supervisor](https://docs.databricks.com/aws/en/generative-ai/agent-bricks/multi-agent-supervisor)
- [Neo4j MCP Server](https://github.com/neo4j/mcp)
- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
