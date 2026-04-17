# SDE — Multi-agent build map

**In plain words:** one product feature is often built by **several “hats”** (planner, implementer, reviewer). This page is a **simple org chart for code** — which **Python areas** own which hat — so people (and LLMs) do not edit the wrong package.

The execution extension is delivered by **multiple implementation roles** coordinated by the orchestrator. This map ties **roles** to **modules** so ownership stays clear under `src/sde_*` packages and `src/orchestrator/` (aligned to `docs/architecture/operating-system-folder-structure.md`).

## Roles

| Agent role | Responsibility | Primary modules |
|------------|----------------|-----------------|
| **PlanningAgent** (singleton) | Emits sequential + parallel plan; does not mutate runtime. | [`pipeline-plan.md`](pipeline-plan.md), [`docs/coding-agent/execution.md`](../coding-agent/execution.md) |
| **PlannerDoc** | Markdown plan, API/data/security/test notes. | `sde_modes/modes/guarded_pipeline/planner.py` (`planner_doc` stage) |
| **PlannerPrompt** | Executor-bound prompt from plan. | `sde_modes/modes/guarded_pipeline/planner.py` (`planner_prompt` stage) |
| **Executor** | Code / structured answer. | `sde_modes/modes/guarded_pipeline/executor.py`, `sde_modes/modes/baseline/pipeline.py`, `sde_foundations/model_adapter.py` |
| **Verifier** | Quality and policy checks on executor output. | `sde_modes/modes/guarded_pipeline/verify_pass.py` (`verifier`, `verifier_fix`) |
| **GateEvaluator** | CTO strict gates, `balanced_gates`, hard-stops HS01–HS06. | `sde_gates/` (`hard_stops.py`, `balanced_gates.py`, `review.py`, …) |
| **RunArchivist** | Traces, orchestration JSONL, `run.log`, `report.md`. | `sde_pipeline/runner/single_task.py`, `sde_foundations/storage.py`, `sde_pipeline/run_logging.py`, `sde_pipeline/report.py` |

## Handoff contracts

- **PlannerDoc → PlannerPrompt:** planning markdown string.
- **PlannerPrompt → Executor:** single prompt string (stored as `executor_prompt.txt` when guarded).
- **Executor → Verifier:** candidate answer / code string.
- **Verifier → GateEvaluator:** `verifier_report` dict plus `traces.jsonl` events.
- **GateEvaluator → RunArchivist:** `review.json`, `token_context.json`, `summary.json` `balanced_gates` / `quality.validation_ready`.

## Quality standard

- **Strict balanced:** reliability, delivery, governance each ≥ 85; composite ≥ 90 (see main V1 spec).
- **Hard-stops:** all HS01–HS06 must pass for `validation_ready`.
- **Observability:** every model stage appears in `traces.jsonl` and is summarized in `run.log`.
