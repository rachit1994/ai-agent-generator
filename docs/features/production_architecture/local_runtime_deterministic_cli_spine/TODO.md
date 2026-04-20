# Local runtime deterministic cli spine

## Context
- [x] Verified feature scope and baseline (`68%`) in `docs/master-architecture-feature-completion.md`.
- [x] Verified deterministic local validation entrypoint in `orchestrator/api/validate_run.py`.
- [x] Verified benchmark and single-task run directory validation paths converge through API-level mode resolution.

## Assumptions and Constraints
- [x] Scope is local run-directory validation determinism and fail-closed artifact checks.
- [x] API should use canonical benchmark artifact contracts rather than ad-hoc partial field checks.
- [x] Existing compatibility tokens for missing/invalid JSON should remain stable where already consumed.

## Phase 0 — Preconditions
- [x] Confirmed benchmark validation path previously used lightweight ad-hoc checks.
- [x] Confirmed benchmark manifest/checkpoint/summary had stronger canonical validators available.
- [x] Confirmed benchmark summary fixture in API tests lacked the newer schema/shape fields enforced elsewhere.

## Phase 1 — Contracts and Interfaces
- [x] Switched benchmark-manifest validation path to canonical `validate_benchmark_manifest_path`.
- [x] Switched benchmark-checkpoint validation path to canonical `validate_benchmark_checkpoint_path`.
- [x] Switched benchmark-summary validation path to canonical `validate_benchmark_aggregate_summary_path`.
- [x] Preserved legacy API-level missing/bad-json tokens while surfacing contract violations via namespaced tokens.

## Phase 2 — Core Implementation
- [x] Replaced ad-hoc benchmark artifact validators in `validate_run.py` with canonical contract adapters.
- [x] Added deterministic mapping:
  - [x] file missing / bad JSON -> legacy API error tokens
  - [x] all other contract failures -> `benchmark_*_contract:<token>`
- [x] Updated benchmark aggregate success test fixture to contract-compliant summary payload (`schema`, `suitePath`, `perTaskDeltas`).

## Phase 3 — Safety and Failure Handling
- [x] Enforced fail-closed benchmark artifact checks via canonical contract validators.
- [x] Ensured benchmark manifest/checkpoint/summary drift now surfaces as explicit contract-token errors.
- [x] Preserved benchmark-only path behavior (`run_kind=benchmark_aggregate`, no execution gates).

## Phase 4 — Verification and Observability
- [x] Re-ran API validation suite in `test_validate_run_api.py`.
- [x] Re-ran benchmark manifest contract suite in `test_benchmark_manifest_contract.py`.
- [x] Re-ran benchmark checkpoint contract suite in `test_benchmark_checkpoint_contract.py`.
- [x] Re-ran benchmark aggregate summary contract suite in `test_benchmark_aggregate_summary_contract.py`.
- [x] Executed focused verification:
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_validate_run_api.py`
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_benchmark_manifest_contract.py`
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_benchmark_checkpoint_contract.py`
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_benchmark_aggregate_summary_contract.py`
  - [x] Result: `35 passed`.

## Definition of Done
- [x] Local runtime validation API now relies on canonical benchmark contracts for manifest/checkpoint/summary.
- [x] Contract drift in benchmark artifacts is surfaced with explicit namespaced tokens.
- [x] API and benchmark contract suites pass with updated deterministic validation behavior.
- [x] Feature checklist is complete for repo-local scope.

## Test Cases
### Unit
- [x] `test_validate_run_missing_directory`.
- [x] `test_validate_run_invalid_mode_from_manifest`.
- [x] `test_validate_run_benchmark_mode_both_requires_override`.

### Integration
- [x] `test_validate_run_reads_mode_from_manifest`.
- [x] `test_validate_run_reads_mode_from_benchmark_manifest`.
- [x] `test_validate_run_single_task_prefers_run_manifest_over_benchmark`.
- [x] `test_validate_run_benchmark_aggregate_ok` (updated summary fixture to canonical contract shape).

### Negative
- [x] Missing/invalid benchmark artifact files still return stable API tokens.
- [x] Non-trivial benchmark artifact violations surface as namespaced contract errors.

### Regression
- [x] Benchmark aggregate and single-task routing semantics remain unchanged.
- [x] Existing contract suites remain green under API-level contract delegation.

## Out of Scope
- [x] Distributed runtime orchestration or remote control-plane scheduling.
- [x] Non-local deployment/runtime guarantees beyond deterministic local validation.
