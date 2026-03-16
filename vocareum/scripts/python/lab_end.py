#!/usr/bin/env python3
"""
Vocareum lab_end.py — runs when user clicks End Lab or session expires.

Reaps all user resources:
- Terminates/deletes clusters
- Stops warehouses
- Drops user catalog/schema
- Cleans up metadata
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from dbacademy import voc_init

user = os.getenv("VOC_USER_EMAIL", "unknown@example.com")
action = os.getenv("VOC_LAB_END_ACTION", "terminate")

print("=" * 60)
print(f"LAB END ({action}): {user}")
print("=" * 60)

db = voc_init()

if action == "stop":
    # Just stop resources (user might come back)
    db.lab_end_stop(user)
elif action == "terminate":
    # Full cleanup — user is done
    db.lab_end_terminate(user)
else:
    print(f"Unknown action: {action}, defaulting to terminate")
    db.lab_end_terminate(user)

print("=" * 60)
print(f"LAB END COMPLETE: {user}")
print("=" * 60)
