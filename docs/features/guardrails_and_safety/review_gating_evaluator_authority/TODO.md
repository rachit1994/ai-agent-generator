# Review gating + evaluator authority

## Context
- [x] Verified priority and completion target in `docs/master-architecture-feature-completion.md` (`Guardrails and safety` row marks this feature at 100%).
- [x] Verified implementation surface exists in `src/guardrails_and_safety/review_gating_evaluator_authority/review_gating/review.py`.
- [x] Verified runtime enforcement path exists in `src/guardrails_and_safety/review_gating_evaluator_authority/review_gating/run_directory.py`.

## Assumptions and Constraints
- [x] Scope is repo-local evaluator authority and review gating, not a distributed control-plane rollout.
- [x] Validation is file-backed (`review.json`, `summary.json`, `token_context.json`, `traces.jsonl`) and must fail closed on malformed input.
- [x] `completed_review_pass` is valid only when evaluator eligibility checks pass with zero blocker findings.

## Phase 0 — Preconditions
- [x] Confirmed review schema constants are present in `src/guardrails_and_safety/risk_budgets_permission_matrix/gates_constants/constants.py`.
- [x] Confirmed `REQUIRED_REVIEW_KEYS` and `REVIEW_SCHEMA` are imported and used by `validate_review_payload`.
- [x] Confirmed HS15 hook is connected in `src/guardrails_and_safety/risk_budgets_permission_matrix/risk_budgets/hard_stops_guarded.py`.

## Phase 1 — Contracts and Interfaces
- [x] Added strict status validation in `validate_review_payload` (`completed_review_pass|completed_review_fail|incomplete`).
- [x] Added type validation for `reasons` list in `validate_review_payload`.
- [x] Added type validation for `required_fixes` list in `validate_review_payload`.
- [x] Added non-empty string validation for `completed_at` in `validate_review_payload`.
- [x] Preserved existing finding-key and finding-severity contract validation.

## Phase 2 — Core Implementation
- [x] Added JSON-safe helper `_read_json_file` in `run_directory.py`.
- [x] Added malformed `summary.json` handling with explicit errors (`invalid_json:summary.json` and `json_not_object:summary.json`).
- [x] Added malformed `review.json` handling with explicit errors (`invalid_json:review.json` and `json_not_object:review.json`).
- [x] Added malformed `token_context.json` handling with explicit errors (`invalid_json:token_context.json` and `json_not_object:token_context.json`).
- [x] Added per-line `traces.jsonl` parsing guards with explicit errors (`invalid_jsonl:*` and `jsonl_not_object:*`).
- [x] Kept evaluator eligibility enforcement (`review_pass_not_evaluator_eligible`) intact in `validate_execution_run_directory`.

## Phase 3 — Safety and Failure Handling
- [x] Confirmed HS15 rejects pass status when blocker findings are present.
- [x] Added HS15 regression coverage for `definition_of_done.all_required_passed == False`.
- [x] Added HS15 regression coverage for `step_review == fail` event metadata.
- [x] Confirmed malformed review payloads are rejected before pass eligibility is accepted.

## Phase 4 — Verification and Observability
- [x] Added positive integration check that `build_review` output is evaluator-eligible for passing finalize flow.
- [x] Expanded negative test coverage for payload branch failures in `test_review_gating_negative.py`.
- [x] Expanded negative test coverage for malformed `review.json` in run-directory validation.
- [x] Re-ran focused suite:
  - [x] `uv run pytest src/guardrails_and_safety/review_gating_evaluator_authority/review_gating/tests/test_review_gating_positive.py`
  - [x] `uv run pytest src/guardrails_and_safety/review_gating_evaluator_authority/review_gating/tests/test_review_gating_negative.py`
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_review_gating_findings.py`
  - [x] Result: `26 passed`.

## Definition of Done
- [x] Review payload contract is strict enough to reject malformed status/finding structures for evaluator authority.
- [x] Run-directory validation fails closed on malformed JSON/JSONL for core review-gating artifacts.
- [x] HS15 blocker-pass prevention is enforced and covered by regression tests.
- [x] Positive and negative evaluator-authority tests are green in the focused suite.
- [x] Feature remains aligned with 100% repo-local completion target in `docs/master-architecture-feature-completion.md`.

## Test Cases
### Unit
- [x] `validate_review_payload` accepts valid payload (`test_validate_review_payload_accepts_valid_payload`).
- [x] `validate_review_payload` rejects invalid status (`test_validate_review_payload_rejects_invalid_status`).
- [x] `validate_review_payload` rejects non-list findings (`test_validate_review_payload_rejects_non_list_findings`).
- [x] `validate_review_payload` rejects non-object finding (`test_validate_review_payload_rejects_non_object_finding`).
- [x] `validate_review_payload` rejects missing finding key (`test_validate_review_payload_rejects_missing_finding_key`).
- [x] `is_evaluator_pass_eligible` rejects blocker/status/non-list/non-object branches.

### Integration
- [x] `build_review` -> evaluator eligibility happy path validated (`test_build_review_output_is_evaluator_eligible_when_finalize_passes`).
- [x] `validate_execution_run_directory` path validates eligible review without evaluator-eligibility errors.
- [x] `validate_execution_run_directory` flags malformed `review.json` as structured error.

### Negative
- [x] HS15 rejects `completed_review_pass` with blocker findings.
- [x] HS15 rejects `completed_review_pass` when DoD required checks are not all passed.
- [x] HS15 rejects run when step-review failure metadata appears in events.

### Regression
- [x] Existing findings-generation tests still pass (`test_review_findings_include_static_gate_blockers`, `test_build_review_adds_verifier_blocker_when_checks_fail`).
- [x] Run-directory evaluator authority still flags `review_pass_not_evaluator_eligible` for blocker findings.
- [x] Focused suite remains green after hardening (`26 passed`).

## Out of Scope
- [x] Multi-tenant policy service and centralized IAM-plane implementation.
- [x] Organization-wide committee workflows outside local run-directory contract enforcement.
