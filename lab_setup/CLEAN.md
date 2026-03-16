# README Cleanup Plan

Findings from comparing `lab_setup/README.md` against the actual codebase.

---

## Issues Found

### 1. `prepare_material.sh` doesn't exist (Lines 5–9)

The README opens with:

> **Participant Materials:** To create the zip file for participants to upload to Databricks, run:
> `./lab_setup/prepare_material.sh`

This script doesn't exist anywhere in the repo. The setup CLI now uploads notebooks directly to the workspace via `databricks-setup setup` (Track B) and `databricks-setup sync`.

**Question:** Is the DBC/zip participant flow dead? Should this entire block be removed, or replaced with a reference to `databricks-setup sync`?

---

### 2. `DATABRICKS_ACCOUNT_ID` missing from `.env.example` (Lines 163–171, 228–229)

Steps 2.1 and 3.1 tell the admin to set `DATABRICKS_ACCOUNT_ID` in `.env`, but that variable is **not in `.env.example`**. The code does require it — `groups.py:53` reads it via `os.getenv("DATABRICKS_ACCOUNT_ID")` and raises if missing. Admins copying `.env.example` won't know to add it.

**Action:** Add `DATABRICKS_ACCOUNT_ID=""` to `.env.example` under a "Permissions" or "Account" section.

**Question:** Should this go next to the existing `GROUP_NAME` entry? Or in its own "Account Admin" section?

---

### 3. `GROUP_NAME` in `.env.example` is unused by the code

`.env.example` has `GROUP_NAME="aircraft_workshop_group"`, but `groups.py` hardcodes `WORKSHOP_GROUP = "aircraft_workshop_group"` and `Config.load()` never reads `GROUP_NAME` from the environment.

**Question:** Should the code be updated to read `GROUP_NAME` from env, or should the variable be removed from `.env.example` (with a comment that the group name is hardcoded)?

---

### 4. `sync` command missing from CLI Command Reference (Lines 383–389)

The CLI has a `sync` command (`databricks-setup sync` — uploads/syncs notebooks to the workspace) that is not listed in the command reference table.

**Action:** Add `databricks-setup sync` to the reference table.

---

### 5. Step 4 "Quick Start Instructions" appears outdated (Lines 296–305)

Step 4 tells participants to:

1. Download `aircraft_etl_to_neo4j.dbc`
2. Import the DBC into their workspace

But `databricks-setup setup` (Track B) already uploads all notebooks to `/Shared/databricks-neo4j-lab/`. Participants don't need to download and import anything — they navigate to the shared folder.

**Question:** Is the DBC participant flow still used at all, or has it been fully replaced by the CLI upload? If replaced, Step 4 needs a rewrite.

---

### 6. Auto-termination default is inconsistent (Line 413)

- README says: "Set to 30 minutes by default"
- `ClusterConfig` default: `autotermination_minutes = 30`
- `.env.example`: `AUTOTERMINATION_MINUTES="60"`

The `.env.example` overrides the code default. An admin who copies `.env.example` gets 60 minutes, not 30.

**Question:** Which is the intended default — 30 or 60? README and `.env.example` should agree.

---

### 7. Instance type "m5.xlarge per user" is wrong (Line 411)

README says "plan for one m5.xlarge per user" under Cost Considerations, but the code default in `config.py:52` is `m5.large` (8 GB, 2 cores), not `m5.xlarge` (16 GB, 4 cores).

**Action:** Update to `m5.large` to match the code default.

---

### 8. Pre-Workshop Checklist item "Configure Databricks Genie Space" has no instructions (Line 22)

The checklist says:
> - [ ] Configure Databricks Genie Space (Lab 6)

But there are no instructions anywhere in the README for how to do this. The troubleshooting section mentions Genie briefly, and Step 4 references a Genie Space ID, but there's no actual "how to set up Genie" section.

**Question:** Should a Genie setup section be added? Or is this documented elsewhere and just needs a link? Or has Lab 6 changed scope (CLAUDE.md describes it as the multi-agent supervisor, not Genie setup)?

---

### 9. File count claim may drift (Line 404)

README says "25 files" (22 CSV + 3 Markdown). Currently correct — `DataConfig.excluded_files` filters out `ARCHITECTURE.md` and `README_LARGE_DATASET.md`, leaving 22 CSV + 3 maintenance manuals = 25. However, the actual directory has 22 CSV + 5 MD total.

**Action:** No change needed now, but consider removing the hard count ("25 files") and just saying "CSV and Markdown files" to prevent future drift. Or keep it and note the exclusions.

---

### 10. `users.csv` doesn't exist in the repo (Lines 233–241)

The README correctly describes the format but doesn't explicitly say the admin must **create** this file — it reads as if the file already exists and just needs editing. The `.env.example` has `USERS_CSV=""` which defaults to `lab_setup/users.csv`.

**Action:** Add a note like "Create this file — it is not included in the repository" or add a `users.csv.example` template.

---

### 11. Notebook upload details are buried / not explained well

Track B's description (lines 196–197) says "Uploads workshop notebooks to the shared workspace folder" but doesn't mention which notebooks or where they end up. The `NotebookConfig` in the code shows:
- Lab 5 notebooks (2 ipynb files)
- Lab 7 notebooks (3 ipynb + 1 py)
- neo4j_mcp_connection (1 py + 2 ipynb)

All uploaded to `/Shared/databricks-neo4j-lab/`.

**Question:** Should Track B's description include the workspace path and notebook list? Or is this too much detail for the README?

---

## Summary of Required Decisions

| # | Question | Options |
|---|----------|---------|
| 1 | Is `prepare_material.sh` dead? | Remove block / Replace with `sync` reference |
| 3 | Should `GROUP_NAME` env var work? | Wire it up in code / Remove from `.env.example` |
| 5 | Is the DBC participant flow dead? | Rewrite Step 4 / Keep both flows |
| 6 | Auto-termination: 30 or 60 min? | Align README + `.env.example` |
| 8 | Genie setup instructions? | Add section / Link elsewhere / Remove checklist item |
| 11 | How much notebook detail in Track B? | Minimal / Full list |

## Actions I Can Take Without Questions

| # | Action |
|---|--------|
| 2 | Add `DATABRICKS_ACCOUNT_ID` to `.env.example` |
| 4 | Add `sync` command to CLI reference |
| 7 | Fix instance type to `m5.large` |
| 9 | Keep or soften file count |
| 10 | Clarify that `users.csv` must be created |
