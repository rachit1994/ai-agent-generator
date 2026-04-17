# Orchestrator service (`src/services/orchestrator`)

Aligned to [docs/operating-system-folder-structure.md](../../../docs/operating-system-folder-structure.md) **service atomicity**: this folder is one deployable unit with a stable internal layout.

## Layout

| Path | Role |
|------|------|
| `api/` | Public import surface and HTTP/RPC boundaries when the service exposes an API. |
| `runtime/sde/` | **SDE** Python package: local CLI (`sde` / `agent` entrypoints), benchmark runner, CTO gate helpers, orchestration modes. Built as a wheel from repo `pyproject.toml`. |
| `tests/` | Service tests (`pytest` testpaths point at `tests/unit/`). |
| `README.md` | This file. |

## Outputs

Run artifacts are written only under **repository root** `outputs/runs/<run-id>/` (see `sde.utils.outputs_base`). They are gitignored; do not commit traces or reports into `src/`.
