# SDE implementation contract

**Reading path:** open this **only when** you change run artifacts or pipeline outputs — see **[`../ESSENTIAL.md`](../ESSENTIAL.md)** §3.

**In plain words:** this is the **checklist of files and stages** a baseline run is expected to produce. Think “**if these files are missing or empty, the run is incomplete**,” not product marketing. For stricter rules (extra artifacts, hard-stops), see **`src/sde_gates/`** and tests that call **`validate_execution_run_directory`**.

---

## Contract

- Stage 1 on a **session directory** (often with **`intake/`**): optional **`sde project plan-lock`**, **`sde project validate --require-plan-lock`**, **`sde project run`** / **`sde continuous`** with **`--enforce-plan-lock`**, and optional strict reviewer via **`--require-non-stub-reviewer`** or env **`SDE_REQUIRE_NON_STUB_REVIEWER`** (pairing rules in **[`project-driver.md`](project-driver.md)** and **[`../runbooks/stage1-intake-failures.md`](../runbooks/stage1-intake-failures.md)**); may write **`project_plan_lock.json`**.
- In scope: local CLI MVP with `run`, `benchmark`, `report`, **`replay`**, **`validate`**, **`project`** (meta-orchestrator: session `project_plan.json` → optional **`workspace`** contract (branch + allowed path prefixes + optional **lease TTL**), **`project validate`** read-only preflight, **`project status`** read-only snapshot (including aggregate / session DoD / ``step_runs`` when present; **Phase 13** byte caps / JSONL tail scan for very large files; **Phase 14** ``context_pack_lineage`` + ``context_packs`` / ``verification`` directory summaries with capped ``step_ids``; **Phase 15** capped ``leases.json`` body + ``_worktrees`` as ``parallel_worktrees``; **Phase 16** ``plan_step_rollups``; **Phase 17** ``step_runs.by_step`` + rollup run pointers when JSONL is small enough to fully scan; **Phase 18** ``repo_snapshot`` when ``repo_root`` is set; **Phase 19–20** ``workspace_status``: plan ``workspace`` echo, branch commit match, and ``allowed_path_prefixes`` vs ``path_scope`` errors; **Phase 21** ``status_at_a_glance`` (compact derived fields + ``red_flags``), **`session_events.jsonl`** on driver runs, per-step `execute_single_task` + orchestrator verification + `progress.json` (optional **`--progress-file`** override) + **`verification_aggregate.json`** + session **`definition_of_done.json`** + terminal **`stop_report.json`** / **`driver_state.json`** exit metadata; optional **`--parallel-worktrees`** when the repo is git and the scheduler picks disjoint-scoped steps; see **[`project-driver.md`](project-driver.md)**), and **`continuous`** (repeat `--task` **or** drive **`--project-session-dir`** / **`--project-plan`** with optional **`--progress-file`** and optional **`--parallel-worktrees`**). **`validate`** re-checks `outputs/runs/<id>/` (**single-task** → manifest + hard-stops, exit **0** when `ok` and `validation_ready`; **benchmark aggregate** → light integrity, exit **0** when `ok`, fields `run_kind` / `execution_gates_applied` in JSON).
- Out of scope: UI, cloud deployment, and production architecture refactors (see also **`what.md`** “Out of scope”).
- Guardrails: input validation, output schema validation, refusal policy, retry cap, timeout cap, token cap, **static code gates** (AST + security patterns + optional `ruff` / `bandit` / `basedpyright` or `pyright` on `PATH`).
- Pipeline stages (sequential, never skipped): `planner_doc -> planner_prompt -> executor -> verifier -> executor_fix(optional, max 1) -> verifier_fix(optional) -> finalize`.
- Required artifacts:
  - per-run traces: `traces.jsonl`, `summary.json`, `report.md`
  - per-run run log: `orchestration.jsonl`, `run.log`
  - per-run **manifest**: `run-manifest.json` (always for `sde run`; task + mode for replay / audit; optional **`project_step_id`** / **`project_session_dir`** when the attempt was started from the **project driver** — Phase 1 traceability to the session plan)
  - **`sde run --repeat N`**: **N** independent runs (each its own `run-manifest.json` and `outputs/runs/<run-id>/`); JSON envelope when **N > 1** (see **`docs/sde/what.md`** RepeatProfile / multi-run envelope)
  - CTO / V1 gate files: `review.json`, `token_context.json`, **`static_gates_report.json`** (successful parse path)
  - per-run generated outputs (when applicable): `answer.txt`, `generated_script.py`
  - per-run pipeline artifacts (guarded_pipeline): `planner_doc.md`, `executor_prompt.txt`, `verifier_report.json`
- Benchmark runs additionally persist **`benchmark-manifest.json`** and incremental **`benchmark-checkpoint.json`** (per-task progress); CLI supports **`--max-tasks`**, **`--continue-on-error`**, and **`--resume-run-id`** (same `outputs/runs/<id>` directory; suite path and mode must match the manifest).
- Required metrics: pass rate, reliability, p50/p95 latency, estimated cost, validity rate, retry frequency.

**Feature status vs upstream harnesses:** [`core-features-and-upstream-parity.md`](core-features-and-upstream-parity.md).

## Assumptions

- Local runtime uses Ollama by default.
- Implementation model is `qwen3:14b`; support model is `gemma 4`.
- API provider exists only as fallback and must be explicitly justified in report.

## Risks

- Missing local model pulls can block benchmark execution.
- Non-JSON model outputs can fail closed and reduce pass rate.
- Latency may regress under guarded mode due to extra stages.
