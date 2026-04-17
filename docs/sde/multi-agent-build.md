# SDE — Multi-agent build map

The execution extension is delivered by **multiple implementation roles** coordinated by the orchestrator. This map ties **roles** to **modules** so ownership stays clear under `src/services/orchestrator/orchestrator/runtime/` (aligned to `docs/operating-system-folder-structure.md`).

## Roles

| Agent role | Responsibility | Primary modules |
|------------|----------------|-----------------|
| **PlanningAgent** (singleton) | Emits sequential + parallel plan; does not mutate runtime. | [`pipeline-plan.md`](pipeline-plan.md), [`docs/coding-agent/execution.md`](../coding-agent/execution.md) |
| **PlannerDoc** | Markdown plan, API/data/security/test notes. | `modes/guarded_pipeline.py` (`planner_doc` stage) |
| **PlannerPrompt** | Executor-bound prompt from plan. | `modes/guarded_pipeline.py` (`planner_prompt` stage) |
| **Executor** | Code / structured answer. | `modes/guarded_pipeline.py`, `modes/baseline.py`, `model_adapter.py` |
| **Verifier** | Quality and policy checks on executor output. | `modes/guarded_pipeline.py` (`verifier`, `verifier_fix`) |
| **GateEvaluator** | CTO strict gates, `balanced_gates`, hard-stops HS01–HS06. | `cto_gates.py` |
| **RunArchivist** | Traces, orchestration JSONL, `run.log`, `report.md`. | `runner.py`, `storage.py`, `run_logging.py`, `report.py` |

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
