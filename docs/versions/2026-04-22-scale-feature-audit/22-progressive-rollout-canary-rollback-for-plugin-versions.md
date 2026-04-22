# Progressive rollout/canary/rollback for plugin versions

## Audit scores
- Agent A score: **7%**
- Agent B score: **8%**
- Independent completion re-audit score: **36%**
- Confirmed score (conservative): **36%**

## Agent A reviewed missing checklist
- [ ] Implement plugin version traffic-splitting controller.
- [ ] Implement staged rollout policy.
- [ ] Define health gates for promotion.
- [ ] Implement auto rollback on SLO breach.
- [ ] Track rollout state/history per plugin.
- [ ] Support safe pause/resume controls.
- [ ] Add canary failure integration tests.
- [ ] Add operator override APIs.

## Agent B reviewed missing checklist
- [ ] Implement plugin version routing by traffic percentage.
- [ ] Implement canary cohort assignment.
- [ ] Implement health gate checks tied to plugin versions.
- [ ] Implement automatic rollback trigger on SLO breach.
- [ ] Implement staged rollout progression controller.
- [ ] Persist rollout history for auditability.
- [ ] Add upgrade/canary/rollback lifecycle tests.
- [ ] Add operator pause/resume/force-rollback controls.

## Confirmed missing (both audits)
- [ ] Build plugin version progressive rollout controller.
- [ ] Support canary cohorts and staged traffic percentages.
- [ ] Enforce health-gated promotion logic.
- [ ] Auto-rollback on SLO or policy breach.
- [ ] Persist rollout timeline for auditability.
- [ ] Provide pause/resume/override operations.
- [ ] Test full canary and rollback lifecycle.
- [ ] Integrate rollout actions with observability signals.

## Confirmed implemented in this pass
- [x] Add isolated feature package scaffold under `src/scale_out_api_mcp_plugin_platform_features/feature_22_plugin_progressive_rollout_canary_rollback/`.
- [x] Implement deterministic rollout gate runtime and strict report contract validation.
- [x] Add unified executable `preflight`/`ci` command at `scripts/plugin_rollout_gate.py`.
- [x] Wire the feature gate into CI as a blocking step in `.github/workflows/ci.yml`.
- [x] Add targeted runtime and script tests with passing local evidence.
- [x] Add baseline fixture and history artifacts under `data/plugin_rollout/`.

## Remaining blockers to 100%
- Replace fixture booleans with runtime-integrated progressive traffic-splitting and canary cohort assignment logic.
- Implement executable health-gated promotion decisions and automatic rollback state transitions on SLO/policy breach.
- Add real operator control APIs/commands for pause/resume/force-rollback with audit-grade event history.
- Expand rollout timeline persistence to include version transitions, actor actions, and timestamped lifecycle events.
- Add end-to-end lifecycle integration tests (upgrade->canary->promote/rollback) tied to real observability signals.

## Review method
- [x] Independent auditor A review complete.
- [x] Independent auditor B review complete.
- [x] Conservative score set to minimum of both auditors.
- [x] Confirmed-missing list created only from overlap themes.

## Additional implemented in latest pass
- [x] Replace boolean-only rollout checks with structured controller invariants (`active_plugin_version`, staged cohort traffic definitions summing to 100%).
- [x] Require concrete health signal payloads (`error_rate_pct`, `latency_p95_ms`, `rollback_triggered`) for gate semantics instead of marker flags.
- [x] Require observability linkage evidence (`observability_signal_ids`) for rollout-to-signal integration checks.
- [x] Add structured timeline event validation (`type`, `timestamp`, `actor`) for persisted rollout audit records.
- [x] Enforce operator control metadata (`override_actions_count`) and lifecycle-test identity (`lifecycle_test_run_id`) in runtime gate checks.
- [x] Add fail-closed regression coverage for invalid stage traffic totals.
- [x] Enforce rollback timeline coherence by requiring a persisted `rollback` event whenever `rollback_triggered` is true.
- [x] Add fail-closed regression coverage for rollback-triggered states without rollback timeline evidence.
