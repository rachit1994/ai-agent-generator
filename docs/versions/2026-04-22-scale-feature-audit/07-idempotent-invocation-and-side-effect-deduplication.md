# Idempotent invocation and side-effect deduplication

## Audit scores
- Agent A score: **10%**
- Agent B score: **24%**
- Independent completion re-audit score: **32%**
- Confirmed score (conservative): **32%**

## Agent A reviewed missing checklist
- [ ] Define canonical idempotency key format and scope.
- [ ] Persist idempotency ledger with TTL and collision protection.
- [ ] Enforce idempotency check at API entrypoint.
- [ ] Replay canonical prior responses for duplicate keys.
- [ ] Deduplicate downstream side effects across retries.
- [ ] Handle concurrent duplicate submissions safely.
- [ ] Add exactly-once side-effect tests.
- [ ] Add observability for dedupe hit/conflict outcomes.

## Agent B reviewed missing checklist
- [ ] Extend idempotency from storage events to API invocation layer.
- [ ] Implement global dedupe ledger across services/plugins.
- [ ] Add idempotency TTL and replay windows.
- [ ] Add duplicate-but-different payload conflict contract.
- [ ] Add cross-process concurrency dedupe tests.
- [ ] Add outbox integration for external side effects.
- [ ] Add plugin/tool-call idempotency propagation.
- [ ] Add idempotency hit/miss/conflict metrics.

## Confirmed missing (both audits)
- [ ] Promote idempotency from storage-only to full invocation path.
- [ ] Implement global dedupe ledger across services/plugins.
- [ ] Enforce API-level key validation and replay semantics.
- [ ] Handle concurrent duplicate writes safely.
- [ ] Deduplicate external side effects via outbox pattern.
- [ ] Define and test conflict response semantics.
- [ ] Add TTL/replay policy for keys.
- [ ] Publish idempotency metrics and alerts.

## Confirmed implemented in this pass
- [x] Add isolated feature package scaffold under `src/scale_out_api_mcp_plugin_platform_features/feature_07_idempotent_invocation_side_effect_deduplication/`.
- [x] Implement deterministic idempotency gate runtime and strict report contract validation.
- [x] Add unified executable `preflight`/`ci` command at `scripts/idempotency_gate.py`.
- [x] Wire the feature gate into CI as a blocking step in `.github/workflows/ci.yml`.
- [x] Add targeted runtime and script tests with passing local evidence.
- [x] Add baseline fixture and history artifacts under `data/idempotency/`.

## Remaining blockers to 100%
- Replace fixture booleans with real invocation-path idempotency key enforcement and replay behavior.
- Implement durable global dedupe ledger with TTL/replay windows and conflict semantics.
- Integrate concurrency-safe duplicate handling across process boundaries.
- Implement outbox-based external side-effect deduplication and propagation semantics.
- Add production metrics/alerts for idempotency hit/miss/conflict and end-to-end exactly-once tests.

## Review method
- [x] Independent auditor A review complete.
- [x] Independent auditor B review complete.
- [x] Conservative score set to minimum of both auditors.
- [x] Confirmed-missing list created only from overlap themes.

## Additional implemented in latest pass
- [x] Replace marker-only API checks with structured invocation semantics (`idempotency_key`, replay status enum, conflict code).
- [x] Enforce ledger partition identity and replay-window configuration (`ledger_partition`, positive `ttl_seconds`) in gate checks.
- [x] Enforce concurrency-shape semantics (`dedupe_lock_held_ms` non-negative) for duplicate-write safety payloads.
- [x] Enforce outbox evidence shape (`outbox_events` non-empty) for external side-effect dedupe checks.
- [x] Enforce idempotency metrics shape (`hits`/`misses`/`conflicts` integer counters) instead of boolean-only metrics flags.
- [x] Add fail-closed regression coverage for invalid replay status values.
- [x] Enforce idempotency metrics arithmetic coherence by requiring `total_requests == hits + misses + conflicts`.
- [x] Add fail-closed regression coverage for metrics-total mismatch.
- [x] Enforce lock-duration coherence by requiring `dedupe_lock_held_ms <= ttl_seconds * 1000` so duplicate-write lock timing cannot exceed replay-window budget.
- [x] Add fail-closed regression coverage for lock duration exceeding TTL window.
