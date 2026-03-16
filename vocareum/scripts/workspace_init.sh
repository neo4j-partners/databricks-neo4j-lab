#!/bin/bash
echo "IN WORKSPACE INIT AT $(date)"
pip3 install "databricks-sdk==0.38.0"
python3 /voc/scripts/python/workspace_init.py
echo "OUT WORKSPACE INIT AT $(date)"
