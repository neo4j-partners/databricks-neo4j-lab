# notebook_validation Structure

*Restructure complete. All Python files live in `agent_modules/`.*

---

## Layout

```
notebook_validation/
├── pyproject.toml                 (uv/hatchling config for local dev)
├── .env / .env.example
├── upload.sh / submit.sh / validate.sh
├── MEMORY.md / LAB7_VALIDATION.md / RESTRUCTURE.md
└── agent_modules/
    ├── __init__.py
    ├── data_utils.py              (shared utilities: embeddings, Neo4j, data loading)
    ├── test_hello.py              (smoke test for cluster execution)
    ├── run_lab5_02.py             (Lab 5 full data load validation)
    ├── run_lab7_03.py             (Lab 7 embedding pipeline validation)
    └── <future agent modules per MEMORY.md>
```

## Organizing Principle

All Python files live in `agent_modules/`. Shell scripts and docs stay at the top level. The `pyproject.toml` at the top level lets `uv sync` resolve dependencies for local development (IDE support, linting, type checking).

## Why agent_modules/ and Not src/

In Python, `src/` conventionally signals the [src layout](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/) packaging pattern, where `src/package_name/` contains a pip-installable package. The Hitchhiker's Guide to Python explicitly advises against placing library code in "an ambiguous src or python subdirectory." `agent_modules/` describes what the directory contains without conflicting with established Python conventions.

## Import Strategy

Two environments, two import styles, no conflict:

**Cluster scripts** (submitted via `submit.sh`): `spark_python_task` adds the script's parent directory to `sys.path`. Since all scripts are in `agent_modules/`, bare imports work:
```python
from data_utils import VolumeDataLoader  # resolves in agent_modules/
```

**MLflow-bundled modules** (deployed to Model Serving): `code_paths=["agent_modules"]` copies to `code/agent_modules/` and adds `code/` to `sys.path`. Package-qualified or relative imports work:
```python
from agent_modules.data_utils import VolumeDataLoader
from .data_utils import VolumeDataLoader  # relative
```

Scripts are never bundled into MLflow. Agent modules are never submitted directly. The two import styles do not conflict.

## Shell Script Behavior

- `./upload.sh` — uploads `test_hello.py` from `agent_modules/`
- `./upload.sh run_lab5_02.py` — uploads specific file from `agent_modules/`
- `./upload.sh --all` — uploads all `agent_modules/*.py`
- `./submit.sh run_lab5_02.py` — submits `$REMOTE_DIR/agent_modules/run_lab5_02.py`
- `./validate.sh` — lists remote workspace contents
- `./validate.sh run_lab5_02.py` — checks specific file exists in `agent_modules/`

## Fast Iteration on agent_modules/

The upload-submit-inspect loop from DBX_LOCAL_DEVELOPMENT.md applies unchanged. For future agent modules, a test script (e.g., `test_agent_modules.py`) exercises modules on the cluster without a full MLflow deploy cycle:

```
edit agent_modules/graph_tools.py → upload --all → submit test_agent_modules.py → inspect
```

The script has two modes:

- **Default (import-and-smoke):** Imports every module, verifies classes instantiate and callables have expected signatures. Seconds to run.
- **`--full` flag:** Exercises tools against live Neo4j and the warehouse. Minutes to run. Use before a deploy.

## Local Development

```bash
cd lab_setup/notebook_validation
uv sync              # install dependencies
uv sync --group dev  # also install pyspark for IDE support
```

No CLI entry points. Scripts are submitted to Databricks, not run locally.
