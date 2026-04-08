# Graph Feature Engineering with Neo4j GDS and Databricks

Feature Engineering in Unity Catalog + AutoML

## Partnership Overview and Recap

- **Joint Customer Base:** over 200 shared customers across Aura and Enterprise, including Gilead, iFord, Comcast, and Ashley Furniture
- **Neo4j Spark Connector (5.x):** bidirectional data transfer between Databricks Lakehouse and Neo4j, supporting Unity Catalog and Delta tables. Silver tables feed the graph; Gold tables capture graph insights
- **Connection Patterns:** Spark Connector for batch pipelines, Unity Catalog JDBC for governed SQL and BI federation, Neo4j MCP Server for agent-driven Cypher, neo4j-graphrag-python for knowledge graph construction
- **Previous webinar:** built a knowledge graph from unstructured documents, then used GraphRAG to combine vector search with graph traversal so agents receive richer context than text search alone

## What You'll Learn

- What feature engineering is and why graph structure produces features flat tables cannot
- How Neo4j GDS algorithms generate features from graph topology
- The bi-directional pattern: GDS features flow to Feature Engineering in Unity Catalog, AutoML predictions flow back to Neo4j
- How to measure the lift graph features add to a classifier
- Sync strategies for keeping Neo4j and Databricks aligned

## Recap: Graph-Enriched Retrieval

- **Data pipeline complete:** Spark Connector projected Delta tables into graph nodes and relationships
- **KG construction complete:** documents chunked, embedded, entity-extracted into the graph
- **Search finds the starting points:** chunks closest in meaning to the question
- **Graph traversal enriches:** follows entities and relationships from those chunks into the operational graph
- **Agents receive richer context** than text search alone: structured data alongside document content

## The Dual Architecture for This Use Case

- **Databricks holds the analytical layer:** Delta tables with customer demographics (income, credit score, portfolio value) and transaction history, plus UC Volumes with unstructured documents (customer profiles, investment guides, market analyses)
- **Neo4j holds the relationship layer:** Customer → Account → Position → Stock portfolio topology, plus enrichment relationships from document analysis (INTERESTED_IN, HAS_GOAL, CONCERNED_ABOUT)
- **The Spark Connector bridges both directions:** Silver tables seed the graph; graph algorithm results flow back to Gold tables
- **Each system does what it's best at:** Databricks runs SQL aggregations, AutoML, and Feature Engineering. Neo4j runs GDS algorithms, pattern matching, and GraphRAG retrieval

## What the Graph Contains: Three Layers

- **Operational graph (from Delta tables):** 103 Customers, their Accounts, Positions, and the Stocks those positions hold. The Spark Connector built this from governed Silver tables
- **Enrichment layer (from document analysis):** INTERESTED_IN, HAS_GOAL, CONCERNED_ABOUT — relationships LLM agents extracted from customer profiles and market documents. Only 3 of 103 customers have profile documents
- **Document layer (for GraphRAG):** Document → Chunk nodes with embeddings and extracted entities (Interest, Goal, Sector) cross-linked to operational nodes
- **GDS operates on any combination** of these layers through projection configuration. The projection you build determines the features you get

## What Graph-Enriched Search Doesn't Capture

- **GraphRAG works well for documents:** chunking, embedding, entity extraction, retrieval with graph context
- **Structural patterns are missing:** which customers cluster together, who holds similar portfolios, what risk categories apply
- **These patterns live in graph topology,** not in document text: no amount of vector search will find them

# Foundations: Features and Classifiers

## What Are Features and Classifiers?

- **Feature:** a column describing an entity: age, balance, number of connections, or a category like community membership
- **Classifier:** takes rows of features and predicts a label like risk category. Features in, label out
- **Feature engineering:** creating new, informative features from raw data
- **Graph feature engineering:** the graph's structure (who connects to whom) becomes columns a classifier can learn from

## Example: Features and Classification

- **Alice:** Income 95K, Portfolio Value 240K, Community 3, Risk Category **High**
- **Bob:** Income 88K, Portfolio Value 310K, Community 3, Risk Category **High**
- **Carol:** Income 62K, Portfolio Value 85K, Community 7, Risk Category **Low**
- **Dave:** Income 91K, Portfolio Value 275K, Community 3, Risk Category **???**
- **Columns are features:** income, portfolio value, and community ID each describe something about a customer
- **Risk category is the label** the classifier learns to predict
- **Dave looks like Alice and Bob:** similar income, similar portfolio, same community. The classifier predicts **High**

## The Problem: The 3-of-103 Gap

- **The 3-of-103 problem:** a standard agent can discover customer interests by reading profile documents, but only 3 of 103 customers have documents. The other 100 have holdings data and tabular attributes with no text
- **What a classifier needs:** features that capture structural patterns: which customers cluster together, who holds similar portfolios, who bridges separate groups
- **The gap:** we need features that capture network position, not just individual attributes

## The Solution: Neo4j GDS + Feature Engineering in Unity Catalog

- **Neo4j GDS:** 65+ graph algorithms that turn topology into features: embeddings, scores, community IDs
- **Feature Engineering in Unity Catalog + AutoML:** consumes graph features alongside tabular data, trains classifiers, selects the best model
- **Neo4j Spark Connector:** the bridge: bidirectional data transfer between the two systems
- **Together:** GDS computes what flat tables cannot see; Feature Engineering + AutoML trains models on the combined picture

# GDS Feature Engineering

## GDS Foundations

- **Graph projections:** algorithms run on in-memory projections, not the live database. A projection selects specific node labels and relationship types, creating an optimized in-memory copy
- **Projection configuration:** which node labels, relationship types, and relationship properties you include determines the features you get. Different projections of the same graph produce different results
- **Execution modes:** stream (return results), stats (summary only), mutate (add to projection for chaining), write (persist to database)

## Five GDS Algorithm Categories

- **Centrality:** who is important (PageRank, Betweenness)
- **Community Detection:** who clusters together (Louvain, Label Propagation)
- **Similarity:** who resembles whom (Jaccard, Cosine)
- **Pathfinding:** how entities connect (Shortest Path, Dijkstra)
- **Node Embeddings:** vector representations for ML (FastRP, Node2Vec)

## FastRP: What Graph Structure Captures

- **Structural vs semantic:** FastRP encodes graph topology (who holds what, who shares neighbors), not word meaning. Both produce vectors, but they capture fundamentally different information
- **What it captures for a customer:** which stocks held, which companies those belong to, how many neighbors share the same holdings
- **Every customer gets a feature vector,** including the 100 with no documents

## FastRP: Configuration and Output

- **Why FastRP:** works on any graph topology, requires no text, produces dense vectors encoding neighborhood structure
- **What it produces:** a 128-dimensional vector stored as a single ArrayType column. Each dimension captures some aspect of neighborhood structure
- **AutoML consumes array columns natively** for tree-based models (XGBoost, LightGBM). No manual flattening required — AutoML expands arrays internally during trial generation

## Additional Algorithms: PageRank, Louvain, Jaccard

- **PageRank centrality:** scores each node by influence. On the portfolio graph weighted by position value, high-PageRank stocks are broadly held at high values
- **Louvain community detection:** assigns every node to a community by optimizing modularity. Produces a single categorical feature column: the community ID
- **Node Similarity (Jaccard):** measures overlap in targets between pairs. Two customers sharing 3 of 4 interest sectors are more similar than two sharing 1 of 10
- These layer on top of FastRP: more features for the same classifier pipeline

## Chaining Algorithms with Mutate Mode

- **Mutate mode:** adds results to the in-memory projection without persisting to the database
- **Pipeline chaining:** PageRank output feeds into community detection, which feeds into similarity scoring
- **The entire feature pipeline runs in-memory** before writing final results
- **Write mode at the end** persists all results as node properties

## Example: Projecting the Portfolio Graph

- **Projection call:** gds.graph.project creates an in-memory projection named 'portfolio-graph'
- **Four node labels:** Customer, Account, Position, Stock — the full portfolio topology
- **Three relationship types:** HAS_ACCOUNT, HAS_POSITION (with positionValue property), OF_SECURITY
- **positionValue on HAS_POSITION:** each customer's position has its own value, enabling weighted PageRank later
- **UNDIRECTED orientation:** algorithms traverse in both directions

## Example: Running FastRP on the Projection

- **Call:** gds.fastRP.write on the 'portfolio-graph' projection
- **Write mode:** persists embeddings as node properties, ready for the Spark Connector
- **iterationWeights [0.0, 1.0, 1.0, 0.8]:** controls how much each hop contributes. Four weights = four hops deep
- **128 dimensions** stored as a single array property per node

## Example: What the Feature Table Looks Like

- **Alice:** Income 95K, Portfolio Value 240K, Embedding [0.12, -0.34, 0.71, ...], PageRank 0.042, Community 3
- **Bob:** Income 88K, Portfolio Value 310K, Embedding [0.11, -0.31, 0.68, ...], PageRank 0.039, Community 3
- **Carol:** Income 62K, Portfolio Value 85K, Embedding [-0.45, 0.22, -0.18, ...], PageRank 0.008, Community 7
- **Dave:** Income 91K, Portfolio Value 275K, Embedding [0.13, -0.29, 0.65, ...], PageRank 0.037, Community 3
- **Tabular features** (income, portfolio value) come from Delta Lake
- **Graph features** (embedding, PageRank, community) come from GDS
- **Alice, Bob, and Dave** have similar embeddings: they share holdings and neighbors in the graph
- **Carol's embedding points a different direction:** different neighborhood, different community

# The Bi-Directional Loop: Neo4j and Databricks

## GDS Results Flow to Gold Tables

- **Write mode to Neo4j:** gds.fastRP.write persists embedding vectors as node properties
- **Spark Connector to Gold tables:** reads enriched nodes back into Delta Lake Gold tables. Embedding vectors become columns alongside original customer attributes
- **Feature Engineering registration:** graph-derived features register in Feature Engineering in Unity Catalog alongside tabular features using FeatureEngineeringClient
- **Versioning:** Feature Engineering tracks which algorithm run produced which features

## The Bi-Directional Data Flow

- **Neo4j GDS side:** FastRP, PageRank, Louvain algorithms write results as node properties
- **Spark Connector:** reads node properties into Delta Lake Gold tables; writes AutoML predictions back to Neo4j
- **Databricks side:** Gold tables feed Feature Engineering in Unity Catalog, which feeds AutoML
- **Full loop:** graph topology produces features, features train models, model predictions become graph properties

## What AutoML Does and Why We Use It

- **The problem:** we have a table of customers with feature columns (graph embeddings, PageRank scores, community IDs, tabular attributes). Some customers already have a risk category assigned. Most do not
- **What AutoML does:** it learns the pattern from labeled customers and predicts risk categories for the rest. You point it at the table and tell it which column to predict
- **Why AutoML:** it evaluates multiple model families (XGBoost, LightGBM, logistic regression, random forests, decision trees), tunes hyperparameters, and selects the best performer automatically
- **No ML expertise required:** AutoML handles model selection, training, and evaluation. You provide the data and the target column

## AutoML: Training and Prediction

- **Training call:** automl.classify takes the feature table and target_col="risk_category". AutoML trains on labeled rows only — rows with null targets are dropped
- **Prediction is a separate step:** load the best model, filter to unlabeled rows, and call fe.score_batch() to fill in missing risk categories
- **Predictions write back to Neo4j** via the Spark Connector, closing the loop

## The Two-System Payoff

- **The classifier fills structural gaps:** missing risk categories predicted from graph topology
- **The LLM fills semantic gaps:** interests and goals extracted from documents
- **Each makes the other's job easier** in the next cycle: richer graph features produce better classifiers, better predictions produce richer agent context

## Key Databricks APIs for the Loop

- **Register features:** FeatureEngineeringClient — register graph-derived features in Unity Catalog
- **Train classifier:** databricks.automl.classify() — evaluate model families on combined feature table
- **Score predictions:** score_batch() — predict labels for unlabeled entities
- **Write back:** Neo4j Spark Connector — push predictions to Neo4j as node properties

## Lakeflow Jobs Pipeline

- **Lakeflow Jobs** chains the full loop as tasks:
  1. **Extract** changed graph data to Delta tables
  2. **Run enrichment agents** on changed documents
  3. **Write approved enrichments** to Neo4j
  4. **Run GDS algorithms** on the enriched graph
  5. **Extract scores** to Gold tables
  6. **Register updated features** in Feature Engineering in Unity Catalog
- **Human-in-the-loop** checkpoints can gate any step

# Quantifying Lift

## Baseline: Tabular Features Only

- **Train a baseline model:** point AutoML at a feature table with only Delta Lake features: demographics, balances, transaction history
- **Record AUC, precision, recall:** this is the benchmark to beat
- **What the baseline sees:** each customer described in isolation by their own attributes
- **What the baseline misses:** which customers cluster together, who bridges separate groups, who occupies similar network positions

## Graph-Augmented: Measuring the Lift

- **Add graph features:** FastRP embeddings, PageRank scores, community ID, Jaccard similarity to the same feature table. Run AutoML again
- **What graph features capture:** community membership and centrality scores encode structural patterns invisible to flat tables
- **Published benchmark:** as one reference point, Neo4j's fraud detection benchmark showed significant improvement in detection rates when graph features were added. Lift varies by domain, and the demo measures it directly on the portfolio dataset
- **MLflow side-by-side:** both runs are MLflow experiments. Feature importance plots show which graph features drove the lift

## MLflow Experiment Tracking: Comparing Runs

- **Every AutoML trial is an MLflow run:** parameters, metrics (AUC, precision, recall, F1), and artifacts are logged automatically — no manual instrumentation
- **Two experiments, one comparison:** the baseline experiment (tabular only) and the graph-augmented experiment appear side by side in the MLflow Experiments UI
- **Metric comparison across runs:** the Experiments page lets you sort by AUC or any metric and compare the best run from each experiment directly
- **Trial notebook generation:** AutoML generates a source code notebook for the best trial, so the team can review, reproduce, and modify the winning model

## Feature Importance with SHAP Values

- **SHAP (Shapley values):** AutoML trial notebooks include SHAP code that scores each feature's contribution to predictions. Game-theory-based — measures how much each feature shifts the model's output
- **What SHAP reveals for graph features:** do FastRP embedding dimensions, PageRank scores, or Louvain community IDs actually move the needle, or does the model ignore them?
- **The proof:** if graph features appear in the top SHAP contributors alongside income and portfolio value, graph enrichment is earning its place. If they don't, you know to revisit the projection or algorithm choice
- **Actionable feedback loop:** SHAP results tell you which GDS algorithms to keep, tune, or replace in the next enrichment cycle

## Compounding Returns Across Cycles

- **Each enrichment cycle** produces more relationships for algorithms to operate on
- **AutoML retraining after Cycle 2** uses richer features than Cycle 1. MLflow experiment tracking compares model performance across cycles
- **The lift is not static:** embeddings after Cycle 2 encode richer topology than Cycle 1, reflecting relationships that did not exist before enrichment

# Sync Strategies and Orchestration

## Incremental Sync with Change Data Feed

- **Change Data Feed:** enable on Gold tables with delta.enableChangeDataFeed = true. Only changes after enablement are captured
- **Structured Streaming:** a Spark Structured Streaming job detects new customers and positions, pushes deltas to Neo4j via the Spark Connector
- **Incremental enrichment triggers:** customer profile updates re-analyze that customer only. New market research triggers batch analysis of that document type
- **Cost proportional to change volume,** not total data volume

# Scaling and Closing

## SEC EDGAR: Proving the Pattern at Scale

- **The dataset:** 3,906 asset managers, 28,960 companies, 590,538 equity holdings from 2021 quarterly SEC filings
- **Structurally identical graph model:** Manager to Holding to Company mirrors Customer to Position to Stock
- **What it proves:** the same FastRP + classifier pattern scales to a significantly larger graph
- **Companion notebook:** GDS computes features on 590K holdings, AutoML trains a classifier to predict whether a manager will increase or decrease a holding, predictions flow back

## Compounding Cycles

- **Cycle 1, obvious gaps:** early cycles capture straightforward missing relationships. INTERESTED_IN makes intent a first-class graph entity alongside transactional data
- **Cycle 2, algorithmic discovery:** Jaccard similarity identifies clusters. Louvain reveals organic segments no one designed upfront. These algorithms operate on relationships that did not exist before Cycle 1
- **Cycle 3+, cross-referencing new data:** new documents cross-reference against interest communities that only became visible through earlier enrichments
- **The distinction:** entity extraction asks "what does this document say?" Agentic enrichment asks "what relationships are missing?" That question, repeated across cycles, compounds

## Key Takeaways

- **Graph features capture what flat tables miss:** network position, community membership, centrality, structural similarity
- **Feature Engineering in Unity Catalog + AutoML** trains classifiers on the combined picture: graph-derived and tabular features together
- **The loop is bi-directional:** GDS scores flow to Gold tables, model predictions flow back to Neo4j via the Spark Connector
- **Lift is measurable and compounding:** each enrichment cycle produces richer features, and MLflow tracks the improvement
- **Lakeflow Jobs orchestrates the full pipeline** end-to-end with incremental sync via Change Data Feed
