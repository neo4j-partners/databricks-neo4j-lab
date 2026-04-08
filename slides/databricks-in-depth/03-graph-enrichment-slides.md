---
marp: true
theme: default
paginate: true
---

<style>
section {
  --marp-auto-scaling-code: false;
}

li {
  opacity: 1 !important;
  animation: none !important;
  visibility: visible !important;
}

/* Disable all fragment animations */
.marp-fragment {
  opacity: 1 !important;
  visibility: visible !important;
}

ul > li,
ol > li {
  opacity: 1 !important;
}
</style>

# Graph Feature Engineering with Neo4j GDS and Databricks

Feature Engineering in Unity Catalog + AutoML

---

## Partnership Overview and Recap

- **Joint Customer Base:** over 200 shared customers across Aura and Enterprise, including Gilead, iFord, Comcast, and Ashley Furniture
- **Neo4j Spark Connector (5.x):** bidirectional data transfer between Databricks Lakehouse and Neo4j, supporting Unity Catalog and Delta tables. Silver tables feed the graph; Gold tables capture graph insights
- **Connection Patterns:** Spark Connector for batch pipelines, Unity Catalog JDBC for governed SQL and BI federation, Neo4j MCP Server for agent-driven Cypher, neo4j-graphrag-python for knowledge graph construction
- **Previous webinar:** built a knowledge graph from unstructured documents, then used GraphRAG to combine vector search with graph traversal so agents receive richer context than text search alone

<!--
Quick recap of the partnership and what we covered last time.
Over 200 organizations run both Neo4j and Databricks. The Spark
Connector is the foundation for everything today: it moves data
bidirectionally between the Lakehouse and the graph.

The previous webinar built a knowledge graph from unstructured
documents: chunking, embedding, entity extraction. GraphRAG
combined vector search with graph traversal so agents receive
document context alongside structured data. Specialized agents
like Genie for SQL and Neo4j MCP for Cypher route through a
supervisor to span both platforms.

Today we add the next layer: feature engineering from graph
topology.
-->

---

## What You'll Learn

- What feature engineering is and why graph structure produces features flat tables cannot
- How Neo4j GDS algorithms generate features from graph topology
- The bi-directional pattern: GDS features flow to Feature Engineering in Unity Catalog, AutoML predictions flow back to Neo4j
- How to measure the lift graph features add to a classifier
- Sync strategies for keeping Neo4j and Databricks aligned

<!--
Five things by the end of this session. First, what graph feature
engineering actually is and why it matters. Second, which GDS
algorithms produce useful features. Third, the full loop between
Neo4j and Databricks. Fourth, how to measure whether graph features
actually improve a classifier. Fifth, how to keep the two systems
in sync without manual intervention.
-->

---

## Recap: Graph-Enriched Retrieval

- **Data pipeline complete:** Spark Connector projected Delta tables into graph nodes and relationships
- **KG construction complete:** documents chunked, embedded, entity-extracted into the graph
- **Search finds the starting points:** chunks closest in meaning to the question
- **Graph traversal enriches:** follows entities and relationships from those chunks into the operational graph
- **Agents receive richer context** than text search alone: structured data alongside document content

<!--
Quick recap of what graph-enriched retrieval gives us. The data
pipeline used the Spark Connector to project governed Delta tables
into Neo4j as nodes and relationships. Knowledge graph construction
added the unstructured layer: documents chunked, embedded, and
entity-extracted into the same graph.

GraphRAG combines both layers. Vector search finds the chunks
most relevant to the user's question. Graph traversal follows
extracted entities from those chunks through cross-links into the
operational data. The agent receives structured holdings alongside
document context in a single response.

This works well for questions that documents can answer. The next
slide shows where it stops.
-->

---

## The Dual Architecture for This Use Case

- **Databricks holds the analytical layer:** Delta tables with customer demographics (income, credit score, portfolio value) and transaction history, plus UC Volumes with unstructured documents (customer profiles, investment guides, market analyses)
- **Neo4j holds the relationship layer:** Customer → Account → Position → Stock portfolio topology, plus enrichment relationships from document analysis (INTERESTED_IN, HAS_GOAL, CONCERNED_ABOUT)
- **The Spark Connector bridges both directions:** Silver tables seed the graph; graph algorithm results flow back to Gold tables
- **Each system does what it's best at:** Databricks runs SQL aggregations, AutoML, and Feature Engineering. Neo4j runs GDS algorithms, pattern matching, and GraphRAG retrieval

<!--
Before we dive into graph features, let's be clear about what
lives where and why. This is the same dual architecture pattern
from the first webinar, applied to the portfolio use case.

Databricks holds the analytical layer. Delta tables contain
customer demographics: income, credit score, portfolio value,
transaction history. UC Volumes store the unstructured documents:
customer profiles, investment guides, and market analyses. This
is where AutoML trains and Feature Engineering registers tables.

Neo4j holds the relationship layer. The Spark Connector projected
Silver tables into the portfolio topology: Customer to Account to
Position to Stock. Document analysis added enrichment
relationships: INTERESTED_IN, HAS_GOAL, CONCERNED_ABOUT. These
connect customers to sectors and themes that no Delta column
encodes.

The Spark Connector bridges both directions. Silver tables seed
the graph. GDS algorithm results flow back to Gold tables. Model
predictions flow back to Neo4j. Each system does what it is built
for: Databricks handles tabular analytics and ML training, Neo4j
handles relationship traversal and graph algorithms.
-->

---

## What the Graph Contains: Three Layers

- **Operational graph (from Delta tables):** 103 Customers, their Accounts, Positions, and the Stocks those positions hold. The Spark Connector built this from governed Silver tables
- **Enrichment layer (from document analysis):** INTERESTED_IN, HAS_GOAL, CONCERNED_ABOUT — relationships LLM agents extracted from customer profiles and market documents. Only 3 of 103 customers have profile documents
- **Document layer (for GraphRAG):** Document → Chunk nodes with embeddings and extracted entities (Interest, Goal, Sector) cross-linked to operational nodes
- **GDS operates on any combination** of these layers through projection configuration. The projection you build determines the features you get

<!-- TODO: create diagram of graph model -->

<!--
The graph has three distinct layers, each built by a different
pipeline stage. The operational graph is what the Spark Connector
built from Delta tables: 103 customers, their accounts, the
positions in those accounts, and the stocks those positions hold.
This is the portfolio topology that GDS algorithms will operate
on.

The enrichment layer is what LLM agents added by analyzing
documents against the graph. INTERESTED_IN, HAS_GOAL, and
CONCERNED_ABOUT are relationship types that connect customers to
sectors and investment themes. Only 3 of 103 customers have
profile documents, so this layer is sparse. That sparsity is
exactly why we need GDS: algorithms can propagate those signals
across the full graph.

The document layer supports GraphRAG retrieval. Documents split
into chunks with embeddings for vector search, and entities
extracted from those chunks cross-link into the operational
graph. This layer answered questions in the previous webinar.

GDS can project any combination of these layers. A projection
including only the operational graph produces features based on
portfolio structure. A projection including enrichment
relationships produces richer features that encode customer
intent alongside holdings. The projection configuration
determines the features you get.
-->

---

## What Graph-Enriched Search Doesn't Capture

- **GraphRAG works well for documents:** chunking, embedding, entity extraction, retrieval with graph context
- **Structural patterns are missing:** which customers cluster together, who holds similar portfolios, what risk categories apply
- **These patterns live in graph topology,** not in document text: no amount of vector search will find them

<!--
Graph-enriched search provides better context for what documents
contain, but critical information is still missing from the
unstructured text. Structural patterns like which customers
cluster together, who holds similar portfolios, and what risk
categories apply are encoded in graph topology, not in words.

No amount of vector search will surface these patterns. You need
algorithms that operate on the graph's structure directly. That
is what GDS feature engineering does.
-->

---

# Foundations: Features and Classifiers

---

## What Are Features and Classifiers?

- **Feature:** a column describing an entity: age, balance, number of connections, or a category like community membership
- **Classifier:** takes rows of features and predicts a label like risk category. Features in, label out
- **Feature engineering:** creating new, informative features from raw data
- **Graph feature engineering:** the graph's structure (who connects to whom) becomes columns a classifier can learn from

<!--
Quick vocabulary for anyone new to ML terminology. A feature is
a column that describes something about an entity. It can be
numeric like age or balance, or categorical like community
membership. A classifier takes rows of features and learns to
predict a label.

Feature engineering is the process of creating new features from
raw data. Graph feature engineering specifically turns the graph's
structure into columns: who connects to whom, who shares neighbors,
who belongs to which community. These structural features capture
information that no single table column encodes.
-->

---

## Example: Features and Classification

| Customer | Income | Portfolio Value | Community | Risk Category |
|----------|--------|-----------------|-----------|---------------|
| Alice    | 95K    | 240K            | 3         | **High**      |
| Bob      | 88K    | 310K            | 3         | **High**      |
| Carol    | 62K    | 85K             | 7         | **Low**       |
| Dave     | 91K    | 275K            | 3         | ???           |

- **Columns are features:** income, portfolio value, and community ID each describe something about a customer
- **Risk category is the label** the classifier learns to predict
- **Dave looks like Alice and Bob:** similar income, similar portfolio, same community. The classifier predicts **High**

<!--
A concrete example makes the vocabulary real. Each row is a
customer. Each column is a feature: income, portfolio value,
and community ID from Louvain. Risk category is the label the
classifier learns to predict.

Alice and Bob are labeled High. Carol is labeled Low. Dave has
no label yet. The classifier looks at the feature columns and
notices Dave's pattern matches Alice and Bob: similar income,
similar portfolio value, and the same community ID. It predicts
High.

Community ID is the graph feature here. Without it, the
classifier only sees income and portfolio value. With it, the
classifier knows Dave clusters with Alice and Bob in the graph,
not with Carol. That structural signal is what graph feature
engineering adds.
-->

---

## The Problem: The 3-of-103 Gap

- **The 3-of-103 problem:** a standard agent can discover customer interests by reading profile documents, but only 3 of 103 customers have documents. The other 100 have holdings data and tabular attributes with no text
- **What a classifier needs:** features that capture structural patterns: which customers cluster together, who holds similar portfolios, who bridges separate groups
- **The gap:** we need features that capture network position, not just individual attributes

<!--
Here is the concrete problem. An LLM-based agent could discover
customer interests by reading profile documents. But only 3 of
103 customers have documents. The other 100 have holdings data
and tabular attributes with no text for the agent to analyze.

A classifier needs numeric and categorical features. Tabular data
alone misses structural patterns. We need features that capture
a customer's position in the network: how they connect to other
customers, stocks, and sectors through the graph.
-->

---

## The Solution: Neo4j GDS + Feature Engineering in Unity Catalog

- **Neo4j GDS:** 65+ graph algorithms that turn topology into features: embeddings, scores, community IDs
- **Feature Engineering in Unity Catalog + AutoML:** consumes graph features alongside tabular data, trains classifiers, selects the best model
- **Neo4j Spark Connector:** the bridge: bidirectional data transfer between the two systems
- **Together:** GDS computes what flat tables cannot see; Feature Engineering + AutoML trains models on the combined picture

<!--
Two systems, complementary strengths. Neo4j GDS has over 65 graph
algorithms that turn topology into numeric features: embeddings,
centrality scores, community IDs. Feature Engineering in Unity
Catalog consumes those features alongside tabular data. AutoML
trains classifiers across multiple model families and selects the
best performer.

The Neo4j Spark Connector is the bridge. It moves data
bidirectionally between the two systems. GDS computes what flat
tables cannot see; Databricks trains models on the combined
picture.
-->

---

# GDS Feature Engineering

---

## GDS Foundations

- **Graph projections:** algorithms run on in-memory projections, not the live database. A projection selects specific node labels and relationship types, creating an optimized in-memory copy
- **Projection configuration:** which node labels, relationship types, and relationship properties you include determines the features you get. Different projections of the same graph produce different results
- **Execution modes:** stream (return results), stats (summary only), mutate (add to projection for chaining), write (persist to database)

<!--
Three foundational concepts before we run algorithms. First,
algorithms run on in-memory projections, not the live database.
You select which node labels and relationship types to include,
and GDS creates an optimized copy for algorithm execution.

Second, what you include in the projection matters. Node labels,
relationship types, and relationship properties all shape algorithm
output. Include position value as a relationship property and
PageRank weights by it. Include INTERESTED_IN relationships from
enrichment and FastRP encodes richer neighborhoods. Different
projections of the same database produce different features.

Third, every algorithm supports four execution modes. Stream
returns results without persisting. Stats gives summary metrics.
Mutate adds results to the in-memory projection for chaining.
Write persists to the database. We will use mutate for chaining
and write for final output.
-->

---

## Five GDS Algorithm Categories

- **Centrality:** who is important (PageRank, Betweenness)
- **Community Detection:** who clusters together (Louvain, Label Propagation)
- **Similarity:** who resembles whom (Jaccard, Cosine)
- **Pathfinding:** how entities connect (Shortest Path, Dijkstra)
- **Node Embeddings:** vector representations for ML (FastRP, Node2Vec)

<!--
GDS organizes its 65+ algorithms into five categories. Centrality
answers who is important: PageRank, Betweenness Centrality.
Community Detection answers who clusters together: Louvain,
Label Propagation. Similarity answers who resembles whom: Jaccard,
Cosine. Pathfinding answers how entities connect: Shortest Path,
Dijkstra. Node Embeddings produce vector representations for ML:
FastRP, Node2Vec.

For this webinar we use algorithms from four of the five
categories: Node Embeddings (FastRP), Centrality (PageRank),
Community Detection (Louvain), and Similarity (Jaccard). The full
library gives you options to match your domain.
-->

---

## FastRP: What Graph Structure Captures

- **Structural vs semantic:** FastRP encodes graph topology (who holds what, who shares neighbors), not word meaning. Both produce vectors, but they capture fundamentally different information
- **What it captures for a customer:** which stocks held, which companies those belong to, how many neighbors share the same holdings
- **Every customer gets a feature vector,** including the 100 with no documents

<!--
The critical distinction before we look at the algorithm. FastRP
embeddings are structural, not semantic. A text embedding encodes
the meaning of words. A FastRP embedding encodes graph topology.
It does not know what "renewable energy" means. It knows that
Customer A is two hops from Stock X through Account Y and shares
three holding-neighbors with Customer B.

For each customer, FastRP captures the shape of their connections:
which stocks they hold, which companies those stocks belong to,
how many other customers hold the same stocks, and how those
neighbors connect outward in turn.

Every customer gets a feature vector. All 103, including the 100
with no profile documents. This is the key advantage over
document-based approaches: graph structure exists for every node,
not just the ones with text.
-->

---

## FastRP: Configuration and Output

- **Why FastRP:** works on any graph topology, requires no text, produces dense vectors encoding neighborhood structure
- **What it produces:** a 128-dimensional vector stored as a single `ArrayType` column. Each dimension captures some aspect of neighborhood structure
- **AutoML consumes array columns natively** for tree-based models (XGBoost, LightGBM). No manual flattening required — AutoML expands arrays internally during trial generation

<!--
FastRP, Fast Random Projection, works on any graph topology and
requires no text input. It produces a fixed-length dense vector
for every node in the projection.

A 128-dimensional embedding is stored as a single ArrayType column
containing 128 floats. No need to explode it into 128 separate
columns. Each dimension encodes some aspect of the node's
neighborhood: shared holdings, company connections, neighbor
overlap.

AutoML in Databricks consumes array columns natively. It expands
them internally during trial generation. You register the feature
table with the embedding column and AutoML handles the rest.
-->

---

## Additional Algorithms: PageRank, Louvain, Jaccard

- **PageRank centrality:** scores each node by influence. On the portfolio graph weighted by position value, high-PageRank stocks are broadly held at high values
- **Louvain community detection:** assigns every node to a community by optimizing modularity. Produces a single categorical feature column: the community ID
- **Node Similarity (Jaccard):** measures overlap in targets between pairs. Two customers sharing 3 of 4 interest sectors are more similar than two sharing 1 of 10
- These layer on top of FastRP: more features for the same classifier pipeline

<!--
FastRP captures neighborhood structure, but the graph has more
to say. PageRank centrality scores each node by influence.
Customers connected to many high-interest sectors score higher.
On the portfolio graph weighted by position value, high-PageRank
stocks are the ones broadly held at high values.

Louvain community detection assigns every node to a community by
optimizing modularity. It produces a single categorical feature
column: the community ID. On the base graph, communities form
around shared holdings. On the enriched graph, communities
incorporate interest and goal relationships.

Jaccard similarity measures overlap in targets between pairs. Two
customers sharing 3 of 4 interest sectors are more similar than
two sharing 1 of 10. All three algorithms layer on top of FastRP,
adding more features to the same classifier pipeline.
-->

---

## Chaining Algorithms with Mutate Mode

- **Mutate mode:** adds results to the in-memory projection without persisting to the database
- **Pipeline chaining:** PageRank output feeds into community detection, which feeds into similarity scoring
- **The entire feature pipeline runs in-memory** before writing final results
- **Write mode at the end** persists all results as node properties: `gds.fastRP.write`, `gds.pageRank.write`, `gds.louvain.write`

<!--
Mutate mode is the key to efficient algorithm chaining. Instead
of writing each algorithm's results to the database and reading
them back, mutate adds results to the in-memory projection. The
next algorithm in the chain consumes them directly.

PageRank output feeds into community detection, which feeds into
similarity scoring. The entire feature pipeline runs in-memory
on the projection. At the end, write mode persists all results
as node properties in a single pass. This avoids repeated disk
I/O and keeps the pipeline fast.
-->

---

## Example: Projecting the Portfolio Graph

```cypher
CALL gds.graph.project(
    'portfolio-graph',
    ['Customer', 'Account', 'Position', 'Stock'],
    {
        HAS_ACCOUNT:  { type: 'HAS_ACCOUNT',  orientation: 'UNDIRECTED' },
        HAS_POSITION: { type: 'HAS_POSITION', orientation: 'UNDIRECTED',
                        properties: ['positionValue'] },
        OF_SECURITY:  { type: 'OF_SECURITY',  orientation: 'UNDIRECTED' }
    }
)
```

- **Four node labels, three relationship types:** the full portfolio topology in one projection
- **`positionValue` on `HAS_POSITION`:** each customer's position has its own value, enabling weighted PageRank later
- **`UNDIRECTED`:** algorithms traverse in both directions

<!--
This is the actual projection call for the portfolio graph. Four
node labels capture the full entity set: Customer, Account,
Position, Stock. Three relationship types capture the connections
between them.

The positionValue property on HAS_POSITION is projected so that
PageRank can weight by dollar value later. Each customer's
position has its own value, so the property lives on HAS_POSITION,
not OF_SECURITY. Without projecting this property, PageRank
treats all relationships equally.

UNDIRECTED orientation means algorithms can traverse in both
directions. A customer reaches a stock through HAS_ACCOUNT,
HAS_POSITION, OF_SECURITY. The stock also reaches back to all
customers who hold it. This bidirectional traversal is what
lets FastRP encode shared-holding neighborhoods.
-->

---

## Example: Running FastRP on the Projection

```cypher
CALL gds.fastRP.write('portfolio-graph', {
    embeddingDimension: 128,
    writeProperty: 'embedding',
    iterationWeights: [0.0, 1.0, 1.0, 0.8]
})
```

- **`write` mode:** persists embeddings as node properties, ready for the Spark Connector
- **`iterationWeights`:** controls how much each hop contributes. Four weights = four hops deep
- **128 dimensions** stored as a single array property per node

<!--
One call, and every node in the projection gets a 128-dimensional
embedding persisted as a node property.

iterationWeights controls how much each hop contributes to the
embedding. Four weights means the algorithm looks four hops deep.
The first weight is 0.0, which means the node's own properties
are excluded. Weights of 1.0, 1.0, and 0.8 mean immediate
neighbors and two-hop neighbors contribute fully, while three-hop
neighbors contribute slightly less.

The result is a 128-dimensional array property on every node in
the projection. The Spark Connector reads these arrays into Delta
Lake Gold tables in the next step.
-->

---

## Example: What the Feature Table Looks Like

| Customer | Income | Portfolio Value | Embedding (128d)       | PageRank | Community |
|----------|--------|-----------------|------------------------|----------|-----------|
| Alice    | 95K    | 240K            | [0.12, -0.34, 0.71, ...] | 0.042    | 3         |
| Bob      | 88K    | 310K            | [0.11, -0.31, 0.68, ...] | 0.039    | 3         |
| Carol    | 62K    | 85K             | [-0.45, 0.22, -0.18, ...] | 0.008   | 7         |
| Dave     | 91K    | 275K            | [0.13, -0.29, 0.65, ...] | 0.037    | 3         |

- **Tabular features** (income, portfolio value) come from Delta Lake
- **Graph features** (embedding, PageRank, community) come from GDS
- **Alice, Bob, and Dave** have similar embeddings: they share holdings and neighbors in the graph
- **Carol's embedding points a different direction:** different neighborhood, different community

<!--
This is what the combined feature table looks like after the
Spark Connector reads GDS results into Gold tables. Each row is
a customer. The first two columns are tabular features from Delta
Lake. The last three columns are graph features from GDS.

Notice Alice, Bob, and Dave have similar embedding values. Their
vectors point in roughly the same direction because they share
holdings and neighbors in the graph. Carol's embedding is
different because her neighborhood structure is different.

The community column confirms it: Alice, Bob, and Dave are all
in community 3. Carol is in community 7. The classifier sees
both the continuous signal from embeddings and the categorical
signal from community ID.

This is the table that AutoML receives. Tabular and graph
features side by side, ready for classification.
-->

---

# The Bi-Directional Loop: Neo4j and Databricks

---

## GDS Results Flow to Gold Tables

- **Write mode to Neo4j:** `gds.fastRP.write` persists embedding vectors as node properties
- **Spark Connector to Gold tables:** reads enriched nodes back into Delta Lake Gold tables. Embedding vectors become columns alongside original customer attributes
- **Feature Engineering registration:** graph-derived features register in Feature Engineering in Unity Catalog alongside tabular features using `FeatureEngineeringClient`
- **Versioning:** Feature Engineering tracks which algorithm run produced which features

<!--
Once algorithms complete, write mode persists results as node
properties in Neo4j. FastRP embedding vectors, PageRank scores,
Louvain community IDs all become queryable properties immediately.
Cypher queries, GraphRAG traversals, and agent tools can use them.

The Spark Connector then reads those scored nodes back into
Delta Lake Gold tables. The FastRP embedding array, PageRank
score, and Louvain community ID become columns alongside
original customer attributes like income, credit score, and
portfolio value.

Graph-derived features register in Feature Engineering in Unity
Catalog using FeatureEngineeringClient. This gives you lineage,
governance, and versioning: you know which algorithm run
produced which features.
-->

---

## The Bi-Directional Data Flow

```
Neo4j GDS                    Spark Connector                  Databricks
+-----------------+          +---------------+          +-------------------+
| FastRP          |          |               |          | Gold Tables       |
| PageRank        |--write-->| Neo4j Spark   |--read--->| (Delta Lake)      |
| Louvain         |          | Connector     |          |                   |
| Node properties |          |               |<--write--| AutoML            |
+-----------------+          +---------------+          | predictions       |
                                                        +-------------------+
                                                               |
                                                        +-------------------+
                                                        | Feature           |
                                                        | Engineering in    |
                                                        | Unity Catalog     |
                                                        +-------------------+
```

<!--
This diagram shows the full data flow. GDS algorithms write
results as node properties in Neo4j. The Spark Connector reads
those properties into Delta Lake Gold tables. Graph-derived
features register in Feature Engineering in Unity Catalog
alongside tabular features.

AutoML trains on the combined feature table. The best model's
predictions write back through the Spark Connector as node
properties in Neo4j. The loop is fully bidirectional: graph
topology produces features, features train models, model
predictions become graph properties.
-->

---

## What AutoML Does and Why We Use It

- **The problem:** we have a table of customers with feature columns (graph embeddings, PageRank scores, community IDs, tabular attributes). Some customers already have a risk category assigned. Most do not
- **What AutoML does:** it learns the pattern from labeled customers and predicts risk categories for the rest. You point it at the table and tell it which column to predict
- **Why AutoML:** it evaluates multiple model families (XGBoost, LightGBM, logistic regression, random forests, decision trees), tunes hyperparameters, and selects the best performer automatically
- **No ML expertise required:** AutoML handles model selection, training, and evaluation. You provide the data and the target column

<!--
AutoML solves a specific problem. You have a feature table where
each row is a customer and each column describes something about
them: their FastRP embedding, PageRank score, Louvain community
ID, plus tabular attributes like income and portfolio value. Some
of these customers already have a risk category assigned by an
analyst. Most do not.

AutoML learns the pattern from the labeled customers: what
combination of features correlates with each risk category. Then
it predicts risk categories for the unlabeled customers.

The reason we use AutoML rather than picking a model ourselves is
that it evaluates five model families automatically: XGBoost,
LightGBM, logistic regression, random forests, and decision
trees. It tunes hyperparameters for each, runs trials, and
selects the best performer. You do not need to know which
algorithm works best for your data. AutoML finds out.
-->

---

## AutoML: Training and Prediction

```python
from databricks import automl

summary = automl.classify(
    dataset=feature_table,
    target_col="risk_category"
)
```

- **`target_col="risk_category"`:** the column AutoML learns to predict. AutoML trains on labeled rows only — rows with null targets are dropped
- **Prediction is a separate step:** load the best model, filter to unlabeled rows, and call `fe.score_batch()` to fill in missing risk categories
- **Predictions write back to Neo4j** via the Spark Connector, closing the loop

<!--
The API is two steps. First, automl.classify takes the feature
table and the name of the column you want to predict. AutoML
uses rows that already have a risk category to train. It splits
those into training and validation sets, evaluates all model
families, and logs every trial to MLflow.

Second, prediction is a separate step. Filter to unlabeled
customers and call fe.score_batch() with the registered model
URI. score_batch is a method on FeatureEngineeringClient that
requires the model to be logged with fe.log_model() first.
Predictions flow back to Neo4j via the Spark Connector as node
properties. Now every customer in the graph has a risk category:
either analyst-assigned or model-predicted.

The loop is fully closed. Graph topology produced the features.
The features trained a classifier. The classifier's predictions
become graph properties that agents and algorithms can reason
over in the next cycle.
-->

---

## The Two-System Payoff

- **The classifier fills structural gaps:** missing risk categories predicted from graph topology
- **The LLM fills semantic gaps:** interests and goals extracted from documents
- **Each makes the other's job easier** in the next cycle: richer graph features produce better classifiers, better predictions produce richer agent context

<!--
Two systems, complementary contributions. The classifier fills
structural gaps: it predicts missing risk categories using graph
topology. Customers who look similar in the graph, similar
holdings, similar neighborhood structure, likely share a risk
category. The classifier discovers that pattern.

The LLM fills semantic gaps: it extracts interests and goals from
documents that no algorithm can parse. Together, each makes the
other's job easier. Richer graph features produce better
classifiers. Better predictions give agents more structured
context to reason over. The cycle compounds.
-->

---

## Key Databricks APIs for the Loop

| Step | API / Tool | Purpose |
|---|---|---|
| Register features | `FeatureEngineeringClient` | Register graph-derived features in Unity Catalog |
| Train classifier | `databricks.automl.classify()` | Evaluate model families on combined feature table |
| Score predictions | `score_batch()` | Predict labels for unlabeled entities |
| Write back | Neo4j Spark Connector | Push predictions to Neo4j as node properties |

<!--
Four key APIs in the Databricks side of the loop.
FeatureEngineeringClient registers graph-derived features in
Unity Catalog alongside tabular features. The automl.classify
call accepts the feature table and evaluates all model families.
score_batch generates predictions for unlabeled entities using
the best model. And the Spark Connector writes those predictions
back to Neo4j as node properties.

This is the complete API surface for the Databricks side of the
bi-directional loop. Each step is a single function call.
-->

---

## Lakeflow Jobs Pipeline

- **Lakeflow Jobs** chains the full loop as tasks:

1. **Extract** changed graph data to Delta tables
2. **Run enrichment agents** on changed documents
3. **Write approved enrichments** to Neo4j
4. **Run GDS algorithms** on the enriched graph
5. **Extract scores** to Gold tables
6. **Register updated features** in Feature Engineering in Unity Catalog

- **Human-in-the-loop** checkpoints can gate any step

<!--
Lakeflow Jobs is Databricks' workflow orchestration service. It
lets you define a pipeline as a directed acyclic graph of tasks,
where each task is a notebook, Python script, SQL query, or other
compute unit. Tasks can depend on each other, run in parallel
where dependencies allow, and retry on failure. You configure
schedules, alerts, and permissions through the Lakeflow Jobs UI
or the REST API.

For this pipeline, each step in the feature engineering loop
becomes a task. Extract pulls changed graph data into Delta
tables. Enrichment agents analyze changed documents against
current graph state. Approved enrichments write back to Neo4j.
GDS algorithms run on the updated graph. Scores extract to Gold
tables. Updated features register in Feature Engineering in
Unity Catalog.

Human-in-the-loop checkpoints can gate any step in the chain.
During early cycles, you might gate the write-back step so data
architects review proposals before they reach the graph. As
confidence grows, those gates shift to exception handling rather
than full review.
-->

---

# Quantifying Lift

---

## Baseline: Tabular Features Only

- **Train a baseline model:** point AutoML at a feature table with only Delta Lake features: demographics, balances, transaction history
- **Record AUC, precision, recall:** this is the benchmark to beat
- **What the baseline sees:** each customer described in isolation by their own attributes
- **What the baseline misses:** which customers cluster together, who bridges separate groups, who occupies similar network positions

<!--
The way to prove graph features matter is to measure the
difference. Start with a baseline. Point AutoML at a feature
table that contains only tabular features from Delta Lake:
annual income, credit score, portfolio value, transaction counts.
Record AUC, precision, and recall.

This baseline sees each customer described in isolation by their
own attributes. It has no visibility into structural patterns:
which customers cluster together, who bridges separate groups,
who shares similar holdings. Those patterns are encoded in graph
topology, not in table columns.
-->

---

## Graph-Augmented: Measuring the Lift

- **Add graph features:** FastRP embeddings, PageRank scores, community ID, Jaccard similarity to the same feature table. Run AutoML again
- **What graph features capture:** community membership and centrality scores encode structural patterns invisible to flat tables
- **Published benchmark:** as one reference point, Neo4j's fraud detection benchmark showed significant improvement in detection rates when graph features were added. Lift varies by domain, and the demo measures it directly on the portfolio dataset
- **MLflow side-by-side:** both runs are MLflow experiments. Feature importance plots show which graph features drove the lift

<!--
Now add graph features to the same table and run AutoML again.
FastRP embeddings, PageRank scores, Louvain community IDs, and
Jaccard similarity scores sit alongside the tabular features.
The same model families compete on richer data.

Graph features capture structural patterns that flat tables cannot
see. Community membership reveals which customers cluster together.
Centrality scores reveal who bridges separate groups. These are
signals that no column in a Delta table encodes.

As one reference point, Neo4j's fraud detection benchmark showed
significant improvement in detection rates when graph features
were added. Lift varies by domain. The demo measures it directly
on the portfolio dataset so you see the actual numbers for this
use case.

Both AutoML runs are MLflow experiments. The experiment comparison
UI shows metrics side-by-side. Feature importance plots show
exactly which graph features drove the improvement.
-->

---

## MLflow Experiment Tracking: Comparing Runs

- **Every AutoML trial is an MLflow run:** parameters, metrics (AUC, precision, recall, F1), and artifacts are logged automatically — no manual instrumentation
- **Two experiments, one comparison:** the baseline experiment (tabular only) and the graph-augmented experiment appear side by side in the MLflow Experiments UI
- **Metric comparison across runs:** the Experiments page lets you sort by AUC or any metric and compare the best run from each experiment directly
- **Trial notebook generation:** AutoML generates a source code notebook for the best trial, so the team can review, reproduce, and modify the winning model

<!--
This is where you see the lift in concrete terms. Every trial
AutoML runs becomes an MLflow run with parameters, metrics, and
artifacts logged automatically. You do not instrument anything
yourself.

The baseline experiment and the graph-augmented experiment are
separate MLflow experiments. The Experiments UI shows them side
by side. You can sort by AUC, F1, or any metric and compare the
best run from each experiment directly.

AutoML also generates a source code notebook for the best trial
in each experiment. These notebooks are fully reproducible: you
can re-run them, modify hyperparameters, or add feature
engineering steps. Everything is transparent and auditable.
-->

---

## Feature Importance with SHAP Values

- **SHAP (Shapley values):** AutoML trial notebooks include SHAP code that scores each feature's contribution to predictions. Game-theory-based — measures how much each feature shifts the model's output
- **What SHAP reveals for graph features:** do FastRP embedding dimensions, PageRank scores, or Louvain community IDs actually move the needle, or does the model ignore them?
- **The proof:** if graph features appear in the top SHAP contributors alongside income and portfolio value, graph enrichment is earning its place. If they don't, you know to revisit the projection or algorithm choice
- **Actionable feedback loop:** SHAP results tell you which GDS algorithms to keep, tune, or replace in the next enrichment cycle

<!--
MLflow tracking shows the numbers improved. SHAP shows why.

AutoML trial notebooks include SHAP code out of the box. You
set shap_enabled to True and re-run the cell. SHAP calculates
each feature's contribution to every prediction using game
theory: how much does adding this feature change the model's
output compared to leaving it out?

For graph features specifically, SHAP answers the critical
question: do FastRP embedding dimensions, PageRank scores, and
Louvain community IDs actually contribute to the classifier, or
does the model ignore them? If graph features rank among the top
SHAP contributors alongside income and portfolio value, graph
enrichment is earning its place.

If they do not rank highly, that is equally valuable information.
It tells you to revisit the projection configuration, try
different algorithm parameters, or add more relationship types.
SHAP turns model evaluation into an actionable feedback loop for
the next GDS enrichment cycle.
-->

---

## Compounding Returns Across Cycles

- **Each enrichment cycle** produces more relationships for algorithms to operate on
- **AutoML retraining after Cycle 2** uses richer features than Cycle 1. MLflow experiment tracking compares model performance across cycles
- **The lift is not static:** embeddings after Cycle 2 encode richer topology than Cycle 1, reflecting relationships that did not exist before enrichment

<!--
The lift is not a one-time improvement. Each enrichment cycle
writes new relationships to the graph: INTERESTED_IN, HAS_GOAL,
and others. Those relationships change what FastRP encodes. The
embeddings after Cycle 2 are richer than after Cycle 1 because
they reflect relationships that did not exist before the first
enrichment pass.

AutoML retraining on the richer feature set produces better
models. MLflow experiment tracking lets you compare performance
across cycles. You can see the improvement compound over time.
-->

---

# Sync Strategies and Orchestration

---

## Incremental Sync with Change Data Feed

- **Change Data Feed:** enable on Gold tables with `delta.enableChangeDataFeed = true`. Only changes after enablement are captured
- **Structured Streaming:** a Spark Structured Streaming job detects new customers and positions, pushes deltas to Neo4j via the Spark Connector
- **Incremental enrichment triggers:** customer profile updates re-analyze that customer only. New market research triggers batch analysis of that document type
- **Cost proportional to change volume,** not total data volume

<!--
Running full analysis across all customers after every update is
prohibitively expensive. Change Data Feed on Delta tables enables
incremental processing. You enable it per table with the
delta.enableChangeDataFeed property set to true. Only changes
made after enablement are captured, so enable it before the
pipeline starts writing.

A Spark Structured Streaming job picks up changes and pushes
only the delta to Neo4j through the Spark Connector. No full
reloads. On the enrichment side, document triggers control what
gets reprocessed. A customer profile update re-analyzes that
customer only. New market research triggers batch analysis of
that document type. Costs stay proportional to what changed.
-->

---

# Scaling and Closing

---

## SEC EDGAR: Proving the Pattern at Scale

- **The dataset:** 3,906 asset managers, 28,960 companies, 590,538 equity holdings from 2021 quarterly SEC filings
- **Structurally identical graph model:** Manager to Holding to Company mirrors Customer to Position to Stock
- **What it proves:** the same FastRP + classifier pattern scales to a significantly larger graph
- **Companion notebook:** GDS computes features on 590K holdings, AutoML trains a classifier to predict whether a manager will increase or decrease a holding, predictions flow back

<!--
Everything demonstrated on 103 customers works at scale. The SEC
EDGAR dataset contains 3,906 asset managers, 28,960 companies,
and 590,538 equity holdings from 2021 quarterly filings. The graph
model is structurally identical: Manager to Holding to Company
mirrors Customer to Position to Stock.

A companion notebook applies the same pattern. GDS computes
FastRP embeddings on the full graph. AutoML trains a classifier
to predict whether a manager will increase or decrease a holding
in the next quarter. Predictions flow back to Neo4j. Same
algorithms, same pipeline, significantly more data.
-->

---

## Compounding Cycles

- **Cycle 1, obvious gaps:** early cycles capture straightforward missing relationships. INTERESTED_IN makes intent a first-class graph entity alongside transactional data
- **Cycle 2, algorithmic discovery:** Jaccard similarity identifies clusters. Louvain reveals organic segments no one designed upfront. These algorithms operate on relationships that did not exist before Cycle 1
- **Cycle 3+, cross-referencing new data:** new documents cross-reference against interest communities that only became visible through earlier enrichments
- **The distinction:** entity extraction asks "what does this document say?" Agentic enrichment asks "what relationships are missing?" That question, repeated across cycles, compounds

<!--
Each enrichment cycle changes what the next cycle discovers.
Cycle 1 captures obvious gaps: INTERESTED_IN relationships make
customer intent a first-class graph entity alongside transactional
holdings data.

Cycle 2 starts from a richer graph. Jaccard similarity identifies
clusters of customers with similar interest profiles. Louvain
reveals organic segments no one designed upfront. These algorithms
operate on relationships that did not exist before the first cycle.

Cycle 3 and beyond cross-reference newly ingested documents
against interest communities that only became visible through
earlier enrichments. The matches span customer preference,
portfolio gap, and market opportunity.

The fundamental distinction: entity extraction asks what does
this document say. Agentic enrichment asks what relationships
are missing. That question, repeated across cycles, compounds
into organizational memory.
-->

---

## Key Takeaways

- **Graph features capture what flat tables miss:** network position, community membership, centrality, structural similarity
- **Feature Engineering in Unity Catalog + AutoML** trains classifiers on the combined picture: graph-derived and tabular features together
- **The loop is bi-directional:** GDS scores flow to Gold tables, model predictions flow back to Neo4j via the Spark Connector
- **Lift is measurable and compounding:** each enrichment cycle produces richer features, and MLflow tracks the improvement
- **Lakeflow Jobs orchestrates the full pipeline** end-to-end with incremental sync via Change Data Feed

<!--
Five things to take away. First, graph features capture structural
patterns that flat tables miss: network position, community
membership, centrality scores, and structural similarity.

Second, Feature Engineering in Unity Catalog and AutoML train
classifiers on the combined picture. Graph-derived features sit
alongside tabular features in the same governed feature table.

Third, the loop is fully bi-directional. GDS scores flow to Gold
tables. Model predictions flow back to Neo4j. The Spark Connector
handles both directions.

Fourth, lift is measurable and it compounds. Each enrichment cycle
produces more relationships for algorithms to encode. MLflow
experiment tracking shows the improvement across cycles.

Fifth, Lakeflow Jobs orchestrates the full pipeline end-to-end.
Change Data Feed keeps the sync incremental. Costs stay
proportional to what changed, not total data volume.
-->
