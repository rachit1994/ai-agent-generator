# Strategy overlay

## Context
- [x] Verified feature scope and baseline (`24%`) in `docs/master-architecture-feature-completion.md`.
- [x] Verified canonical strategy proposal contract in `strategy_overlay_contract.py`.
- [x] Verified producer integration in `organization_layer.py` and HS32 consumer in `hard_stops_organization.py`.

## Assumptions and Constraints
- [x] Scope is repo-local strategy proposal contract quality and HS32 consistency with contract validation.
- [x] HS32 must evaluate against full contract semantics, not partial truthiness checks.
- [x] Proposal references should be constrained to sane local artifact-like paths.

## Phase 0 — Preconditions
- [x] Confirmed existing tests covered happy path plus a subset of failure branches.
- [x] Confirmed contract previously accepted any non-empty schema version value.
- [x] Confirmed HS32 previously bypassed full contract checks and could pass malformed proposals.

## Phase 1 — Contracts and Interfaces
- [x] Added explicit schema version constant (`STRATEGY_OVERLAY_SCHEMA_VERSION = "1.0"`).
- [x] Added strict schema version value validation.
- [x] Added proposal ref format validation (relative path, no traversal, `.json` suffix).
- [x] Preserved camel/snake alias compatibility for contract ingestion.

## Phase 2 — Core Implementation
- [x] Hardened `validate_strategy_proposal_dict` with schema value + ref format checks.
- [x] Updated HS32 (`_hs32_strategy_self_approval`) to use full `validate_strategy_proposal_dict` validation.
- [x] Retained existing producer behavior in `write_organization_artifacts` while enforcing stricter contract.

## Phase 3 — Safety and Failure Handling
- [x] Added negative tests for invalid schema version value.
- [x] Added negative tests for bad `proposal_ref` format.
- [x] Added HS32 fail-closed test for invalid strategy proposal schema in organization hard-stop evaluation.
- [x] Preserved and updated existing HS32 requirement test to match new contract-required fields.

## Phase 4 — Verification and Observability
- [x] Expanded strategy contract tests in `test_strategy_overlay_contract.py`.
- [x] Expanded HS32 evaluation tests in `test_evolution_organization_hard_stops.py`.
- [x] Executed focused verification:
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_strategy_overlay_contract.py`
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_evolution_organization_hard_stops.py`
  - [x] Result: `22 passed`.

## Definition of Done
- [x] Strategy overlay proposal contract enforces explicit schema version and ref format constraints.
- [x] HS32 now evaluates strategy proposal validity using the same canonical contract.
- [x] Strategy overlay and HS32 tests cover happy, negative, alias, and fail-closed branches.
- [x] Feature checklist is complete for repo-local scope.

## Test Cases
### Unit
- [x] `test_validate_strategy_proposal_dict_harness_ok`.
- [x] `test_validate_strategy_proposal_dict_requires_schema_version_value`.
- [x] `test_validate_strategy_proposal_dict_no_ref_needed_when_not_required`.
- [x] `test_validate_strategy_proposal_dict_accepts_camel_aliases`.
- [x] `test_validate_strategy_proposal_dict_rejects_bad_proposal_ref_format`.
- [x] Existing path tests (`missing`, `bad_json`) remain green.

### Integration
- [x] `test_write_organization_artifacts_writes_valid_proposal`.
- [x] `test_hs32_requires_promotion_package_and_proposal_ref` with contract-complete payload.

### Negative
- [x] `test_validate_strategy_proposal_dict_not_object`.
- [x] `test_validate_strategy_proposal_dict_autonomy_without_promotion`.
- [x] `test_validate_strategy_proposal_dict_missing_ref_when_required`.
- [x] `test_hs32_fails_when_strategy_proposal_schema_invalid`.

### Regression
- [x] Existing HS29/HS30/HS31 and related organization hard-stop paths remain green.
- [x] Strategy contract ID + producer integration behavior remains stable.

## Out of Scope
- [x] Full portfolio/runtime strategy control-plane implementation.
- [x] Cross-repository rollout orchestration and enterprise strategy governance services.
