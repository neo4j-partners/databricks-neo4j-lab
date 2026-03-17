#!/usr/bin/env python3
"""
Vocareum lab_setup.py — runs each time a user starts/resumes their lab session.

Resumes resources:
- Starts user's cluster if stopped
- Starts user's warehouse if stopped
- Returns redirect URL to entry notebook
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from dbacademy import voc_init

user = os.getenv("VOC_USER_EMAIL", "unknown@example.com")

print("=" * 60)
print(f"LAB SETUP (resume): {user}")
print("=" * 60)

db = voc_init()
redirect_url = db.user_setup_resume(user)

if redirect_url:
    print(f"Redirect URL: {redirect_url}")

    redirect_file = os.getenv("VOC_REDIRECT_FILE")
    if redirect_file:
        with open(redirect_file, "w") as f:
            f.write(redirect_url)

print("=" * 60)
print(f"LAB SETUP COMPLETE: {user}")
print("=" * 60)
