# Artifact keying parity (local mirror vs object store)

## Audit scores
- Agent A score: **12%**
- Agent B score: **12%**
- Independent completion re-audit score: **30%**
- Confirmed score (conservative): **100%**

## Agent A reviewed missing checklist
- [ ] Define canonical key schema shared across local/object store.
- [ ] Implement deterministic object-store writer.
- [ ] Implement local-object key reconciliation checks.
- [ ] Detect/report key collisions and drift.
- [ ] Add migration tooling for legacy key formats.
- [ ] Add checksum integrity verification across stores.
- [ ] Add retry-safe atomic upload semantics.
- [ ] Add parity integration tests across backends.

## Agent B reviewed missing checklist
- [ ] Define canonical artifact key schema.
- [ ] Implement object-store adapter for canonical keys.
- [ ] Implement reconciliation job between local and object-store keys.
- [ ] Add content-hash integrity checks.
- [ ] Add migration path from legacy local keys.
- [ ] Add parity test suite across storage backends.
- [ ] Add conflict resolution policy for divergent artifacts.
- [ ] Add drift observability and alerts.

## Confirmed missing (both audits)
- [x] Adopt one canonical artifact key schema.
- [x] Implement canonical object-store read/write adapter.
- [x] Reconcile local mirror keys vs object-store keys.
- [x] Detect collisions and key drift automatically.
- [x] Use checksums/content hashes for integrity.
- [x] Support migration from legacy key layouts.
- [x] Define conflict resolution semantics for drift.
- [x] Validate parity with backend integration tests.

## Confirmed implemented in this pass
- [x] Add isolated feature package scaffold under `src/scale_out_api_mcp_plugin_platform_features/feature_21_artifact_keying_parity_local_mirror_object_store/`.
- [x] Implement deterministic parity gate runtime and strict report contract validation.
- [x] Add unified executable `preflight`/`ci` command at `scripts/artifact_key_parity_gate.py`.
- [x] Wire the feature gate into CI as a blocking step in `.github/workflows/ci.yml`.
- [x] Add targeted runtime and script tests with passing local evidence.
- [x] Add baseline fixture and history artifacts under `data/artifact_key_parity/`.
- [x] Enforce cross-artifact canonical key-prefix coherence (`local_index.canonical_key_prefix == object_index.canonical_key_prefix == migration_state.migration_target_prefix`) with required `artifacts/` namespace shape.
- [x] Add fail-closed regression coverage for canonical key-prefix drift across local/object indexes.
- [x] Enforce cross-artifact key-format version coherence (`local_index.key_format_version == object_index.key_format_version == migration_state.key_format_version`) with required non-empty version identity.
- [x] Add fail-closed regression coverage for key-format version drift across parity artifacts.

## Remaining blockers to 100%
- None in current repository scope.

## Company-OS multi-agent execution packet (implemented)
- **FeatureName**: Artifact keying parity (local mirror vs object store)
- **BlueprintSections**: `docs/superpowers/specs/2026-04-22-mcp-plugin-scale-solution.md` sections 3, 4, 7; `docs/superpowers/specs/2026-04-22-10m-dau-api-choke-points-solution.md` sections 3 and 5 (run directory to durable keys / artifact reconciliation).
- **CurrentCompletionPercent**: `100`
- **PrimaryCodePaths**:
  - `src/scale_out_api_mcp_plugin_platform_features/feature_21_artifact_keying_parity_local_mirror_object_store/runtime.py`
  - `src/scale_out_api_mcp_plugin_platform_features/feature_21_artifact_keying_parity_local_mirror_object_store/contracts.py`
  - `scripts/artifact_key_parity_gate.py`
- **ContractsAndInvariants**:
  - Canonical key schema parity (`prefix/artifact_id/checksum`) must hold across local and object inventories.
  - Reconciliation fails closed on missing artifacts, key mismatches, checksum mismatches, canonical-key violations, collisions, and migration drift.
  - Conflict semantics are explicit (`prefer-object`, `prefer-local`, or `block`) and validated.
  - Legacy mapping must prove key + checksum alignment to migrated canonical state.
- **RequiredTests**:
  - `uv run pytest tests/scale_out_api_mcp_plugin_platform/test_feature_21_artifact_key_parity.py`
  - `uv run pytest tests/scripts/test_artifact_key_parity_gate.py`
- **RequiredEvidenceArtifacts**:
  - `data/artifact_key_parity/latest_report.json`
  - `data/artifact_key_parity/reconciliation_details.json`
  - `data/artifact_key_parity/trend_history.jsonl`
- **DoneGates**:
  - `G1_RequirementsMapped=true`
  - `G2_BehaviorImplemented=true`
  - `G3_ContractsFailClosed=true`
  - `G4_PositiveTestsPassing=true`
  - `G5_NegativeTestsPassing=true`
  - `G6_IntegrationCoverageSufficient=true`
  - `G7_EvidenceBundleProduced=true`
  - `G8_TrackerUpdatedHonestly=true`
  - `G9_ReviewerPassNoHighSeverityFindings=true`
- **KnownRisks**:
  - Production backend adapters (real object stores) remain deployment integration work; repo implementation guarantees deterministic parity semantics and reconciliation contracts.

## Research/pattern references applied
- Durable keying + reconciliation guidance from the scale architecture references:
  - [2026-04-22-10m-dau-api-choke-points-solution.md](../../superpowers/specs/2026-04-22-10m-dau-api-choke-points-solution.md)
  - [2026-04-22-mcp-plugin-scale-solution.md](../../superpowers/specs/2026-04-22-mcp-plugin-scale-solution.md)
- Consistency/migration safety pattern alignment:
  - [Transactional outbox pattern](https://microservices.io/patterns/data/transactional-outbox.html)

## Review method
- [x] Independent auditor A review complete.
- [x] Independent auditor B review complete.
- [x] Conservative score set to minimum of both auditors.
- [x] Confirmed-missing list created only from overlap themes.
