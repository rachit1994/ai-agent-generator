# SDE — Planning pipeline (sequential + parallel)

This document is the **single planning-agent output**: it defines the order of work and what may run in parallel to ship the **execution extension** (see [`docs/coding-agent/execution.md`](../coding-agent/execution.md)).

## Sequential spine (blocking order)

These steps must complete in order; later steps assume earlier contracts exist.

1. **Spec lock** — Freeze `docs/coding-agent/execution.md` (artifacts, CTO hard-stops, strict balanced gates).
2. **Runtime contract** — Orchestrator writes all required per-run artifacts under `outputs/runs/<run-id>/` (including `review.json`, `token_context.json`, `balanced_gates`, multi-file `outputs/`, `run.log`).
3. **Gate implementation** — Python module evaluates hard-stops and balanced scores from on-disk evidence (`sde/cto_gates.py`).
4. **Quality tests** — Unit tests assert CTO / strict readiness on a deterministic fake run (`test_cto_gates.py`).
5. **Demo validation** — `demo_apps/sde-demo/` tasks exercised via `sde benchmark` (or `sde run`) to prove end-to-end behavior. Seed the tree with `cp -R docs/templates/sde-demo demo_apps/sde-demo` (`demo_apps/` is gitignored).

## Parallel lanes (safe after step 1)

After the spec is fixed, these workstreams have **weak coupling** and can proceed in parallel once shared types (trace event shape, `summary.json` keys) are agreed:

| Lane | Scope | Touches |
|------|--------|---------|
| A | Human-readable run narrative | `run_logging.py`, `runner.py` |
| B | CTO math and artifacts | `cto_gates.py`, `runner.py` |
| C | Report surfaces for humans | `report.py` |
| D | Demo suite + sample project | `demo_apps/` (ignored; template `docs/templates/sde-demo/`), `docs/sde/multi-agent-build.md` |

**Merge rule:** all lanes reconcile on `runner.py` and `summary.json`; one owning PR should integrate runner changes to avoid drift.

## Exit criteria (planning agent)

- Paths documented only under `docs/` (alongside `docs/sde/`), not a dedicated version-numbered subtree for the main execution spec.
- `validate_execution_run_directory` returns `validation_ready` and `ok` on a green reference run.
- Demo `tasks.jsonl` runs without structural errors (model quality may vary by environment).

See [`multi-agent-build.md`](multi-agent-build.md) for which implementation roles map to which code units.
