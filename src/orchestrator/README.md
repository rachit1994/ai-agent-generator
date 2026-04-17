# Orchestrator (`src/orchestrator`)

Aligned to [docs/architecture/operating-system-folder-structure.md](../../docs/architecture/operating-system-folder-structure.md): the **SDE orchestrator** Python package lives here as `src/orchestrator/` (import name **`orchestrator`**). Runnable pipeline and modes live in sibling packages **`sde_pipeline`**, **`sde_modes`**, **`sde_gates`**, **`sde_foundations`** under `src/`.

## Layout

| Path | Role |
|------|------|
| `api/` | **Public import surface** — `from orchestrator.api import execute_single_task`, `run_benchmark`, `generate_report`. |
| `runtime/` | **CLI only** — `runtime/cli/`; pipeline and modes are in `sde_*` siblings. |
| `tests/` | Pytest suite (`testpaths` in repo `pyproject.toml`). |

The import package name is **`orchestrator`**. The published **distribution name** is **`sde`** (`sde` / `agent` entry points in `pyproject.toml`).

## Outputs

Run artifacts go to **repository root** `outputs/runs/<run-id>/` via `sde_foundations.utils.outputs_base`.
