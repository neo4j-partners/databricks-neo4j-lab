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

# Debug: print all VOC_ env vars to discover available identity info
print("VOC environment variables:")
for k, v in sorted(os.environ.items()):
    if k.startswith("VOC") or k.startswith("DATABRICKS") or k.startswith("DB_"):
        print(f"  {k}={v}")

# Debug: list workspace users to find IDP-provisioned identity
db_tmp = voc_init()
try:
    ws_users = list(db_tmp.w.users.list())
    print(f"Workspace users ({len(ws_users)}):")
    for u in ws_users:
        print(f"  {u.user_name} (id={u.id}, active={u.active})")
except Exception as e:
    print(f"Could not list workspace users: {e}")

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
