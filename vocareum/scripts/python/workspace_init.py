#!/usr/bin/env python3
"""
Vocareum workspace_init.py — runs once when a workspace is first provisioned.

Sets up:
1. Metastore, default catalog, shared warehouse (via dbacademy)
2. CSV data upload to UC volumes
3. Delta lakehouse tables for Genie
4. Permissions for all users
"""
import os
import sys
import zipfile

# dbacademy.py lives in the same directory
sys.path.insert(0, os.path.dirname(__file__))

from dbacademy import voc_init

print("=" * 60)
print("WORKSPACE INIT: Neo4j + Databricks Workshop")
print("=" * 60)

# Phase 1: Standard dbacademy workspace initialization
# Creates metastore, catalog, warehouse, imports notebooks, etc.
db = voc_init()
db.workspace_init()

print("=" * 60)
print("PHASE 2: Workshop-specific data setup")
print("=" * 60)

# Find CSV data — check multiple possible locations
# Vocareum may auto-extract zips on upload
# .dat extension prevents Vocareum from auto-extracting on upload
data_zips = [
    "/voc/private/courseware/aircraft_digital_twin_data.dat",
    "/voc/private/courseware/aircraft_digital_twin_data.zip",
]
candidate_dirs = [
    "/voc/private/courseware/aircraft_digital_twin_data",  # subdirectory from zip
    "/voc/private/courseware",                              # flat alongside other files
]
data_dir = None

for d in candidate_dirs:
    if os.path.exists(d):
        csvs = [f for f in os.listdir(d) if f.endswith(".csv")]
        if csvs:
            data_dir = d
            print(f"Found {len(csvs)} CSV files at {data_dir}")
            break

if data_dir is None:
    for data_zip in data_zips:
        if os.path.exists(data_zip):
            print(f"Extracting {data_zip}...")
            with zipfile.ZipFile(data_zip, "r") as z:
                z.extractall("/voc/private/courseware/")
            data_dir = "/voc/private/courseware/aircraft_digital_twin_data"
            print(f"Extracted to {data_dir}")
            break

if data_dir is None:
    print("WARNING: No CSV files found — skipping data setup")
    print("Searched:", candidate_dirs, data_zips)
    sys.exit(0)

# Run workshop data setup (uploads CSVs, creates tables, grants permissions)
from workshop_data_setup import setup_workshop_data

setup_workshop_data(
    workspace_client=db.w,
    warehouse_id=db._warehouse,
    data_dir=data_dir,
)

print("=" * 60)
print("WORKSPACE INIT COMPLETE")
print("=" * 60)
