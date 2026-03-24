#!/bin/bash
#
# upload.sh — Bulk upload Vocareum lab files via REST API v2
#
# Usage:
#   export VOC_TOKEN="your-personal-access-token"
#   export VOC_COURSE_ID="12345"
#   export VOC_ASSIGNMENT_ID="67890"
#   export VOC_PART_ID="11111"
#   ./upload.sh
#
# Get your token from: Vocareum → Settings → Personal Access Tokens
# Get IDs from the Vocareum URL when viewing your lab assignment.
#
# Valid targets: course, data, docs, scripts, startercode, private
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
API_BASE="https://api.vocareum.com/api/v2"

# --- Validate env vars ---
for var in VOC_TOKEN VOC_COURSE_ID VOC_ASSIGNMENT_ID VOC_PART_ID; do
    if [[ -z "${!var:-}" ]]; then
        echo "ERROR: $var is not set" >&2
        exit 1
    fi
done

ENDPOINT="${API_BASE}/courses/${VOC_COURSE_ID}/assignments/${VOC_ASSIGNMENT_ID}/parts/${VOC_PART_ID}"

TMPDIR=$(mktemp -d)
trap 'rm -rf "$TMPDIR"' EXIT

# --- Helper: zip a directory and upload to a target ---
upload_target() {
    local target="$1"
    local src_dir="$2"

    if [[ ! -d "$src_dir" ]]; then
        echo "  SKIP $target (no files)"
        return
    fi

    local zip_path="$TMPDIR/${target}.zip"
    (cd "$src_dir" && zip -r "$zip_path" . -x '*.DS_Store' > /dev/null)

    local zip_b64
    zip_b64=$(base64 < "$zip_path")
    local payload_path="$TMPDIR/${target}_payload.json"

    python3 -c "
import json, sys
b64 = sys.stdin.read()
with open('$payload_path', 'w') as f:
    json.dump({
        'update': 1,
        'content': [
            {'target': '$target', 'zipcontent': b64}
        ]
    }, f)
" <<< "$zip_b64"

    local http_code
    http_code=$(curl -s -o "$TMPDIR/${target}_response.json" -w "%{http_code}" \
        -X PUT "$ENDPOINT" \
        -H "Authorization: Token $VOC_TOKEN" \
        -H "Content-Type: application/json" \
        -d @"$payload_path")

    local size
    size=$(du -h "$zip_path" | cut -f1)

    if [[ "$http_code" == "200" || "$http_code" == "202" ]]; then
        echo "  OK   $target ($size)"
    else
        echo "  FAIL $target → HTTP $http_code"
        cat "$TMPDIR/${target}_response.json" 2>/dev/null
        echo ""
        return 1
    fi
}

# --- Build notebook archive from repo root ---
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
echo "Building notebook archive from repo root: $REPO_ROOT"

NOTEBOOK_ZIP="$TMPDIR/neo4j-databricks-workshop.zip"
(cd "$REPO_ROOT" && zip -r "$NOTEBOOK_ZIP" \
    Lab_2_Databricks_ETL_Neo4j/*.ipynb \
    Lab_3_Semantic_Search/*.ipynb \
    Lab_3_Semantic_Search/data_utils.py \
    -x '*.DS_Store' > /dev/null)
echo "  Built notebook archive: $(du -h "$NOTEBOOK_ZIP" | cut -f1)"

# --- Stage files into per-target directories ---
echo "Building upload packages..."

# Target: private → /voc/private/
PRIVATE_DIR="$TMPDIR/stage_private"
mkdir -p "$PRIVATE_DIR/courseware"

cp "$SCRIPT_DIR/courseware/neo4j-databricks-workshop.cfg" "$PRIVATE_DIR/courseware/"
cp "$NOTEBOOK_ZIP"                                         "$PRIVATE_DIR/courseware/neo4j-databricks-workshop.zip"
cp "$SCRIPT_DIR/courseware/dlt_fleet_etl.py"              "$PRIVATE_DIR/courseware/"

if [[ -f "$SCRIPT_DIR/courseware/aircraft_digital_twin_data.zip" ]]; then
    cp "$SCRIPT_DIR/courseware/aircraft_digital_twin_data.zip" "$PRIVATE_DIR/courseware/aircraft_digital_twin_data.dat"
elif [[ -f "$SCRIPT_DIR/courseware/aircraft_digital_twin_data.dat" ]]; then
    cp "$SCRIPT_DIR/courseware/aircraft_digital_twin_data.dat" "$PRIVATE_DIR/courseware/aircraft_digital_twin_data.dat"
fi

# Target: scripts → /voc/scripts/
SCRIPTS_DIR="$TMPDIR/stage_scripts"
mkdir -p "$SCRIPTS_DIR/python"

cp "$SCRIPT_DIR/scripts/workspace_init.sh" "$SCRIPTS_DIR/"
cp "$SCRIPT_DIR/scripts/user_setup.sh"     "$SCRIPTS_DIR/"
cp "$SCRIPT_DIR/scripts/lab_setup.sh"      "$SCRIPTS_DIR/"
cp "$SCRIPT_DIR/scripts/lab_end.sh"        "$SCRIPTS_DIR/"
cp "$SCRIPT_DIR/scripts/python/workspace_init.py"      "$SCRIPTS_DIR/python/"
cp "$SCRIPT_DIR/scripts/python/user_setup.py"          "$SCRIPTS_DIR/python/"
cp "$SCRIPT_DIR/scripts/python/lab_setup.py"           "$SCRIPTS_DIR/python/"
cp "$SCRIPT_DIR/scripts/python/lab_end.py"             "$SCRIPTS_DIR/python/"
cp "$SCRIPT_DIR/scripts/python/workshop_data_setup.py" "$SCRIPTS_DIR/python/"

# Target: docs → /voc/docs/
DOCS_DIR="$TMPDIR/stage_docs"
mkdir -p "$DOCS_DIR"
cp "$SCRIPT_DIR/docs/README.md" "$DOCS_DIR/"

# --- Upload each target (update=1 overwrites existing) ---
echo ""
echo "Uploading to Vocareum (update=1, overwrites existing)..."
echo "  Course:     $VOC_COURSE_ID"
echo "  Assignment: $VOC_ASSIGNMENT_ID"
echo "  Part:       $VOC_PART_ID"
echo ""

FAILED=0
upload_target "private" "$PRIVATE_DIR" || FAILED=1

# 15s delay between uploads (Vocareum API rate limit)
echo "  (waiting 15s for API rate limit...)"
sleep 15

upload_target "scripts" "$SCRIPTS_DIR" || FAILED=1

echo "  (waiting 15s for API rate limit...)"
sleep 15

upload_target "docs" "$DOCS_DIR" || FAILED=1

echo ""
if [[ "$FAILED" -eq 0 ]]; then
    echo "All uploads successful!"
else
    echo "Some uploads failed. Check output above." >&2
    exit 1
fi
