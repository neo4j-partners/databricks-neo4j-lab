#!/bin/bash
echo "IN LAB SETUP AT $(date)"
pip3 install "databricks-sdk==0.38.0"
python3 /voc/scripts/python/lab_setup.py
echo "OUT LAB SETUP AT $(date)"
