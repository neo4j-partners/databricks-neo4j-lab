# Lab 6: Databricks Genie & AgentBricks

In this lab, you will create an AI/BI Genie space to enable natural language querying of financial services data, then integrate it as a subagent within Databricks AgentBricks Multi-Agent Supervisor to build a coordinated multi-agent system.

## Prerequisites

- Completed **Lab 0** (Sign In to Databricks)
- Access to a Databricks workspace with:
  - Serverless SQL warehouse (or Pro warehouse)
  - Unity Catalog enabled
  - Mosaic AI Agent Bricks Preview enabled
- Pre-loaded data in Unity Catalog (provided by your administrator)

Your administrator has already uploaded the financial services dataset to a Databricks Volume and created the following Unity Catalog tables:

| Table | Description |
|-------|-------------|
| `customer_profiles` | Customer information including demographics, risk tolerance, and investment preferences |
| `company_reports` | Quarterly reports and financial metrics for companies |
| `investment_strategies` | Investment guidance documents and risk profiles |
| `market_analysis` | Sector analysis and market trends |

## Learning Objectives

By completing this lab, you will:

1. Understand what Databricks AI/BI Genie is and when to use it
2. Create and configure a Genie space for natural language data querying
3. Apply best practices for curating effective Genie spaces
4. Integrate a Genie space as a subagent in AgentBricks Multi-Agent Supervisor
5. Test multi-agent coordination and task delegation

---

## Part 1: Create a Databricks Genie Space

### What is AI/BI Genie?

Databricks AI/BI Genie enables business users to ask questions about their data in natural language. Genie translates questions into SQL queries, executes them against your data, and returns results with explanations of its reasoning.

Key capabilities:
- Natural language to SQL translation
- Stateful conversations with follow-up questions
- Thinking steps showing query interpretation
- Integration with Unity Catalog for governance

### Step 1: Navigate to Genie

1. In your Databricks workspace, click **Genie** in the left sidebar
2. Click **New** in the upper-right corner to create a new Genie space

### Step 2: Configure Your Genie Space

**Name:** `Financial Services Analyst` (add your initials to make it unique)

**Description:**
```
An AI-powered assistant for analyzing customer profiles, company financial reports,
investment strategies, and market trends. Helps answer questions about customer
portfolios, risk assessments, and financial metrics.
```

### Step 3: Select Data Sources

Add the following tables from Unity Catalog to your Genie space:

- `catalog.schema.customer_profiles`
- `catalog.schema.company_reports`
- `catalog.schema.investment_strategies`
- `catalog.schema.market_analysis`

> **Note:** Replace `catalog.schema` with the actual catalog and schema names provided by your administrator.

### Step 4: Configure SQL Warehouse

Select your **Serverless SQL Warehouse** for optimal performance. Genie requires either a Pro or Serverless warehouse.

### Step 5: Add Sample Questions (Best Practice)

Adding sample questions helps Genie understand your business context. Click **Add Sample Questions** and include:

```
What is the investment risk tolerance for customer Maria Rodriguez?
```

```
Show me the quarterly revenue for Global Finance Corp.
```

```
Which customers have a conservative investment approach?
```

```
What are the top risks mentioned in the market analysis for the technology sector?
```

### Step 6: Add Instructions (Best Practice)

Provide domain-specific instructions to improve Genie's accuracy:

```
When answering questions about customers:
- Customer risk tolerance can be: conservative, moderate, or aggressive
- Always include customer ID when referencing specific customers
- Credit scores range from 300-850

When answering questions about companies:
- Use ticker symbols when available (e.g., GFIN for Global Finance Corp)
- Financial metrics should include currency units
- Quarterly reports follow fiscal year conventions
```

### Step 7: Test Your Genie Space

Test the Genie space with these questions:

1. **"Tell me about Maria Rodriguez's investment profile"**
   - Observe the thinking steps showing how Genie interpreted the question
   - Review the generated SQL query

2. **"What companies are in the database?"**
   - Verify Genie correctly queries the company_reports table

3. **"Which customers prefer ESG investments?"**
   - Test semantic understanding of investment preferences

4. **"Compare the risk factors between technology and real estate sectors"**
   - Test cross-table analysis capabilities

---

## Part 2: Integrate Genie with AgentBricks

### What is AgentBricks Multi-Agent Supervisor?

AgentBricks Multi-Agent Supervisor creates a coordinator that orchestrates multiple specialized agents (including Genie spaces) to complete complex tasks. The supervisor:

- Routes questions to the appropriate subagent
- Manages context across agent interactions
- Synthesizes responses from multiple sources

### Step 1: Navigate to AgentBricks

1. In your Databricks workspace, click **Agents** in the left sidebar
2. Find the **Multi-Agent Supervisor** tile
3. Click **Build**

### Step 2: Configure the Supervisor

**Name:** `Financial Services Coordinator` (add your initials)

**Description:**
```
A multi-agent system that coordinates financial data analysis through Genie
with additional tools for comprehensive customer and market intelligence.
```

### Step 3: Add Your Genie Space as a Subagent

1. Under **Configure Agents**, click **Add Agent**
2. Select **Genie Space** as the agent type
3. Choose your `Financial Services Analyst` Genie space from the dropdown
4. The agent name and description will auto-populate (you can edit these)

**Agent Configuration:**
- **Name:** `financial_data_analyst`
- **Description:** `Queries structured financial data including customer profiles, company reports, investment strategies, and market analysis. Use for questions requiring SQL-based data retrieval.`

### Step 4: (Optional) Add Additional Subagents

You can extend your supervisor with additional capabilities:

| Agent Type | Use Case |
|------------|----------|
| **Unity Catalog Functions** | Custom Python functions for calculations |
| **Knowledge Assistant** | RAG over unstructured documents |
| **MCP Server** | External tool integrations |

### Step 5: Configure Supervisor Instructions

Add instructions to help the supervisor route questions effectively:

```
You are a financial services coordinator that helps users with:
1. Customer portfolio analysis - delegate to financial_data_analyst
2. Company financial metrics - delegate to financial_data_analyst
3. Investment strategy questions - delegate to financial_data_analyst

Always provide context about which agent answered the question.
For complex questions requiring multiple data sources, synthesize responses from relevant agents.
```

### Step 6: Test the Multi-Agent System

Test supervisor coordination with these questions:

1. **"What is Maria Rodriguez's risk tolerance and what investment strategies match it?"**
   - Observe the supervisor delegating to the Genie agent
   - Review how results are synthesized

2. **"Compare customer portfolios with the latest market analysis for their sectors"**
   - Test multi-step reasoning across data sources

3. **"Summarize Global Finance Corp's performance and identify customers who hold their stock"**
   - Test cross-entity relationship queries

---

## Part 3: Access Genie Programmatically (Optional)

### Genie Conversation API

The Genie API enables programmatic access for integration into applications. Key endpoints:

| Endpoint | Purpose |
|----------|---------|
| `POST /api/2.0/genie/spaces/{space_id}/start-conversation` | Start a new conversation |
| `POST /api/2.0/genie/spaces/{space_id}/conversations/{conversation_id}/messages` | Send follow-up messages |
| `GET /api/2.0/genie/spaces/{space_id}/conversations/{conversation_id}/messages/{message_id}` | Get message results |

### Rate Limits

- UI access: 20 questions/minute per workspace
- API free tier: 5 questions/minute per workspace (best effort during preview)

### Example: Python Client

```python
import requests
import time

class GenieClient:
    def __init__(self, host: str, token: str, space_id: str):
        self.host = host
        self.token = token
        self.space_id = space_id
        self.headers = {"Authorization": f"Bearer {token}"}

    def ask(self, question: str) -> dict:
        # Start conversation
        response = requests.post(
            f"{self.host}/api/2.0/genie/spaces/{self.space_id}/start-conversation",
            headers=self.headers,
            json={"content": question}
        )
        result = response.json()
        conversation_id = result["conversation_id"]
        message_id = result["message_id"]

        # Poll for completion
        while True:
            status = requests.get(
                f"{self.host}/api/2.0/genie/spaces/{self.space_id}/conversations/{conversation_id}/messages/{message_id}",
                headers=self.headers
            ).json()

            if status.get("status") == "COMPLETED":
                return status
            time.sleep(1)
```

---

## Best Practices Summary

### Curating Effective Genie Spaces

1. **Add sample questions** - Help Genie understand your business terminology
2. **Provide text instructions** - Define domain-specific rules and conventions
3. **Monitor usage** - Review questions on the Monitoring tab to identify gaps
4. **Iterate based on feedback** - Add context for questions Genie struggles with

### Multi-Agent Design

1. **Clear agent descriptions** - Help the supervisor route correctly
2. **Single responsibility** - Each agent should have a focused purpose
3. **Test edge cases** - Verify routing for ambiguous questions
4. **Limit agent count** - Maximum of 10 subagents per supervisor

---

## Summary

In this lab, you:

| Step | Accomplishment |
|------|---------------|
| **Part 1** | Created a Genie space for natural language data querying |
| **Part 2** | Integrated Genie as a subagent in AgentBricks Multi-Agent Supervisor |
| **Part 3** | Learned how to access Genie programmatically via the API |

Your multi-agent system can now coordinate complex financial analysis tasks by leveraging Genie's natural language to SQL capabilities within a broader agent orchestration framework.

## Next Steps

- **Lab 7**: Explore Neo4j MCP integration to add graph-based reasoning to your agent system
- **Lab 10**: Build programmatic clients for the Aura Agents API

## Resources

- [Set up and manage an AI/BI Genie space](https://docs.databricks.com/aws/en/genie/set-up)
- [Curate an effective Genie space](https://docs.databricks.com/aws/en/genie/best-practices)
- [Use Genie in multi-agent systems](https://docs.databricks.com/aws/en/generative-ai/agent-framework/multi-agent-genie)
- [Genie Conversation API](https://docs.databricks.com/aws/en/genie/conversation-api)
- [AgentBricks Multi-Agent Supervisor](https://docs.databricks.com/aws/en/generative-ai/agent-bricks/multi-agent-supervisor)
