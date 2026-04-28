# Graph Feature Engineering with Neo4j GDS and Databricks — Talk Notes

## Overview: The Arc of This Talk

Here is the full story we are telling today, from start to finish.

We begin with tabular data: accounts, merchants, transactions. Flat rows in Delta
tables. Individually, those rows tell you what happened — account 42 sent $3,000
to account 17. What they cannot tell you is whether that transfer is part of a
coordinated pattern, whether account 42 sits at the center of a ring of connected
accounts all routing money through the same intermediaries, whether a cluster of
accounts shares the same high-risk merchants and the same off-hours activity.
That information lives in the relationships, not the columns.

The first move is to load that tabular data into Neo4j Aura and let it become a
graph. Accounts become nodes. Merchants become nodes. TRANSACTED_AT and
TRANSFERRED_TO become edges carrying the transaction details. What was a flat
table is now a network you can traverse.

Once the data is in the graph, we run Neo4j Graph Data Science algorithms against
it. Three algorithms, three new signals:

- **PageRank** scores each account by how central it is to the peer-to-peer
  transfer network. A high-risk score means money from many accounts is funnelling
  through this node — the classic aggregation pattern before a cashout.
- **Louvain community detection** partitions the network into clusters. Fraud
  rings show up as unusually small, dense communities: a handful of accounts with
  a disproportionate share of internal transfer edges relative to their external
  connections.
- **Node Similarity** finds accounts that share transfer counterparties without
  a direct link between them. Two accounts coordinating through shared
  intermediaries score high — a pattern flat-table features cannot surface at all.

These three scores — risk_score, community_id, similarity_score — are things a
tabular model will never see because they don't exist in any single row. They
emerge from the structure of the graph.

Those scores write back to the Account nodes in Neo4j as properties. Then the
Spark Connector reads them into Databricks as Gold table columns, sitting
alongside the original tabular features: balance, account type, region,
transaction counts, average amounts.

Now the feature table is complete. We hand it to the Databricks ML platform.
Feature Engineering in Unity Catalog governs the feature table with lineage and
versioning. MLflow runs two experiments side by side: one trained on tabular
features only, one with the graph features added. The accuracy delta is the lift
graph topology contributes — concrete and measurable, not theoretical.

The best classifier's predictions write back to Neo4j through the Spark Connector,
so every account node carries a fraud probability alongside its graph scores. The
loop is fully bi-directional.

The final piece is scale. Once the graph-enriched model is trained, Databricks
applies it on ingest. New transactions arriving in Delta tables are scored
immediately using the model — no manual Cypher, no rerunning the full pipeline.
The graph intelligence trained offline runs at lakehouse scale in real time.

**Five things this talk demonstrates:**

1. **Graph features capture what flat tables miss:** network position, community
   membership, centrality, structural similarity — all invisible to row-level analysis.
2. **Feature Engineering in Unity Catalog + MLflow** trains classifiers on the
   combined picture: graph-derived and tabular features together in a single
   governed feature table.
3. **The loop is bi-directional:** GDS scores flow to Gold tables via the Spark
   Connector; model predictions flow back to Neo4j as node properties.
4. **Lift is measurable:** MLflow experiment tracking shows exactly how much
   accuracy the graph features add over tabular features alone.
5. **Graph enrichment scales with Databricks:** the graph-enriched model is
   deployed as a serving endpoint and applied to data at scale on ingest — graph
   intelligence without per-record Cypher queries.

---

## Partnership Overview and Recap

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

## What You'll Learn

Five things by the end of this session. First, what graph feature
engineering actually is and why it matters. Second, which GDS
algorithms produce useful features. Third, the full loop between
Neo4j and Databricks. Fourth, how to measure whether graph features
actually improve a classifier. Fifth, how to keep the two systems
in sync without manual intervention.

## The Dual Architecture for This Use Case

Let's start with what lives where. This is the same dual
architecture from the first webinar, applied to the portfolio
use case.

Databricks holds the analytical layer. Delta tables contain
customer demographics and transaction history. UC Volumes store
unstructured documents: customer profiles and investment research.

Neo4j holds the relationship layer. The portfolio topology runs
from Customer to Account to Position to Stock. Document nodes
with vector embeddings bridge unstructured content into the
graph, so text and structure live side by side.

## Graph-Enriched Retrieval

The graph data pipeline analyzed customer profiles to extract
interests, goals, and concerns. Those entities became nodes
linked to customers with relationships like INTERESTED_IN,
HAS_GOAL, and CONCERNED_ABOUT. These relationships didn't exist
in the raw data.

GraphRAG combines both layers. Vector search finds the chunks
most relevant to the user's question. Graph traversal follows
extracted entities from those chunks into the operational data.
The agent receives structured holdings alongside document context
in a single response.

This works well for questions that documents can answer. But it
has a coverage limit, which is where we're headed next.

## The GraphRAG Gap

Here is the concrete problem. Semantic search can now find
customers by risk profile because the pipeline linked profiles
to customer nodes. GraphRAG retrieves across that structure
beautifully.

But only some customers have profile documents. For the
remaining customers, there is nothing for vector search to find, which
means there are no starting points for graph traversal.

The graph itself still encodes useful information about those
remaining customers: their portfolio connections, account
structures, and relationships to stocks and sectors. But GraphRAG
cannot surface structural patterns because it enters the graph
through text, not through topology. We need a different approach
for the rest.

## What's Missing: Structural Similarity

The unlabeled customers are not empty rows. They have accounts,
positions, stocks, sector connections. The same topology as the
labeled customers. The structure is there,
just no documents.

The intuition is straightforward: customers with similar
portfolios likely share similar risk profiles. If Alice holds
the same stocks as Bob and Alice is labeled high-risk, Bob
probably is too. The pattern is in the graph structure, not
in any document.

What we need is a way to quantify that structural similarity
across the entire graph and use it to classify the unlabeled
customers. That is exactly what graph feature engineering does.

## The Solution: Graph Feature Engineering

This is the core idea for the rest of the webinar. What if we
could group customers by the structure of their connections?
Customers who hold similar stocks, connect to similar sectors,
and share graph neighbors likely belong in the same risk
category.

Neo4j Graph Data Science computes these from the graph: which
group a customer belongs to, how influential they are in the
network, and a numeric fingerprint of their connections. Think
of it as a summary of who they're connected to, compressed into
numbers. Customers with similar fingerprints have similar
connection patterns. These computed values become the features
an ML model trains on.

An ML model trained on the labeled customers learns which
feature patterns correspond to which risk category, then
predicts labels for the rest. Those predictions write back to
Neo4j through the Spark Connector. Now every customer has a
risk classification, even without a profile document.

## What Are Features and Classifiers?

Quick vocabulary for anyone new to ML terminology. A feature is
a column that describes something about an entity. It can be
numeric like age or balance, or categorical like community
membership. A classifier takes rows of features and learns to
predict a label.

Feature engineering is the process of creating new features from
raw data. Graph feature engineering uses relationships and
network structure to create new features: who connects to whom,
who shares neighbors, who belongs to which community. These
structural features capture information that no single table
column encodes.

## Example: Features and Classification

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

## GDS Foundations

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

## Five GDS Algorithm Categories

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

## FastRP: Capturing Graph Structure

FastRP compresses a customer's connections into numbers: which
stocks they hold, which accounts link where, how their neighbors
overlap with other customers.

Two customers who hold the same stocks through similar account
structures produce similar fingerprints because they occupy
similar positions in the graph.

And every customer gets a fingerprint, including those with no
profile documents. Graph structure exists for every node, not
just the ones with text. That is what closes the coverage gap
we identified earlier.

## Example: Projecting the Portfolio Graph

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

## Example: Running FastRP on the Projection

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

## Example: What a Node Looks Like After GDS

After the algorithm pipeline completes, each Customer node carries
three new properties alongside its original attributes. The
embedding array is the FastRP graph fingerprint. The pageRank
score reflects influence in the portfolio network. The communityId
is the Louvain cluster assignment.

These properties are written directly to Neo4j by the GDS write
calls we just saw. They are immediately queryable. A Cypher query
can filter customers by community. A GraphRAG traversal can use
pageRank to prioritize high-influence nodes. An agent tool can
retrieve the embedding for similarity comparison.

In the next section, the Spark Connector reads these enriched
nodes back into Delta Lake Gold tables, combining graph properties
with tabular features for classifier training.

## Spark Connector Brings Results to Gold Tables

The Spark Connector then reads those enriched nodes back into
Delta Lake Gold tables. The embedding array, PageRank score,
and community ID become columns alongside original customer
attributes like income and portfolio value.

The result is a feature table in Unity Catalog that combines
graph-derived and tabular columns. That feature table is what
the classifier trains on in the next step. Unity Catalog tracks
lineage and versioning, so you know which algorithm run produced
which features and which model version consumed them.

## What the Feature Table Looks Like

The combined feature table holds everything the classifier needs
in a single row per customer. The tabular columns — income and
portfolio value — come from Delta Lake. The graph columns —
embedding array, PageRank score, and community ID — come from
GDS write output read back through the Spark Connector.

Customers with similar portfolio topology produce embeddings that
point in the same direction. Two customers who hold the same
stocks through similar account structures occupy similar positions
in the graph, so their fingerprints align. That alignment is
invisible in a flat table but captured by the embedding.

Community ID adds a categorical signal on top. Customers who
cluster together in the graph share dense connections and end up
in the same community. The classifier sees both the continuous
signal from embeddings and the categorical signal from community
ID — two complementary views of the same structural similarity.

This combined table is what the classifier receives. Graph-derived
and tabular features together, ready for training.

## What Is a Classifier?

A classifier is a type of ML model that assigns categories to
data. You give it examples where you already know the answer,
and it learns which feature patterns map to which categories.
Once trained, it applies those patterns to rows where the answer
is unknown.

In our portfolio example, some customers already have risk
categories assigned by an analyst through their profile documents.
The classifier learns from those labeled customers and predicts
High, Medium, or Low risk for the remaining customers who have
no documents. That is how we close the coverage gap from earlier.

## Training a Classifier on Graph Features

The classifier receives the feature table we just built. Some
customers already have risk categories assigned by an analyst.
The classifier learns which feature patterns correspond to each
category, then predicts categories for the remaining customers.

Several classifiers each train on the same data. Each finds
patterns differently. Running them all reveals which approach
fits best for this dataset.

## The Bi-Directional Data Flow

Now you can see the full loop. GDS algorithms write results as
node properties in Neo4j. The Spark Connector reads those
properties into the feature table. Classifiers train on the
feature table and the best model's predictions write back
through the Spark Connector as node properties in Neo4j. The
loop is fully bidirectional: graph topology produces features,
features train models, model predictions become graph properties.

## What Is MLflow?

We just trained several classifiers on the combined feature table.
That raises two questions: which classifier performed best, and
did the graph features actually help? MLflow answers both.

MLflow is Databricks' experiment tracking platform. It
automatically logs parameters, accuracy metrics, and the trained
model for every run. No manual logging code needed.

The key use for us is comparing two experiments side by side:
one trained with only tabular features, one with graph features
added. That comparison tells us exactly how much lift graph
topology contributes.

## Measuring Graph Feature Lift with MLflow

This is the comparison we set up on the previous slide. MLflow
tracks two experiments against the same feature table.

The baseline experiment trains classifiers with only tabular
features: income, portfolio value, and other attributes from
Delta Lake. This establishes the benchmark.

The graph-enhanced experiment trains the same classifiers with
graph features added: FastRP embeddings and Louvain community
IDs. MLflow shows both experiments side by side. The difference
in accuracy tells you exactly how much graph topology
contributes on top of what tabular features already provide.

## How Classifiers and LLMs Work Together

Two systems, complementary contributions. The classifier fills
structural gaps: it predicts missing risk categories using graph
topology. Customers who look similar in the graph, similar
holdings, similar neighborhood structure, likely share a risk
category. The classifier discovers that pattern.

The LLM fills semantic gaps: it extracts interests and goals from
documents that no algorithm can parse. Together, each improves
the other. The LLM-extracted relationships from enrichment make
the graph richer, which gives GDS algorithms more structure to
work with, which produces better classifier features. The
classifier's predictions become node properties that give agents
more structured context to reason over. The cycle compounds with
each iteration.

## Lakeflow Jobs Pipeline

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

## Incremental Sync with Change Data Feed

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

## Key Takeaways

Five things to take away. First, graph features capture structural
patterns that flat tables miss: network position, community
membership, centrality scores, and structural similarity.

Second, Feature Engineering in Unity Catalog and scikit-learn
train classifiers on the combined picture. Graph-derived features sit
alongside tabular features in the same governed feature table.

Third, the loop is fully bi-directional. GDS scores flow to Gold
tables. Model predictions flow back to Neo4j. The Spark Connector
handles both directions.

Fourth, lift is measurable. MLflow experiment tracking shows
exactly how much accuracy graph features add over tabular
features alone.

Fifth, Lakeflow Jobs orchestrates the full pipeline end-to-end.
Change Data Feed keeps the sync incremental. Costs stay
proportional to what changed, not total data volume.
