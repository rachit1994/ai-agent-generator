# `orchestrator.api`

**Docs:** read **[`../../../docs/ESSENTIAL.md`](../../../docs/ESSENTIAL.md)** before you chase every file under `docs/`.

**In plain words:** this package is the **stable front door** for Python code that wants to drive SDE without reaching deep into `sde_pipeline` or `sde_modes`. The CLI in `orchestrator.runtime.cli.main` calls these same functions.

**CI:** [`.github/workflows/ci.yml`](../../../.github/workflows/ci.yml) runs **Python 3.11**; from repo root use **`uv run --python 3.11 pytest src/orchestrator/tests/unit/ -q`** before pushing if your default Python is newer.

Prefer:

```python
from orchestrator.api import (
    apply_intake_doc_review_result,
    append_roadmap_learning_line,
    build_project_stage1_observability_export,
    evaluate_project_plan_lock_readiness,
    lineage_manifest_session_event_snapshot,
    describe_project_session,
    execute_single_task,
    generate_report,
    replay_run,
    roadmap_review,
    run_benchmark,
    run_bounded_evolve_loop,
    run_continuous_project_session,
    run_continuous_until,
    run_project_session,
    stage1_observability_export_schema_errors,
    write_intake_lineage_manifest,
    write_project_plan_lock,
    write_project_stage1_observability_export,
    scaffold_project_intake,
    intake_merge_anchor_present,
    validate_project_session,
    validate_run,
)
```

| Import | Everyday job |
|--------|----------------|
| `execute_single_task` | One task → one folder under `outputs/runs/<id>/`. |
| `run_benchmark` / `generate_report` / `replay_run` | Suite runs, Markdown report, trajectory / optional rerun. |
| `validate_run` | Check an existing run folder (strict single-task contract **or** light benchmark-dir check). |
| `roadmap_review` / `append_roadmap_learning_line` | Ask the support model for a roadmap % digest; append a learning JSONL line. |
| `run_bounded_evolve_loop` | Bounded “review → optional task → repeat” cadence (not magic completion). |
| `run_continuous_until` / `run_continuous_project_session` | Task repeat loop **or** project session loop used by `sde continuous`. In project mode, optional `enforce_plan_lock` and `require_non_stub_reviewer` match CLI `--enforce-plan-lock` / `--require-non-stub-reviewer` (strict reviewer only applies when the lock is enforced). |
| `run_project_session` | Meta-orchestrator: walk `project_plan.json` steps, verification, progress (see `docs/sde/project-driver.md`). Optional `enforce_plan_lock` runs `evaluate_project_plan_lock_readiness` before steps; with `require_non_stub_reviewer=True`, readiness uses `allow_local_stub_attestation=False` (same policy as strict `plan-lock` / `validate --require-plan-lock`). Defaults stay permissive for tests and golden flows. |
| `validate_project_session` / `describe_project_session` | Read-only plan + workspace checks; full JSON status snapshot (`status_at_a_glance`, rollups, caps). `describe_project_session` merges `intake_lineage_manifest_*` into the `session_events` block (same contract as driver `session_events.jsonl` lines). |
| `build_project_stage1_observability_export` / `write_project_stage1_observability_export` / `stage1_observability_export_schema_errors` | Versioned JSON export for Stage 1 revise/status glance (CLI: `sde project export-stage1-observability`). |
| `scaffold_project_intake` | Write `intake/` Stage 1 stubs under a session dir (CLI: `sde project scaffold-intake`); does not edit `project_plan.json`. |
| `apply_intake_doc_review_result` | Apply bounded intake revise-loop state from `intake/doc_review.json` (review fail -> retry count -> `blocked_human` at retry cap). |
| `write_intake_lineage_manifest` | Write `intake/lineage_manifest.json` with `sha256` hashes for Stage 1 artifacts used by lock-readiness checks. |
| `lineage_manifest_session_event_snapshot` | Read-only summary of that manifest for `session_events.jsonl` payloads and `describe_project_session` → `session_events` (`intake_lineage_manifest_*` fields). |
| `evaluate_project_plan_lock_readiness` / `write_project_plan_lock` | Evaluate Stage 1 lock-readiness (intake artifacts + reviewer outcome + lineage + plan metadata) and optionally write `project_plan_lock.json`. |
| `intake_merge_anchor_present` | Read-only: true when `intake/discovery.json` or `intake/doc_review.json` is present **and schema-valid** (same rule as context packs / `project status`). |

Use **`from orchestrator.api import …`** instead of importing `sde_pipeline`, `sde_modes`, or `sde_foundations` directly from outside this service (except tests and internal extensions).
