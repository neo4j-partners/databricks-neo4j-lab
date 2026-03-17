#!/bin/bash
echo "IN USER SETUP AT $(date)"
pip3 install "databricks-sdk==0.38.0"
python3 /voc/scripts/python/user_setup.py
echo "OUT USER SETUP AT $(date)"
