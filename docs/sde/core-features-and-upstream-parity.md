# Core SDE features and upstream parity (post-pull checklist)

**In plain words:** after you **pull latest `main`**, use this page to see what the **local `sde` CLI** already does versus patterns in mature **coding-agent harnesses** (e.g. SWE-agent, OpenHands). It is **not** a line-by-line port list; it is the **contract** for what is implemented in *this* repo today and what remains **reasonable next work** under the **local-only** product decision.

**Related:** license notes when copying from upstream trees — [`upstream-harvest-licenses.md`](upstream-harvest-licenses.md). Trajectory / replay design notes — [`../superpowers/specs/2026-04-18-sde-trajectory-replay-cli-design.md`](../superpowers/specs/2026-04-18-sde-trajectory-replay-cli-design.md).

---

## Implemented core features (this repo)

| Area | What you get | Primary code / artifacts |
|------|----------------|---------------------------|
| **Staged pipeline** | `baseline` vs `guarded_pipeline` (planner → executor → verifier → optional fix → finalize) | `src/sde_modes/modes/`, `traces.jsonl` |
| **CTO-style gates** | `review.json`, `token_context.json`, `balanced_gates`, `validation_ready`, hard-stops **HS01–HS06** | `src/sde_gates/`, [`execution.md`](../coding-agent/execution.md) |
| **Static code + security gates** | `static_gates_report.json`: AST parse, high-signal dangerous patterns, optional **`ruff`**, **`bandit`**, **`basedpyright`/`pyright`** on `PATH`; failures in **verifier** and **HS04** | `src/sde_gates/static_analysis.py`, `verifier_report` |
| **Run manifests** | `run-manifest.json` for every `sde run` (task + mode + run_id) | `src/sde_pipeline/runner/single_task.py` |
| **Repeat execution (V1)** | `sde run … --repeat N` (isolated run dirs; envelope lists `runs[]`, `validation_ready_all`) | `single_task.execute_single_task`, CLI `run` |
| **Completion skeleton (guarded)** | `program/*`, `step_reviews/*.json`, `verification_bundle.json`, `review.json` → `definition_of_done`; HS07–HS16 on `guarded_pipeline` when not a safety refusal | `completion_layer.py`, `hard_stops_guarded.py`, `manifest.py` |
| **Event / replay lineage (all modes)** | `replay_manifest.json` (SHA256 of `traces.jsonl`), `event_store/run_events.jsonl` (envelope `contract_version` **1.0**), `kill_switch_state.json`; HS17–HS20 unless `summary.json` → `run_class: coding_only` | `event_lineage_layer.py`, `hard_stops_events.py` |
| **Memory harness (all modes)** | `memory/retrieval_bundle.json` (chunks cite `event_store` **event_id**), `quarantine.jsonl`, `quality_metrics.json`, `capability/skill_nodes.json`; HS21–HS24 (skipped for `coding_only`) | `memory_artifact_layer.py`, `hard_stops_memory.py` |
| **Evolution harness** | `learning/reflection_bundle.json`, `canary_report.json`, `lifecycle/promotion_package.json`, `practice/*`; HS25–HS28 | `evolution_layer.py`, `hard_stops_evolution.py` |
| **Organization harness** | `coordination/lease_table.json`, `iam/*`, `orchestration/shard_map.json`, `strategy/proposal.json`; HS29–HS32 | `organization_layer.py`, `hard_stops_organization.py` |
| **Validate existing run** | `sde validate --run-id …` → `validate_run`: **single-task** → `validate_execution_run_directory` (exit **0** iff `ok` ∧ `validation_ready`); **benchmark-only dir** → aggregate integrity (`run_kind: benchmark_aggregate`, `execution_gates_applied: false`, exit **0** iff `ok`) | `orchestrator/api/validate_run.py`, CLI `validate` |
| **Benchmark manifests + batch ergonomics** | `benchmark-manifest.json`, **`benchmark-checkpoint.json`** (per-task); `--max-tasks`, `--continue-on-error`, **`--resume-run-id`** | `src/sde_pipeline/benchmark/` |
| **Project driver (meta-orchestrator)** | **`sde project run`** / **`validate`** / **`status`** (`--session-dir` \| **`--plan`**, optional **`--progress-file`**, **`--parallel-worktrees`**, **`--lease-stale-sec`**, validate-only **`--skip-workspace`**, status **`--max-concurrent-agents`** for next-tick hint). **`sde continuous`** same run path via **`--project-session-dir`** \| **`--project-plan`**. Session `project_plan.json` + `progress.json` (path overridable); **ContextPack** + `execute_single_task`; **`run-manifest`** project fields; **`verification/`** + **`verification_aggregate.json`**; **`definition_of_done.json`** + **`stop_report.json`**; **`driver_state.json`** terminal **`exit_code`**; append-only **`session_events.jsonl`** on driver milestones; **`project status`** also surfaces **verification aggregate**, session **DoD**, and **step_runs** tail stats (Phase 12) with **bounded reads** for large artifacts (Phase 13) and **context pack lineage** plus **context_packs/** / **verification/** inventories (Phase 14), **leases** body + **parallel worktrees** dir (Phase 15), **plan_step_rollups** (Phase 16), **step_runs latest-by-step** + rollup run pointers when the JSONL fits the scan cap (Phase 17), **repo git snapshot** via **`--repo-root`** (Phase 18), and **plan workspace** (branch match + **path prefix** vs ``path_scope`` checks, Phases 19–20), plus **status_at_a_glance** (Phase 21: compact roll-up + ``red_flags``). **`--stop-when`** = task-mode `continuous` only. **Parallel / workspace / leases** as in [`project-driver.md`](project-driver.md). | [`project-driver.md`](project-driver.md), `src/orchestrator/api/project_*.py`, `context_pack.py`, `project_aggregate.py`, `project_stop.py`, `project_workspace.py`, `project_validate.py`, `project_status.py`, `project_events.py`, CLI |
| **Trajectory narrative + rerun** | `sde replay --run-id …` (`--format json|html`, `--write-html` → `trajectory.html`, `--rerun` for single-task from manifest) | `src/sde_pipeline/replay.py`, CLI |
| **Input safety (keyword refusal)** | Expanded refusal markers in task text | `src/sde_foundations/safeguards.py` |
| **Verifier checklist (docs)** | Heuristic checklist for prompts / review culture | [`prompts/verifier-heuristic-checklist.md`](prompts/verifier-heuristic-checklist.md) |

---

## Parity with SWE-agent / OpenHands (local CLI scope)

**Deliberately not targeted here:** Docker sandboxes, remote runtimes (E2B, Daytona, …), browser tools, full repo edit/test loops inside a container. Those are **infra-heavy**; this SDE stays a **local Ollama-first CLI** unless the product explicitly expands.

| Upstream theme | In this repo today | Gap / next step (still local) |
|----------------|-------------------|------------------------------|
| Trajectories + inspect | `traces.jsonl`, `orchestration.jsonl`, `sde replay`, `run.log`, **`trajectory.html`** via `--write-html` or `--format html` | Richer tables / filters (optional future) |
| Batch / suite | `sde benchmark` + manifests + caps + **checkpoint resume** | Suite **versioning** in summary (optional polish) |
| Lint / security | `static_gates_report.json` + optional `ruff` / `bandit` / `basedpyright`/`pyright` | Tune severities; add **`semgrep`** optional profile (future) |
| Reviewer agent | Heuristic verifier + `review.json` gate_snapshot | Optional **second-pass LLM reviewer** behind flag (tokens + contract) |
| Skills / playbooks | `docs/sde/prompts/*` | Keep prompts **versioned** next to gate changes |

---

## Suggested implementation order (core only)

1. ~~**Optional linters** — `bandit` / `basedpyright`~~ **Done** — same “binary on `PATH`” pattern as `ruff`; see `static_gates_report.json` keys `bandit` / `basedpyright`.
2. ~~**Trajectory viewer**~~ **Done (MVP)** — `sde replay --write-html` or `--format html` writes / prints `trajectory.html` under the run directory.
3. ~~**Benchmark resume**~~ **Done** — `benchmark-checkpoint.json` + `sde benchmark --resume-run-id <run_id>`; traces append per task so partial progress survives crashes.

When any remaining item ships, update **`what.md`**, this file, and **`implementation-contract.md`** in the same PR.
