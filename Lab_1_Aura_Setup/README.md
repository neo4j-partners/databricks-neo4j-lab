# Lab 1: Neo4j Aura Setup

In this lab, you will set up your Neo4j Aura database and save your connection credentials for use in later labs.

## Prerequisites

- Completed **Lab 0** (environment setup)
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

## Next Steps

After completing this lab, continue to [Lab 5 - Databricks ETL to Neo4j](../Lab_5_Databricks_ETL_Neo4j) to load the Aircraft Digital Twin dataset into your Neo4j Aura instance.
