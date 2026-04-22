# Local/prod config overlay with invariant semantics

## Audit scores
- Agent A score: **11%**
- Agent B score: **14%**
- Confirmed score (conservative): **11%**

## Independent completion re-audit (2026-04-22)
- Independent reviewer score: **34%**
- Updated conservative score for current repo state: **34%**

## Agent A reviewed missing checklist
- [ ] Create unified config schema for local and prod.
- [ ] Implement startup fail-fast validation for adapters.
- [ ] Mark invariant fields and enforce semantics.
- [ ] Implement deterministic overlay precedence.
- [ ] Add config drift detector.
- [ ] Add redaction and secret-source validation.
- [ ] Add backward-compatible config migration tooling.
- [ ] Add integration tests for overlay behavior.

## Agent B reviewed missing checklist
- [ ] Implement shared config schema consumed by both runtimes.
- [ ] Implement overlay merge logic.
- [ ] Declare invariant fields across overlays.
- [ ] Fail startup on invariant violations.
- [ ] Add env-specific override allowlist.
- [ ] Add secret handling rules.
- [ ] Add CI tests comparing local/prod config resolutions.
- [ ] Add versioned config migration tooling.

## Confirmed missing (both audits)
- [ ] Introduce one schema for local/prod config.
- [ ] Implement deterministic overlay merge engine.
- [ ] Enforce invariants with startup fail-fast checks.
- [ ] Detect and report config drift.
- [ ] Constrain environment overrides safely.
- [ ] Handle secrets/redaction consistently.
- [ ] Support versioned config migrations.
- [ ] Test config overlays across all runtime adapters.

## Remaining blockers to 100%
- [ ] Replace marker-based gate checks with executable config schema validation and deterministic overlay merge logic.
- [ ] Enforce invariant declarations at startup over concrete config keys/values and fail fast on violations.
- [ ] Implement real drift detection, override allowlist enforcement, and secret-source/redaction validation flows.
- [ ] Add versioned migration tooling and adapter-level integration tests exercising real local/prod config resolution behavior.

## Additional implemented in latest pass
- [x] Enforce shared-schema version coherence across base/overlay/resolved artifacts by requiring aligned non-empty `config_schema_version`.
- [x] Add fail-closed regression coverage for schema-version drift in overlay payloads.
- [x] Update runtime/script fixtures to include explicit schema-version evidence in all config artifacts.
- [x] Enforce deterministic precedence evidence in resolved artifacts by requiring exact `applied_precedence` ordering (`base -> env_overlay -> runtime_override_allowlist`).
- [x] Add fail-closed regression coverage for precedence ordering drift.
- [x] Enforce override allowlist evidence coherence by requiring aligned non-empty `override_allowlist_hash` across overlay/resolved artifacts.
- [x] Add fail-closed regression coverage for override allowlist hash drift.

## Review method
- [x] Independent auditor A review complete.
- [x] Independent auditor B review complete.
- [x] Conservative score set to minimum of both auditors.
- [x] Confirmed-missing list created only from overlap themes.
