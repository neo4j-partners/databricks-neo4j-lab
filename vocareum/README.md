# Vocareum Lab Platform Setup

This directory contains everything needed to run the Neo4j + Databricks workshop on the [Vocareum](https://labs.vocareum.com) lab platform.

## Structure

```
vocareum/
  courseware/
    neo4j-databricks-workshop.cfg   # Course config (cluster, catalog, entry notebook)
    aircraft_digital_twin_data.zip  # CSV data for DLT pipeline (22 files)
    dlt_fleet_etl.py                # DLT pipeline notebook (bronze/silver/gold)
  scripts/
    workspace_init.sh               # Shell wrappers that Vocareum calls
    user_setup.sh
    lab_setup.sh
    lab_end.sh
    python/
      workspace_init.py             # Provisions metastore, runs DLT pipeline
      user_setup.py                 # Per-student cluster + notebook import
      lab_setup.py                  # Resumes cluster/warehouse on lab start
      lab_end.py                    # Tears down student resources
      workshop_data_setup.py        # Uploads CSVs, creates Delta tables, grants access
  docs/
    README.md                       # Student-facing instructions (shown in Vocareum iframe)
  upload.sh                         # Bulk upload script (builds notebook archive from repo root)
  SETUP_GUIDE.md                    # Full admin setup instructions
```

## Notebooks

Lab notebooks are **not** duplicated here. The `upload.sh` script builds the Vocareum notebook archive directly from the repo root:

- `Lab_2_Databricks_ETL_Neo4j/*.ipynb`
- `Lab_3_Semantic_Search/*.ipynb` + `data_utils.py`

This ensures the Vocareum courseware always matches the latest notebooks without maintaining copies.

## Quick Start

```bash
# Set Vocareum API credentials
export VOC_TOKEN="your-personal-access-token"
export VOC_COURSE_ID="206455"
export VOC_ASSIGNMENT_ID="..."
export VOC_PART_ID="..."

# Build and upload everything
./upload.sh
```

See [SETUP_GUIDE.md](SETUP_GUIDE.md) for full setup instructions including Vocareum course configuration, MCP connection setup, and Genie Space creation.
