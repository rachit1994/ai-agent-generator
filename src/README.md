# `src`

Top-level source tree for this repository: **services**, future **contracts**, **tools**, and **tests** — not run artifacts or caches.

## Where to look first

- **Orchestrator service:** [`services/orchestrator/`](services/orchestrator/) — contains `orchestrator/api/` (public surface), `orchestrator/runtime/` (implementation), and `tests/`.
- **CLI:** `sde` / `agent` entrypoints → `orchestrator.runtime.cli.main:main` (`pyproject.toml`).
- **Tests:** [`services/orchestrator/tests/unit/`](services/orchestrator/tests/unit/).

## Documentation

Junior-friendly path through docs and code: **[../docs/developer-walkthrough.md](../docs/developer-walkthrough.md)**.
