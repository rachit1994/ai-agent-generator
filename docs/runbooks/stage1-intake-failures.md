# Stage 1 intake failure runbook

This runbook covers Stage 1 intake failure modes for `OSV-STORY-01` in the local orchestrator spine.

## OSV-STORY-01 status (done vs remaining)

Mapped to `docs/versioning/plans/story-01-stage1-intake.md` sections 4-6.

Implemented now:

- [x] `discovery.json` schema checks (`goal_excerpt` non-empty for anchor semantics)
- [x] `research_digest.md` + `question_workbook.jsonl` presence in lock-readiness checks
- [x] `doc_review.json` schema validation (`passed` bool + `findings` list/dict), fail-closed in validate
- [x] bounded revise loop with deterministic `blocked_human` after retry cap
- [x] lock-readiness evaluation + lock artifact (`project_plan_lock.json`)
- [x] run-time lock enforcement (`sde project run --enforce-plan-lock`)
- [x] preflight lock enforcement (`sde project validate --require-plan-lock`)
- [x] golden Stage 1 success + failure tests in `src/orchestrator/tests/unit/test_stage1_golden_flow.py`
- [x] runbook + runbook consistency test
- [x] CI wall-clock SLO for Stage 1 preflight (`STAGE1_SUITE_MAX_SECONDS` in `scripts/run-stage1-suite.sh`, set in CI)
- [x] intake `lineage_manifest.json` + hash checks at plan-lock readiness
- [x] session-local revise metrics (`intake/revise_metrics.jsonl`) surfaced via `project status`
- [x] structured Stage 1 observability export (`intake/stage1_observability_export.json`) via `sde project export-stage1-observability` (schema validated in tests; `revise_metrics` + `status_at_a_glance`)
- [x] golden cold-start command narrative: `./scripts/stage1-cold-start-demo.sh` (mirrors `test_stage1_golden_flow.py` success path; exercised by `test_stage1_cold_start_demo.py` in the Stage 1 suite)

Remaining for full Stage 1 closure:

- [ ] independent reviewer identity/credentials boundary with audit proof (not local stub reviewer)
- [ ] full autonomous model-driven revise/doc regeneration loop (current loop applies deterministic local regeneration only)
- [ ] durable platform lineage/event binding beyond session-local manifests
- [ ] production/local-prod observability service for `doc_review` latency + retry trends

## Structured observability export (doc_review / revise)

For automation, CI artifacts, or log scrapers, write a **small versioned JSON** file (default **`intake/stage1_observability_export.json`**) that embeds `revise_metrics` and `status_at_a_glance` from the same read-only snapshot as `project status`:

```bash
sde project export-stage1-observability --session-dir /path/to/session
```

Custom path:

```bash
sde project export-stage1-observability --session-dir /path/to/session --output /tmp/stage1_metrics.json
```

Contract: top-level `schema_version` **`1.0`**, `kind` **`project_stage1_observability`**, plus `captured_at`, `session_dir`, `revise_metrics`, `status_at_a_glance`. Validate with `stage1_observability_export_schema_errors` in `orchestrator.api` (used by unit tests).

## Golden cold start (operator demo, OSV-STORY-01 §5 / B5)

End-to-end **CLI** sequence from an empty session directory through scaffold → minimal `project_plan.json` → `intake-revise` → `plan-lock` → `validate --require-plan-lock` → `export-stage1-observability`. Expected end state: **`project_plan_lock.json`** with `locked: true`, validate **`exit_code` 0**, and **`intake/stage1_observability_export.json`** present.

From **repository root**:

```bash
./scripts/stage1-cold-start-demo.sh
```

Each `uv run sde …` step prints JSON to **stdout**; the script echoes the session path to **stderr**. Exits **`0`** only if every step succeeds. Uses a fresh temp session unless you pin a directory:

```bash
STAGE1_COLD_START_SESSION_DIR=/path/to/empty-session ./scripts/stage1-cold-start-demo.sh
```

**Per-step exit semantics (when invoked via `sde`):**

| Step | Command | Success exit |
|------|---------|---------------|
| 1 | `project scaffold-intake` | **0** (`ok` in JSON) |
| 2 | *(write `project_plan.json`; script uses fixed golden shape)* | — |
| 3 | `project intake-revise` | **0** if `review_passed`; **1** if `retry_allowed` / `blocked_human`; **2** on error |
| 4 | `project plan-lock` | **0** if ready and lock written; **1** if evaluated but not ready; **2** on hard failure |
| 5 | `project validate --require-plan-lock` | **0** ok; **1** workspace; **2** plan / lock failure |
| 6 | `project export-stage1-observability` | **0** if export written |

Automated parity: `src/orchestrator/tests/unit/test_stage1_cold_start_demo.py` runs this script (included in `./scripts/run-stage1-suite.sh`). The Python golden path remains in `test_stage1_golden_flow.py`.

## One-shot verification command

From repo root, run the Stage 1 verification subset:

```bash
./scripts/run-stage1-suite.sh
```

Optional local SLO (whole seconds, must be `>= 1` when set); fails with exit code 1 if the suite wall time exceeds the budget:

```bash
STAGE1_SUITE_MAX_SECONDS=300 ./scripts/run-stage1-suite.sh
```

Optional strict reviewer policy for **CLI** invocations only (does not change Python API defaults used by tests): when `SDE_REQUIRE_NON_STUB_REVIEWER` is `1`, `true`, `yes`, or `on`, these commands apply the same rules as `--require-non-stub-reviewer` without repeating the flag (useful in CI wrappers or shell profiles): `sde project plan-lock`, `sde project validate --require-plan-lock`, `sde project run --enforce-plan-lock`, and `sde continuous` when driving a project session with `--enforce-plan-lock`.

Equivalent inline command:

```bash
uv run pytest \
  src/orchestrator/tests/unit/test_project_intake_scaffold.py \
  src/orchestrator/tests/unit/test_project_intake_util.py \
  src/orchestrator/tests/unit/test_project_intake_revise.py \
  src/orchestrator/tests/unit/test_project_plan_lock.py \
  src/orchestrator/tests/unit/test_project_validate.py \
  src/orchestrator/tests/unit/test_project_status.py \
  src/orchestrator/tests/unit/test_project_stop.py \
  src/orchestrator/tests/unit/test_stage1_golden_flow.py \
  src/orchestrator/tests/unit/test_stage1_runbook_consistency.py -q
```

## Scope

- Intake scaffold artifacts under `<session>/intake/`
- `doc_review.json` validation + revise loop
- Plan-lock readiness and enforcement
- Validate preflight with required plan lock

## Fast triage commands

From repo root:

```bash
uv run sde project status --session-dir "<session_dir>"
uv run sde project validate --session-dir "<session_dir>" --skip-workspace --require-plan-lock
uv run sde project validate --session-dir "<session_dir>" --skip-workspace --require-plan-lock --require-non-stub-reviewer
uv run sde project plan-lock --session-dir "<session_dir>" --check-only
uv run sde project plan-lock --session-dir "<session_dir>" --check-only --require-non-stub-reviewer
uv run sde project run --session-dir "<session_dir>" --enforce-plan-lock --require-non-stub-reviewer --mode guarded_pipeline
uv run sde continuous --project-session-dir "<session_dir>" --repo-root "<repo_root>" --enforce-plan-lock --require-non-stub-reviewer
```

Interpret quickly:

- `project validate` exit `0`: lock-ready preflight passed
- `project validate` exit `2`: invalid plan/intake/lock readiness failed
- `project run --enforce-plan-lock` (and `continuous` project mode with `--enforce-plan-lock`) exit `1` with `blocked_human`: lock gate blocked execution; with `--require-non-stub-reviewer` or `SDE_REQUIRE_NON_STUB_REVIEWER`, stub reviewer attestation fails lock readiness the same way as on `plan-lock` / `validate`
- `project plan-lock --require-non-stub-reviewer` exit `1` with reason `reviewer_identity_attestation_stub_disallowed`: local stub reviewer proof is rejected

## Failure mode matrix

- `invalid_doc_review_json`
  - Trigger: `intake/doc_review.json` has bad schema (`passed` not bool or bad `findings` type)
  - Detect: `sde project validate ... --require-plan-lock`
  - Fix: rewrite `doc_review.json` to valid shape, then re-run validate

- `plan_lock_not_ready`
  - Trigger: one or more Stage 1 prerequisites missing (digest/workbook/revise_state/contract step/rollback hints/etc.)
  - Detect: `sde project plan-lock --check-only`
  - Fix: satisfy reasons list, then write lock again

- `blocked_human` from revise loop
  - Trigger: repeated failed `doc_review` reached retry cap in `intake/revise_state.json`
  - Detect: `intake/revise_state.json` has `status: blocked_human`
  - Fix: provide corrected reviewer output (`passed: true` + findings shape), then apply revise again

- deterministic auto-regeneration applied
  - Trigger: `doc_review.passed == false` and `intake-revise` runs
  - Detect: `intake/revise_autogen.json` exists and `research_digest.md` / `question_workbook.jsonl` include `auto-revise-*` entries
  - Fix: if not present, rerun `intake-revise`; if still absent, treat as intake tooling failure and escalate

- `plan_lock_gate_failed` during project run
  - Trigger: `--enforce-plan-lock` enabled and readiness false
  - Detect: `stop_report.json` and run output detail `plan_lock_not_ready`
  - Fix: run `plan-lock --check-only`, resolve reasons, then retry run

## Required files and expected fields

- `intake/discovery.json`
  - must include non-empty `goal_excerpt`
- `intake/research_digest.md`
  - non-empty markdown content
- `intake/question_workbook.jsonl`
  - at least one JSON object row
- `intake/doc_review.json`
  - `passed: <bool>`
  - `findings: <list|dict>`
  - `reviewer: <non-empty string>`
  - `reviewed_at: <valid ISO timestamp>`
- `intake/planner_identity.json`
  - `actor_id: <non-empty string>`
- `intake/reviewer_identity.json`
  - `actor_id: <non-empty string>`
  - `role: reviewer`
  - `attestation_type: one of [local_stub, agent_signature, service_token]`
  - `attestation: <non-empty string>`
  - `reviewed_at: <non-empty string>`
  - `reviewed_at` must be a valid ISO timestamp and be within 300s of `doc_review.reviewed_at`
  - `doc_review.reviewer` must equal reviewer `actor_id`
  - reviewer `actor_id` must not equal planner `actor_id`
- `intake/revise_state.json` (when required)
  - `status: review_passed`
- `project_plan.json`
  - valid schema
  - each step has non-empty `rollback_hint`
  - at least one step with `contract_step: true`

## Recovery playbook (ordered)

1. Run `status` and `validate --require-plan-lock` to capture current state.
2. If `doc_review` invalid, fix schema first.
3. Apply revise loop:
   - `uv run sde project intake-revise --session-dir "<session_dir>" --max-retries 2`
4. Check lock readiness:
   - `uv run sde project plan-lock --session-dir "<session_dir>" --check-only`
5. Write lock artifact:
   - `uv run sde project plan-lock --session-dir "<session_dir>"`
6. Re-run preflight:
   - `uv run sde project validate --session-dir "<session_dir>" --skip-workspace --require-plan-lock`
7. Resume execution:
   - `uv run sde project run --session-dir "<session_dir>" --enforce-plan-lock --mode guarded_pipeline`
   - For CI parity with strict reviewer policy: add `--require-non-stub-reviewer` or set `SDE_REQUIRE_NON_STUB_REVIEWER` (same semantics as validate/plan-lock)

## Stage 1 progress signals (quick JSON checklist)

Use these commands:

```bash
uv run sde project status --session-dir "<session_dir>"
uv run sde project plan-lock --session-dir "<session_dir>" --check-only
uv run sde project validate --session-dir "<session_dir>" --skip-workspace --require-plan-lock
```

Reviewer proof locations:

- `sde project plan-lock --check-only ...` JSON includes `reviewer_proof_summary`
- `<session_dir>/project_plan_lock.json` includes `reviewer_proof_summary` when lock is written
- `sde project status --session-dir ...` `status_at_a_glance.reviewer_*` fields prefer `plan_lock.reviewer_proof_summary` when present (fallback: live `reviewer_proof` from intake files)
- `status_at_a_glance.reviewer_signal_source` reports `plan_lock` vs `intake`

Healthy indicators:

- `status_at_a_glance.plan_lock_ready == true`
- `status_at_a_glance.plan_lock_locked == true`
- `status_at_a_glance.intake_merge_anchor_present == true`
- `status_at_a_glance.reviewer_attestation_type_allowed == true`
- `status_at_a_glance.reviewer_attestation_policy_ok == true` (when strict reviewer policy is active)
- `status_at_a_glance.reviewer_matches_doc_review == true`
- `status_at_a_glance.reviewer_differs_from_planner == true`
- `status_at_a_glance.reviewed_at_skew_ok == true`
- `status_at_a_glance.red_flags` does not include:
  - `intake_doc_review_invalid`
  - `plan_lock_not_ready`
  - `plan_lock_not_locked`
- `project validate` returns `exit_code: 0`

Blocked indicators:

- `status_at_a_glance.plan_lock_ready == false`
- `status_at_a_glance.plan_lock_locked == false`
- `status_at_a_glance.red_flags` includes one or more of:
  - `plan_lock_not_ready`
  - `plan_lock_not_locked`
  - `reviewer_attestation_type_invalid`
  - `reviewer_attestation_policy_failed`
  - `reviewer_identity_doc_review_mismatch`
  - `reviewer_identity_matches_planner`
  - `reviewed_at_skew_exceeded`
- `project validate` returns `error: "plan_lock_not_ready"` with `details` reasons
- `project run --enforce-plan-lock` stops with `stopped_reason: "blocked_human"` and detail `plan_lock_not_ready`

Useful files to inspect directly:

- `<session_dir>/project_plan_lock.json`
- `<session_dir>/intake/doc_review.json`
- `<session_dir>/intake/revise_state.json`
- `<session_dir>/stop_report.json` (after blocked runs)

## Escalation

Escalate when any condition persists after one correction loop:

- lock reasons remain unchanged after fixes
- revise state stays `blocked_human` with corrected `doc_review.json`
- validate fails with unreadable/malformed plan artifacts

Attach in escalation:

- `project_plan.json`
- `intake/doc_review.json`
- `intake/revise_state.json` (if present)
- `project_plan_lock.json` (if present)
- `stop_report.json` (if present)
