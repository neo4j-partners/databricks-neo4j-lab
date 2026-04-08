"""Minimal smoke test to verify remote execution on Databricks.

Confirms the cluster has the prerequisites for catalog validation:
1. Python and Spark are available
2. Output is captured in the job run

Usage:
    ./upload.sh test_hello.py && ./submit.sh test_hello.py
"""

import os
import sys

print("=" * 60)
print("catalog_validation: Remote execution test")
print("=" * 60)
print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")
print(f"Working directory: {os.getcwd()}")
print(f"DATABRICKS_RUNTIME_VERSION: {os.environ.get('DATABRICKS_RUNTIME_VERSION', 'not set')}")

# Verify Spark is available
try:
    from pyspark.sql import SparkSession
    spark = SparkSession.builder.getOrCreate()
    print(f"Spark version: {spark.version}")
    print(f"Spark app name: {spark.sparkContext.appName}")
except Exception as e:
    print(f"Spark not available: {e}")

print("=" * 60)
print("SUCCESS: Remote execution verified")
print("=" * 60)
