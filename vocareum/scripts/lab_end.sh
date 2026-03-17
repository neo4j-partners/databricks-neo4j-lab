#!/bin/bash
echo "IN LAB END AT $(date)"
pip3 install "databricks-sdk==0.38.0"
python3 /voc/scripts/python/lab_end.py
echo "OUT LAB END AT $(date)"
