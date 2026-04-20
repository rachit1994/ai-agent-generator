# Topology And Repository Layout

## Context
- [x] Confirmed scope and baseline (`24%`) from `docs/master-architecture-feature-completion.md`.
- [x] Audited repository topology indexing in `orchestrator/api/repo_index.py`.
- [x] Identified fail-closed gap: malformed `path_scopes` entries and invalid `max_files` values were not explicitly rejected, risking inconsistent index behavior.

## Assumptions and Constraints
- [x] Repo index generation is a topology contract for context packs and should be deterministic under malformed inputs.
- [x] Contract failures should return an empty index artifact rather than best-effort partial matching.
- [x] Valid existing behavior must remain unchanged for clean inputs.

## Phase 0 — Preconditions
- [x] Verified `build_repo_index` accepted raw scopes without normalization.
- [x] Verified invalid `max_files` values were not fail-closed at function ingress.
- [x] Verified missing direct unit coverage for repo-index malformed input behavior.

## Phase 1 — Contracts and Interfaces
- [x] Added scope normalization and malformed detection contract (`_normalized_scopes`).
- [x] Added canonical empty artifact constructor (`_empty_index`) for fail-closed outcomes.
- [x] Enforced strict ingress checks:
  - [x] malformed scopes -> empty index
  - [x] non-int/bool/`<1` `max_files` -> empty index

## Phase 2 — Core Implementation
- [x] Updated `build_repo_index` to normalize scopes and reject malformed scope input.
- [x] Updated `build_repo_index` to reject invalid `max_files`.
- [x] Preserved path matching behavior for valid scopes and positive integer caps.

## Phase 3 — Safety and Failure Handling
- [x] Added unit test for malformed scope list (blank scope entry) with fail-closed empty index.
- [x] Added unit test for invalid `max_files` values (`True`, `0`) with fail-closed empty index.
- [x] Confirmed no regression in `context_pack` behavior.

## Phase 4 — Verification and Observability
- [x] Added new unit suite: `test_repo_index.py`.
- [x] Ran focused suites:
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_repo_index.py`
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_context_pack.py`
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_public_export_surface.py`
  - [x] Result: `214 passed`.

## Definition of Done
- [x] Repo topology index now fail-closes on malformed input contracts.
- [x] New tests pin fail-closed behavior for scopes and size limits.
- [x] Related context-pack and public-surface regressions are green.

## Test Cases
### Unit
- [x] Valid scope indexing remains accepted.
- [x] Malformed scope set yields empty index.
- [x] Invalid `max_files` type/value yields empty index.

### Integration
- [x] Context pack generation remains functional with repo index integration.
- [x] Public export surface remains stable.

### Negative
- [x] Blank/malformed scope entries no longer produce ambiguous partial indexing.
- [x] Bool/non-positive file caps no longer produce uncertain capped behavior.

### Regression
- [x] `test_context_pack` suite remains green.
- [x] `test_public_export_surface` suite remains green.

## Out of Scope
- [x] Semantic or language-aware topology indexing.
- [x] Cross-repository topology federation beyond local repo index artifacting.
