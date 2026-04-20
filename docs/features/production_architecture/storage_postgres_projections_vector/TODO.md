# Storage Postgres Projections Vector

## Context
- [x] Confirmed feature scope against `docs/master-architecture-feature-completion.md` (`0%` baseline, local file-backed storage only).
- [x] Audited active storage implementation in `src/production_architecture/storage/storage/storage.py`.
- [x] Identified closure slice: deterministic and test-covered local persistence primitives.

## Assumptions and Constraints
- [x] Scope remains local JSON/JSONL storage primitives (no real Postgres/vector engine in this repo).
- [x] Determinism of persisted artifact bytes is useful for reproducible local runs and review diffs.
- [x] Existing call sites rely on current API shape (`ensure_dir`, `write_json`, `append_jsonl`, `read_json`, `read_jsonl`).

## Phase 0 — Preconditions
- [x] Verified no dedicated storage utility unit tests existed.
- [x] Verified storage module was migration-critical export surface (validated via public export tests).
- [x] Verified behavior before change used unsorted JSON key output.

## Phase 1 — Contracts and Interfaces
- [x] Introduced internal deterministic serialization helper `_stable_json_dumps`.
- [x] Contracted `write_json` to emit stable pretty JSON (`indent=2`, `sort_keys=True`).
- [x] Contracted `append_jsonl` to emit stable compact JSONL rows (`sort_keys=True`).
- [x] Preserved read-path behavior and public function signatures.

## Phase 2 — Core Implementation
- [x] Updated `write_json` to use stable serialization.
- [x] Updated `append_jsonl` to use stable serialization.
- [x] Added storage utility unit tests in `test_storage_utils.py`.

## Phase 3 — Safety and Failure Handling
- [x] Added negative test proving malformed JSONL line still fails closed via `JSONDecodeError`.
- [x] Added coverage for missing-file behavior (`read_jsonl` returns empty list).
- [x] Added coverage that parent directories are created automatically before writes.

## Phase 4 — Verification and Observability
- [x] Ran targeted storage utility tests:
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_storage_utils.py`
- [x] Ran migration/export regression surface:
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_public_export_surface.py`
- [x] Result: `209 passed`.

## Definition of Done
- [x] Storage writes are deterministic for JSON and JSONL outputs.
- [x] Storage utility behavior is covered by focused unit tests.
- [x] Export/public-surface regression suite remains green after storage changes.

## Test Cases
### Unit
- [x] `test_write_json_is_stable_and_creates_parent_dirs`.
- [x] `test_append_jsonl_uses_stable_key_order_and_roundtrips`.
- [x] `test_read_jsonl_returns_empty_for_missing_file`.
- [x] `test_read_jsonl_raises_for_invalid_line`.

### Integration
- [x] `test_public_export_surface.py` remains green with storage API unchanged.

### Negative
- [x] Malformed JSONL still raises `JSONDecodeError` (fail-closed parse behavior).

### Regression
- [x] Public storage module exports still import and resolve correctly through migration surface tests.

## Out of Scope
- [x] Real Postgres-backed storage, projection services, or vector database integration.
- [x] Distributed durability semantics beyond local filesystem artifact persistence.
