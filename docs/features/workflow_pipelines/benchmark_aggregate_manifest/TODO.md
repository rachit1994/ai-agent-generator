# Benchmark aggregate manifest

## Context
- [x] Verified feature scope and baseline (`56%`) in `docs/master-architecture-feature-completion.md`.
- [x] Verified canonical benchmark manifest contract in `benchmark_manifest_contract.py`.
- [x] Verified producer + resume path integration in `run_benchmark.py`.

## Assumptions and Constraints
- [x] Scope is repo-local benchmark-manifest contract quality for resume/validate/replay correctness.
- [x] Contract should fail closed on unknown keys and duplicate task IDs.
- [x] Task prompt fields should be non-empty to preserve deterministic benchmark semantics.

## Phase 0 — Preconditions
- [x] Confirmed existing tests covered core happy path and several negatives.
- [x] Confirmed manifest previously accepted unknown top-level keys.
- [x] Confirmed duplicate task IDs and blank prompts were not rejected.

## Phase 1 — Contracts and Interfaces
- [x] Added explicit allowed key set enforcement.
- [x] Added duplicate task ID rejection across task list.
- [x] Tightened task prompt rule from “is string” to “non-empty string”.
- [x] Preserved contract IDs and existing required core fields (`schema`, `run_id`, `suite_path`, `mode`, `tasks`, `continue_on_error`).

## Phase 2 — Core Implementation
- [x] Hardened `validate_benchmark_manifest_dict` with unknown-key, duplicate-ID, and prompt-quality checks.
- [x] Preserved compatibility for producer paths in `run_benchmark.py`.
- [x] Kept resume-mode validation behavior stable while increasing fail-closed strictness.

## Phase 3 — Safety and Failure Handling
- [x] Added negative test for blank prompt.
- [x] Added negative test for duplicate task IDs.
- [x] Added negative test for unknown top-level key.
- [x] Added path-level negative tests for missing file, bad JSON, and non-object JSON.

## Phase 4 — Verification and Observability
- [x] Expanded benchmark manifest tests in `test_benchmark_manifest_contract.py`.
- [x] Re-ran benchmark-harvest integration checks in `test_benchmark_harvest.py`.
- [x] Re-ran validate-run API integration checks in `test_validate_run_api.py`.
- [x] Executed focused verification:
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_benchmark_manifest_contract.py`
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_benchmark_harvest.py`
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_validate_run_api.py`
  - [x] Result: `22 passed`.

## Definition of Done
- [x] Benchmark aggregate manifest contract rejects unknown keys, duplicate task IDs, and blank prompts.
- [x] Producer and resume/validate integrations remain green under stricter contract rules.
- [x] Unit and integration coverage includes newly hardened fail-closed branches.
- [x] Feature checklist is complete for repo-local scope.

## Test Cases
### Unit
- [x] `test_validate_benchmark_manifest_ok`.
- [x] `test_validate_benchmark_manifest_rejects_blank_prompt`.
- [x] `test_validate_benchmark_manifest_rejects_duplicate_task_ids`.
- [x] `test_validate_benchmark_manifest_rejects_unknown_keys`.
- [x] Existing schema/mode/continue-on-error negatives remain covered.

### Integration
- [x] `test_benchmark_harvest.py` suite remains green.
- [x] `test_validate_run_api.py` suite remains green with stricter manifest validation.

### Negative
- [x] `test_validate_benchmark_manifest_path_missing_bad_and_non_object`.
- [x] Existing bad-schema and bad-mode tests remain green.

### Regression
- [x] Contract ID remains stable (`sde.benchmark_manifest.v1`).
- [x] Existing benchmark-manifest producer payload shape remains valid.

## Out of Scope
- [x] Distributed control-plane benchmark orchestration across repos.
- [x] Enterprise benchmark governance automation beyond local contract enforcement.
