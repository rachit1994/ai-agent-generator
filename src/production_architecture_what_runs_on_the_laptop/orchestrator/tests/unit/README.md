# `src/production_architecture_what_runs_on_the_laptop/orchestrator/tests/unit`

- Purpose: Fast unit tests for orchestrator runtime and API.
- Run: `uv run pytest src/production_architecture_what_runs_on_the_laptop/orchestrator/tests/unit` (or `uv run pytest` from repo root per `pyproject.toml`). **`uv`** should use **3.11** via repo-root **`.python-version`** (same as [`.github/workflows/ci.yml`](../../../../.github/workflows/ci.yml)); confirm **`uv run python -V`**, or pass **`--python 3.11`** if **`uv`** is not honoring the pin.
