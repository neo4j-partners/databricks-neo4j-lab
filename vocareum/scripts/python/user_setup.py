#!/usr/bin/env python3
"""
Vocareum user_setup.py — runs when a user first enters the lab.

Sets up per-user resources:
- Personal cluster with Neo4j Spark Connector
- Personal schema for scratch work
- Working volume
- Notebooks imported to user's home folder
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from dbacademy import voc_init

user = os.getenv("VOC_USER_EMAIL", "unknown@example.com")

print("=" * 60)
print(f"USER SETUP: {user}")
print("=" * 60)

db = voc_init()
redirect_url = db.user_setup(user)

if redirect_url:
    print(f"Redirect URL: {redirect_url}")

    # Write redirect URL for Vocareum to pick up
    redirect_file = os.getenv("VOC_REDIRECT_FILE")
    if redirect_file:
        with open(redirect_file, "w") as f:
            f.write(redirect_url)

print("=" * 60)
print(f"USER SETUP COMPLETE: {user}")
print("=" * 60)
