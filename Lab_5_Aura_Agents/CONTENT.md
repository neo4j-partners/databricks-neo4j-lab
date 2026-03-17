# Lab 5: Concepts and Reference

Labs 3 and 4 built retrieval and agent capabilities programmatically, wiring vector search, Cypher queries, and LLM orchestration through Databricks notebooks and Agent Bricks. Lab 5 takes a different path to a similar outcome. Neo4j Aura Agents provide a managed, no-code conversational interface over the same knowledge graph, so the focus shifts from building agent infrastructure to configuring one that already exists.

## What Are Aura Agents?

Aura Agents combine semantic search, graph traversal, and natural language queries into a single conversational layer hosted inside the Neo4j console. The "Create with AI" workflow inspects the knowledge graph schema and automatically generates the tools an agent needs. There is no application code to write and no Cypher templates to configure manually. The result is a chatbot-style interface where users ask questions in plain English and the agent selects the right retrieval strategy behind the scenes.

## The "Create with AI" Workflow

When you launch "Create with AI" against a database, the system reads the graph's node labels, relationship types, properties, and vector indexes. From that schema inspection it generates a set of tools across three categories, each mapped to the query patterns the graph can support. You can then test the agent in the console, adjust which tools are enabled, and iterate without redeploying anything.

## Agent Tool Types

### Cypher Templates

Pre-defined graph traversal patterns that map to specific relationships in the knowledge graph. Each template takes parameters (an aircraft ID, a flight number) and executes a fixed Cypher query. Because the query never varies, results are deterministic given valid input.

### Similarity Search

Semantic vector search over embedded content. The agent converts the user's question into an embedding and retrieves the most similar chunks from the vector index, surfacing maintenance manual passages even when the terminology differs from the query.

### Text2Cypher

Translates arbitrary natural language into Cypher for ad-hoc exploration. This is the most flexible tool but carries the highest risk of incorrect results, since the generated query varies with each invocation.

## Confabulation Risk with Text2Cypher

Text2Cypher generates a different Cypher query each time, and subtle bugs in the generated query can produce wrong answers silently. Filtering on `"critical"` instead of `"CRITICAL"` returns no results for case-sensitive properties. Rather than questioning the empty result, the agent confabulates a plausible explanation, confidently stating that the aircraft had no critical events when it actually has seven.

This failure mode is why the three tool types exist as a spectrum of reliability. Cypher Templates are deterministic and always return correct results. Similarity Search is grounded in vector similarity scores. Text2Cypher is valuable for ad-hoc exploration but should be cross-checked, especially when the answer is zero or seems surprising. Running the same question twice and comparing results is a practical way to spot generated-query variability.
