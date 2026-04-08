# Catalog Validation

Validates Unity Catalog operations on a Databricks cluster: create a catalog, schema, and volume, write a CSV, and read it back. Use this to confirm that your cluster and user permissions are set up correctly for UC operations before running workshop labs.

## Prerequisites

- Databricks CLI configured with a profile (`databricks configure --profile <name>`)
- An all-purpose cluster (does not need to be running — scripts auto-start it if terminated)

## Setup

```bash
cd lab_setup/catalog-validation
cp .env.example .env
```

Edit `.env` with your values:

| Variable | Required | Description |
|----------|:--------:|-------------|
| `DATABRICKS_PROFILE` | Yes | CLI profile name |
| `DATABRICKS_CLUSTER_ID` | Yes | All-purpose cluster ID |
| `WORKSPACE_DIR` | Yes | Remote path for uploaded scripts (e.g., `/Workspace/Users/you@example.com/catalog_validation`) |
| `CATALOG_NAME` | Yes | Catalog to create (default: `test_catalog_validation`) |
| `SCHEMA_NAME` | Yes | Schema to create (default: `test_schema`) |
| `VOLUME_NAME` | Yes | Volume to create (default: `test_volume`) |
| `STORAGE_ROOT` | Maybe | Storage root URL — required on Default Storage metastores (see below) |

### Finding the Storage Root

Azure Databricks workspaces using **Default Storage** metastores require a `STORAGE_ROOT` for catalog creation. Without it, `CREATE CATALOG` fails with:

```
Metastore storage root URL does not exist. Default Storage is enabled in your account.
You can use the UI to create a new catalog using Default Storage, or please provide a
storage location for the catalog (for example 'CREATE CATALOG myCatalog MANAGED LOCATION '<location-path>').
```

To find the storage root, inspect any existing catalog in your workspace:

```bash
databricks catalogs get <existing-catalog> --profile <profile> -o json
```

Look for the `storage_root` field. It will be an `abfss://` URL like:

```
abfss://unity-catalog-storage@<storage-account>.dfs.core.windows.net/<workspace-id>
```

Copy this value into `STORAGE_ROOT` in your `.env`. The script uses it to add `MANAGED LOCATION` to the `CREATE CATALOG` statement.

> If your metastore has a configured storage root (common on AWS), you can leave `STORAGE_ROOT` empty — `CREATE CATALOG` will work without it.

## Validation Flow

### Step 1: Upload scripts

```bash
./upload.sh --all
```

Verify the upload:

```bash
./validate.sh
```

### Step 2: Smoke test the cluster

Confirms Python and Spark are available:

```bash
./submit.sh test_hello.py
```

### Step 3: Run catalog validation

Creates the catalog/schema/volume, writes a 3-row test CSV to the volume, reads it back, and verifies the data round-trips correctly:

```bash
./submit.sh test_catalog.py
```

The script reports PASS/FAIL for each step:

```
  [PASS] Spark initialized — version 4.0.0
  [PASS] Create catalog — test_catalog_validation
  [PASS] Create schema — test_catalog_validation.test_schema
  [PASS] Create volume — test_catalog_validation.test_schema.test_volume
  [PASS] Write CSV — 3 rows -> /Volumes/test_catalog_validation/test_schema/test_volume/test_validation.csv
  [PASS] Read CSV — 3 rows from /Volumes/test_catalog_validation/test_schema/test_volume/test_validation.csv
  [PASS] Data round-trip — row count and values match
```

If the catalog already exists, the script detects it and continues (reports `already exists, using it`).

### Step 4: Cleanup

The test catalog persists after validation so you can inspect it. To clean it up, delete it via the CLI:

```bash
databricks catalogs delete test_catalog_validation --profile <profile> --force
```

To clean up the remote workspace and job runs:

```bash
./clean.sh
```

For a full reset and re-run:

```bash
./clean.sh --yes
./upload.sh --all
./submit.sh test_hello.py
./submit.sh test_catalog.py
```

## Scripts Reference

| Script | Purpose | Destructive |
|--------|---------|:-----------:|
| `test_hello.py` | Cluster smoke test (Python, Spark) | No |
| `test_catalog.py` | Create catalog/schema/volume, write and read CSV (7 checks) | **Yes** — creates UC objects |

## Shell Scripts

| Script | Purpose |
|--------|---------|
| `upload.sh` | Upload scripts to Databricks workspace |
| `submit.sh` | Check cluster, then submit a script as a one-time job run |
| `validate.sh` | Check cluster, then list remote workspace contents and verify uploads |
| `clean.sh` | Delete remote workspace and `catalog_validation:*` job runs |
| `cluster_utils.sh` | Shared helper — checks cluster state and auto-starts if terminated (symlink to `notebook_validation/`) |

### upload.sh

```bash
./upload.sh                     # uploads test_hello.py (default)
./upload.sh test_catalog.py     # uploads a specific file
./upload.sh --all               # uploads all agent_modules/*.py files
```

### submit.sh

```bash
./submit.sh                     # runs test_hello.py (default)
./submit.sh test_catalog.py     # runs catalog validation
./submit.sh test_catalog.py --no-wait   # submit without waiting for completion
```

Catalog settings and `STORAGE_ROOT` from `.env` are automatically injected as command-line arguments (`--catalog`, `--schema`, `--volume`, `--storage-root`). The cluster is auto-started if terminated (polls up to 10 minutes).

### validate.sh

```bash
./validate.sh                   # list all remote files
./validate.sh test_catalog.py   # check if a specific file exists
```

### clean.sh

Deletes the remote workspace directory and all `catalog_validation:*` one-time job runs. Prompts for confirmation before proceeding.

```bash
./clean.sh              # clean workspace + job runs (with confirmation)
./clean.sh --workspace  # clean only remote workspace
./clean.sh --runs       # clean only job runs
./clean.sh --yes        # skip confirmation prompt
```

## Troubleshooting

### `Metastore storage root URL does not exist`

Set `STORAGE_ROOT` in `.env`. See [Finding the Storage Root](#finding-the-storage-root) above.

### `INSUFFICIENT_PERMISSIONS` on CREATE CATALOG

Your user lacks the `CREATE CATALOG` privilege. Ask a workspace admin to grant it:

```sql
GRANT CREATE CATALOG ON METASTORE TO `your-email@example.com`;
```

### Job reports FAILED but logs show all PASS

Earlier versions called `sys.exit(0)` which Databricks treats as a `SystemExit` error. Update to the latest `test_catalog.py` which exits naturally on success.

### Inspecting job output

When a job fails, retrieve the logs in three steps:

```bash
# Find the run
databricks jobs list-runs --profile <profile> --limit 3

# Get the task-level run ID
databricks jobs get-run <RUN_ID> --profile <profile> -o json

# Get stdout/stderr
databricks jobs get-run-output <TASK_RUN_ID> --profile <profile> -o json
```

The parent run ID and task run ID are different. `get-run` returns the parent; each task has its own `run_id` in the `tasks` array. `get-run-output` requires the task-level ID.
