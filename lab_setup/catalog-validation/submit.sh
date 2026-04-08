#!/usr/bin/env bash
# Submit a Python script as a one-time Databricks job run.
#
# Usage:
#   ./submit.sh                             # runs test_hello.py (default)
#   ./submit.sh test_catalog.py             # runs catalog validation
#   ./submit.sh test_catalog.py --no-wait   # submit without waiting
#
# Scripts live in agent_modules/ on the remote workspace.
# Catalog settings from .env are automatically injected as script parameters.
# Scripts that don't use argparse (like test_hello.py) safely ignore them.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Load .env
set -a
source "$SCRIPT_DIR/.env"
set +a

PROFILE="$DATABRICKS_PROFILE"
REMOTE_DIR="$WORKSPACE_DIR"
CLUSTER_ID="$DATABRICKS_CLUSTER_ID"

SCRIPT_NAME="${1:-test_hello.py}"
NO_WAIT=""
if [[ "${2:-}" == "--no-wait" ]]; then
    NO_WAIT="--no-wait"
fi

REMOTE_PATH="$REMOTE_DIR/agent_modules/$SCRIPT_NAME"
RUN_NAME="catalog_validation: $SCRIPT_NAME"

# shellcheck source=cluster_utils.sh
source "$SCRIPT_DIR/cluster_utils.sh"

echo "Submitting job (profile: $PROFILE)"
echo "  Script:   $REMOTE_PATH"
ensure_cluster_running "$PROFILE" "$CLUSTER_ID"
echo "  Run name: $RUN_NAME"

# Build parameters: inject catalog settings from .env.
# Uses Python to safely handle special characters.
PARAMS="[]"
if [[ -n "${CATALOG_NAME:-}" ]]; then
    PARAMS=$(python3 -c "
import json, os
params = []
cat = os.environ.get('CATALOG_NAME', '')
sch = os.environ.get('SCHEMA_NAME', '')
vol = os.environ.get('VOLUME_NAME', '')
storage = os.environ.get('STORAGE_ROOT', '')
if cat:
    params += ['--catalog', cat]
if sch:
    params += ['--schema', sch]
if vol:
    params += ['--volume', vol]
if storage:
    params += ['--storage-root', storage]
print(json.dumps(params))
")
    echo "  Catalog:  settings injected from .env"
fi

echo "---"

# Build the job JSON.
# Uses an existing all-purpose cluster (started automatically if terminated).
JOB_JSON=$(cat <<EOF
{
  "run_name": "$RUN_NAME",
  "tasks": [
    {
      "task_key": "run_script",
      "spark_python_task": {
        "python_file": "$REMOTE_PATH",
        "parameters": $PARAMS
      },
      "existing_cluster_id": "$CLUSTER_ID"
    }
  ]
}
EOF
)

databricks jobs submit \
    --profile "$PROFILE" \
    --json "$JOB_JSON" \
    $NO_WAIT

echo ""
echo "Job submission complete."
