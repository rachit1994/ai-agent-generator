# Orchestrator service (`src/services/orchestrator`)

Aligned to [docs/operating-system-folder-structure.md](../../../docs/operating-system-folder-structure.md) **service atomicity**: one deployable unit with **`api/`**, **`runtime/`**, and **`tests/`** as intended in the master layout.

## Layout

| Path | Role |
|------|------|
| `orchestrator/api/` | **Public import surface** — re-exports `execute_single_task`, `run_benchmark`, `generate_report`. Other services or tools should import from `orchestrator.api`, not deep `runtime`. |
| `orchestrator/runtime/` | **Implementation** — CLI modules, modes, eval, storage, CTO gates, model adapter. |
| `tests/` | Pytest suite (`pytest` `testpaths` in `pyproject.toml`). |

The installable Python **import package** is **`orchestrator`** (directory `orchestrator/`). The published **distribution name** remains **`sde`** with console scripts `sde` and `agent`.

## Outputs

Run artifacts are written only under **repository root** `outputs/runs/<run-id>/` (see `orchestrator.runtime.utils.outputs_base`). They are gitignored; do not commit traces or reports into `src/`.
