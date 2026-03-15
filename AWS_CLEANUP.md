# AWS Infrastructure Removal

The workshop setup previously required operators to provision IAM roles, S3 buckets, cross-account trust policies, and instance profiles before the Databricks CLI could run. This AWS prerequisite layer added hours of setup time, exposed credentials to shell scripts, and created failure modes unrelated to the workshop content. The core `databricks-setup` CLI was already 95% Databricks-native: it uploads data through Unity Catalog volumes, creates Delta tables via SQL, and manages permissions through the Databricks SDK. The AWS code was vestigial.

This document catalogs every change made during cleanup.

---

## Status: COMPLETE

All items below have been implemented and verified.

---

## Files Deleted

These files existed solely to provision or manage AWS infrastructure. None were called by the `databricks-setup` CLI.

| File | Purpose | Status |
|------|---------|--------|
| `lab_setup/scripts/fix_workspace.sh` | Provisioned classic-compute workspace: cross-account IAM role, S3 root bucket, storage IAM role, credential/storage configs. 600+ lines. | DELETED |
| `lab_setup/scripts/setup_databricks_external_location.sh` | Created S3-backed external location in UC: IAM role, S3/KMS access policy, storage credential, external location. 625+ lines. | DELETED |
| `lab_setup/scripts/cleanup_databricks_external_location.sh` | Teardown companion for the above. | DELETED |
| `lab_setup/scripts/README.md` | Documented the three scripts above. | DELETED |
| `lab_setup/scripts/` (directory) | Empty after deletions. | DELETED |
| `lab_setup/docs/WORKSPACE_SETUP.md` | Manual AWS workspace setup guide with hardcoded AWS account IDs, IAM role ARNs, S3 bucket names. | DELETED |
| `lab_setup/neo4j_mcp_connection/setup_databricks_secrets.sh` | Read `.mcp-credentials.json` from aws-starter and stored OAuth2 secrets in Databricks. | DELETED |
| `lab_setup/neo4j_mcp_connection/.mcp-credentials.json` | AWS AgentCore OAuth2 credentials file. | DELETED |

---

## Files Modified

### `lab_setup/auto_scripts/src/databricks_setup/cluster.py`

| Change | Status |
|--------|--------|
| Removed `AwsAttributes`, `AwsAvailability`, `EbsVolumeType` imports | DONE |
| Removed `ensure_instance_profile_registered()` function (25 lines) | DONE |
| Removed `AwsAttributes` construction block in `create_cluster()` | DONE |
| Removed `aws_attributes=aws_attributes` parameter from `clusters.create()` call | DONE |
| Removed instance profile registration call in `get_or_create_cluster()` | DONE |

### `lab_setup/auto_scripts/src/databricks_setup/config.py`

| Change | Status |
|--------|--------|
| Removed `instance_profile_arn` field from `ClusterConfig` | DONE |
| Removed `cloud_provider` field from `ClusterConfig` | DONE |
| Removed `INSTANCE_PROFILE_ARN` and `CLOUD_PROVIDER` env var loading | DONE |
| Simplified `get_node_type()` to default to `m5.large` with `NODE_TYPE` env override | DONE |

### `lab_setup/.env.example`

| Change | Status |
|--------|--------|
| Removed AWS Configuration section (`AWS_CLI_PROFILE`, `AWS_REGION`, `AWS_ACCOUNT_ID`) | DONE |
| Removed S3 Bucket Configuration section | DONE |
| Removed IAM Role Configuration section | DONE |
| Removed storage credential/external location names | DONE |
| Removed `CLOUD_PROVIDER` and `INSTANCE_PROFILE_ARN` | DONE |
| Removed KMS, file events, read-only, UC master role settings | DONE |
| Reduced from 166 lines to ~90 lines | DONE |

### `lab_setup/.env`

| Change | Status |
|--------|--------|
| Removed all AWS-specific config (account IDs, ARNs, S3, IAM, instance profiles) | DONE |
| Kept Databricks profile, cluster, warehouse, UC, permissions, Neo4j credentials | DONE |

### `lab_setup/neo4j_mcp_connection/README.md`

| Change | Status |
|--------|--------|
| Rewrote to describe generic external MCP pattern (Option A) | DONE |
| Removed all AWS AgentCore, aws-starter, Cognito references | DONE |
| Replaced architecture diagram (removed AgentCore Gateway layer) | DONE |
| Added inline secret creation instructions (replaces deleted shell script) | DONE |
| Removed `setup_databricks_secrets.sh` from Files table | DONE |

### `lab_setup/neo4j_mcp_connection/neo4j_mcp_agent.py`

| Change | Status |
|--------|--------|
| Updated module docstring: removed "AWS AgentCore Gateway" and `setup_databricks_secrets.sh` references | DONE |
| Updated comments: "AgentCore Gateway" → "MCP gateway" | DONE |
| Updated comments: "AWS Cognito" → generic OAuth2 | DONE |

### `lab_setup/neo4j_mcp_connection/neo4j-mcp-http-connection.ipynb`

| Change | Status |
|--------|--------|
| Updated title: removed "(AWS AgentCore)" | DONE |
| Updated description: "deployed on AWS AgentCore Gateway" → "external Neo4j MCP server" | DONE |
| Updated prerequisites: removed aws-starter, AgentCore deployment requirements | DONE |
| Updated authentication note: removed AWS Cognito reference | DONE |
| Updated troubleshooting: removed AgentCore-specific fix instructions | DONE |
| Updated next steps: removed "via AWS AgentCore" | DONE |
| Updated error handling: replaced aws-starter instructions with generic secret setup | DONE |
| Updated comments: "AgentCore Gateway" → "MCP gateway" throughout | DONE |

### `lab_setup/neo4j_mcp_connection/neo4j-mcp-agent-deploy.ipynb`

| Change | Status |
|--------|--------|
| Updated description: "AWS AgentCore Gateway" → "external MCP server" | DONE |
| Updated architecture diagram: "AgentCore Gateway" → "External MCP Server" | DONE |
| Updated prerequisites: removed "Running on AWS AgentCore" → "Running on an external hosting platform" | DONE |
| Updated print statements: "AgentCore Gateway" → "MCP gateway" | DONE |
| Updated deployment tag: `neo4j-mcp-agentcore` → `neo4j-mcp` | DONE |

---

## Documentation Updates

| File | Change | Status |
|------|--------|--------|
| `CLAUDE.md` | Removed "deployed on AWS AppRunner" from Multi-Agent Architecture | DONE |
| `CLAUDE.md` | Removed `CLOUD_PROVIDER` from Configuration section | DONE |
| `lab_setup/README.md` | Removed `CLOUD_PROVIDER="aws"` from minimum config example | DONE |
| `lab_setup/auto_scripts/README.md` | Removed `CLOUD_PROVIDER`, `INSTANCE_PROFILE_ARN` from options table | DONE |
| `lab_setup/auto_scripts/README.md` | Removed cloud provider defaults table (AWS vs Azure) | DONE |
| `lab_setup/auto_scripts/README.md` | Simplified cluster defaults table to single node type | DONE |
| `lab_setup/auto_scripts/README.md` | Removed `CLOUD_PROVIDER` from minimum config example | DONE |

### Additional files (caught in review pass)

| File | Change | Status |
|------|--------|--------|
| `README.md` (root) | Removed "runs on AWS AppRunner" from Lab Architecture description | DONE |
| `slides/docs/overview-and-genai-foundations.md` | Removed "AWS AgentCore" from What You'll Build, infrastructure table, and lab notes | DONE |
| `slides/overview-knowledge-graph/01-workshop-over.md` | Removed "AWS" and "AWS Bedrock" from title/subtitle, "AWS AgentCore" from What You'll Build, infrastructure table, and lab notes | DONE |

---

## Verification Results

| Check | Result |
|-------|--------|
| Grep sweep for AWS infrastructure refs in `lab_setup/` | Zero hits |
| Grep sweep for AWS infrastructure refs in `CLAUDE.md` | Zero hits |
| Grep sweep for "AgentCore" in all `.md`, `.py`, `.ipynb` files | Zero hits (outside AWS_CLEANUP.md) |
| Grep sweep for "AWS AppRunner", "AWS Bedrock", "aws-starter" repo-wide | Zero hits (outside AWS_CLEANUP.md) |
| Python import test (`cluster.py`, `config.py`) | PASS |
| `ruff check` on modified files | PASS (0 errors) |
| `mypy` on modified files | PASS (0 issues) |
| Pre-existing lint errors in other files | Unchanged (4 pre-existing issues in `log.py`, `main.py`, `permissions.py`) |

### Remaining "AWS" references (legitimate, not infrastructure)

These references to "AWS" remain in the repo and are correct — they describe Neo4j Aura's cloud hosting options, not Databricks infrastructure:

- `Lab_1_Aura_Setup/Aura_Free_Trial.md` — "Cloud provider: AWS" (Neo4j Aura instance setup)
- `slides/overview-knowledge-graph/01-neo4j-aura-overview-slides.md` — "Deploy in AWS, GCP, or Azure" (Neo4j Aura availability)
- `Lab_1_Aura_Setup/slides/04-neo4j-aura.md` — "Cloud-native - Deploy in AWS, GCP, or Azure"

### Note: `lab_setup/.env` catalog name

`CATALOG_NAME="aws-databricks-neo4j-lab"` retains the "aws-" prefix. This is the name of an existing deployed catalog in the Databricks workspace. Changing it here would cause the setup CLI to target a non-existent catalog. If the catalog is recreated, the name should be updated to `databricks-neo4j-lab` to match `.env.example`.

---

## What Was Preserved

- **`lab_setup/docs/MANUAL_SETUP.md`** — Pure Databricks UI setup guide, no AWS references
- **Connection name `neo4j_agentcore_mcp`** — This is a Unity Catalog resource name used across notebooks, the agent, and permissions code. Renaming it would require coordinated changes across the deployed Databricks workspace. The name is vestigial but harmless.
- **Tool name prefixes `neo4j-mcp-server-target___`** — These are determined by the MCP gateway at the server side, not by the Databricks code. Changed comments from "prefixed by AgentCore Gateway" to "may be prefixed by the MCP gateway."
- **`lab_setup/neo4j_mcp_connection/neo4j-mcp-http-connection.ipynb` code cells** — The `spark.sql()` calls, `http_request()` usage, and helper functions are all Databricks-native. Only markdown cells and comments were updated.
