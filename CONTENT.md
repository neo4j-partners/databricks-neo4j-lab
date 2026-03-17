# Workshop Overview

Participants build a production-ready multi-agent system for aircraft digital twins, combining Neo4j's knowledge graph with Databricks' Lakehouse to answer questions that neither platform can handle alone.

## GenAI Limitations and How This Workshop Addresses Them

Large language models generate the most *probable* continuation of a prompt, not the most *accurate*. Three structural limitations make them unreliable for enterprise applications without additional architecture.

**Hallucination.** LLMs produce confident, detailed responses even when they have no factual basis. The outputs read as authoritative because the model optimizes for fluency, not correctness. In 2023, US lawyers submitted an LLM-generated legal brief containing six fabricated case citations. Production systems need a way to ground responses in verified data.

**Knowledge cutoff.** Models are trained at a fixed point in time on publicly available text. They cannot access your maintenance records, last quarter's sensor telemetry, or this morning's flight data. Worse, they don't decline to answer. Ask about data they've never seen and they generate a plausible response anyway.

**Relationship blindness.** LLMs process text sequentially and treat each piece of information in isolation. Questions like "which aircraft have engines with critical maintenance events?" or "how is a sensor reading connected to a flight delay?" require reasoning across chains of connected entities. Similarity search over document chunks cannot reconstruct those chains.

All three limitations share a common remedy: providing the right context at inference time. This workshop builds three layers of that remedy. Graph databases ground responses in verified, structured data (hallucination). RAG retrieval surfaces your proprietary information at query time (knowledge cutoff). Knowledge graph traversal preserves and exposes the relationships between entities (relationship blindness).

---

> **Context ROT: when more context makes things worse.**
>
> Research from Chroma ("Context ROT") demonstrates that irrelevant context doesn't just fail to help; it actively degrades LLM accuracy. As retrieved chunks increase in volume but decrease in relevance, the model's responses get worse, not better. The context window fills with tangentially related information and the model gets confused or misled by the noise. Quality of context matters more than quantity. This is the core argument for GraphRAG over traditional RAG: graph-structured retrieval returns *connected, relevant* context rather than *similar but unrelated* chunks, because it follows explicit relationships between entities instead of relying solely on embedding distance.

---

## Databricks + Neo4j

Databricks and Neo4j solve different problems well, and most real-world systems need both.

Databricks excels at scale: aggregations over millions of sensor readings, time-series analysis, and machine learning pipelines across large tabular datasets. Neo4j excels at structure: traversing chains of relationships, finding patterns across connected entities, and answering questions about how things relate to each other.

In this workshop, aircraft, systems, and sensors exist in both platforms as shared join points. The Spark Connector moves data between them. MCP lets AI agents query the graph directly. Neither platform replaces the other; each handles the class of query it was designed for.

## Workshop Roadmap

The five labs progress from foundational setup through increasingly sophisticated AI patterns.

**Lab 1: Neo4j Aura Setup.** Stand up a Neo4j Aura instance and load the aircraft digital twin graph. Explore the topology with Cypher: aircraft, systems, components, sensors, flights, maintenance events, and the relationships connecting them.

**Lab 2: Databricks ETL.** Use the Neo4j Spark Connector to move data from Databricks Lakehouse tables into the knowledge graph. What was implicit in foreign keys and table joins becomes explicit, traversable structure in Neo4j.

**Lab 3: GraphRAG Semantic Search.** Chunk maintenance manuals, generate embeddings, and store them as graph-connected nodes in Neo4j. Vector search finds relevant text; graph traversal enriches results with the aircraft, systems, and components each document describes.

**Lab 4: Compound AI Agents.** Build a multi-agent system with a Supervisor Agent that routes questions to specialized sub-agents. A Genie space agent handles numeric aggregations and time-series queries over Lakehouse tables via natural language to SQL. A Neo4j MCP agent handles relationship traversals and structural queries over the knowledge graph via Cypher. The supervisor decides where each question belongs, or calls both agents in sequence when a question spans both domains.

**Lab 5: Aura Agents.** Use Neo4j's Create with AI capability to build graph-native agents directly within Aura.
