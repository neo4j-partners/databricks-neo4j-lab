# Lab 1: Neo4j Aura Setup

In this lab, you will set up your Neo4j Aura database and save your connection credentials for use in later labs.

> **Background Reading:** For the concepts and architecture behind this lab, see [CONTENT.md](CONTENT.md).

## Prerequisites

- For **Workshop SSO Login**: Access to OneBlink credentials page (provided by your organizer)
- For **Free Trial Signup**: A valid email address

## Part 1: Neo4j Aura Signup

There are two signup options for this lab. **Please follow the signup process provided by your workshop organizer.**

### Option A: Workshop SSO Login (Recommended for organized workshops)

If your organizer has provided OneBlink credentials, use the SSO login process:

- Follow the [Neo4j Aura SSO Login](SSO_Neo4j_Aura_Signup.md) guide to log in using your organization's SSO credentials
- This option uses pre-configured workshop accounts

### Option B: Free Trial Signup (For self-paced learning)

If you're completing this lab independently or your organizer has instructed you to create a free trial:

- Follow the [Neo4j Aura Free Trial Signup](Aura_Free_Trial.md) guide to create your own account
- This option provides a 14-day free trial with an automatically created instance

---

### Create Your Database Instance

> **Note:** If you signed up using the **Free Trial** option (Option B), your instance was already created during the signup process. You can skip ahead to [saving your credentials](#save-your-credentials).

1. After logging in, click on **Instances** in the left sidebar under "Data services", then click the **Create instance** button.

   ![Neo4j Aura Console showing Instances menu and Create instance button](images/07_create_instance.png)

   If you already have existing instances, click the **Create instance** button in the top-right corner of the Instances page.

   ![Instances page with Create instance button for existing instances](images/07_alternative_create_instance.png)

2. Configure your new instance with the following settings:
   - Select the **Aura Professional** plan
   - Set the **Instance name** to a unique name based on your name (e.g., `ryans-lab-instance`). If you have an error try another unique name by adding your initials or a number.
   - Set the **Sizing** to **4 GB RAM / 1 CPU**
   - Enable **Vector-optimized configuration** under Additional settings

   ![Create instance configuration page showing Professional tier, naming, sizing, and vector optimization options](images/08_Create_Instance_Details.png)

3. Click **Create** to provision your database instance.

### Save Your Credentials

4. **Save your connection credentials immediately.** When your instance is created, a dialog will appear showing your database credentials (Username and Password). Click **Download and continue** to save the credentials file.

   ![Credentials dialog showing username and password with download option](images/09_Download_Credentails.png)

> **CRITICAL:** The password is only shown once and will not be available after you close this dialog. Download the credentials file and store it somewhere safe. You will need these credentials in later labs to connect your applications to Neo4j.

You will enter these credentials in the Configuration cell of each Databricks notebook:

```python
NEO4J_URI = "neo4j+s://xxxxxxxx.databases.neo4j.io"
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "<your-password>"
```

## Part 2: Introduction to Cypher

Cypher is Neo4j's query language. Before you load data in Lab 2, practice the basics by creating and querying a small graph.

### Open the Query Interface

1. Go to [console.neo4j.io](https://console.neo4j.io)
2. Select your instance
3. Click **Query** to open the query editor

This is where you will run the Cypher examples below.

### Creating Nodes

Create an Aircraft node with properties:

```cypher
CREATE (a:Aircraft {tail_number: 'N12345', model: 'B737-800', manufacturer: 'Boeing'})
RETURN a
```

`CREATE` makes a node. `:Aircraft` is a **label** (like a type). Properties go inside curly braces.

### Reading Nodes

Find all Aircraft nodes and return their properties:

```cypher
MATCH (a:Aircraft)
RETURN a.tail_number, a.model, a.manufacturer
```

`MATCH` finds patterns in the graph. `RETURN` selects what to display.

### Creating Relationships

Create two nodes connected by a relationship:

```cypher
CREATE (a:Aircraft {tail_number: 'N12345', model: 'B737-800'})
CREATE (s:System {name: 'Engine #1', type: 'CFM56-7B'})
CREATE (a)-[:HAS_SYSTEM]->(s)
RETURN a, s
```

`-[:HAS_SYSTEM]->` creates a directed relationship from the Aircraft to the System.

### Querying Relationships

Traverse relationships to find connected nodes:

```cypher
MATCH (a:Aircraft)-[:HAS_SYSTEM]->(s:System)
RETURN a.tail_number, s.name, s.type
```

### Filtering with WHERE

Add conditions to narrow results:

```cypher
MATCH (a:Aircraft)
WHERE a.manufacturer = 'Boeing'
RETURN a.tail_number, a.model
```

### Cleaning Up

Remove all nodes and relationships to start fresh:

```cypher
MATCH (n) DETACH DELETE n
```

`DETACH DELETE` removes nodes and all their relationships.

> **Note:** Run this cleanup before starting Lab 2 so you begin with an empty graph.

> **Tip:** These examples are for learning. In Lab 2 you will load the full Aircraft Digital Twin dataset programmatically using the Spark Connector.

## Next Steps

After completing this lab, continue to [Lab 2 - Databricks ETL to Neo4j](../Lab_2_Databricks_ETL_Neo4j) to load the Aircraft Digital Twin dataset into your Neo4j Aura instance.
