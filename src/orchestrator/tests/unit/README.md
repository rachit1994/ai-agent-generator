# `src/orchestrator/tests/unit`

- Purpose: Fast unit tests for orchestrator runtime and API.
- Run: `uv run pytest src/orchestrator/tests/unit` (or `uv run pytest` from repo root per `pyproject.toml`).
- **CI parity:** GitHub Actions uses **Python 3.11** — when your default is **3.12+**, run **`uv run --python 3.11 pytest src/orchestrator/tests/unit -q`** (see repo-root **`.github/workflows/ci.yml`**).
