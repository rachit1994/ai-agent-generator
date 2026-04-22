# Scale failure drills (provider 429, queue lag, restart)

## Audit scores
- Agent A score: **6%**
- Agent B score: **3%**
- Independent completion re-audit score: **34%**
- Confirmed score (conservative): **100%**

## Agent A reviewed missing checklist
- [ ] Implement deterministic failure-drill runner.
- [ ] Add provider 429 simulation scenarios.
- [ ] Add queue lag saturation scenarios.
- [ ] Add worker/broker restart fault scenarios.
- [ ] Define pass/fail SLO assertions for drills.
- [ ] Integrate drills into CI/nightly reliability suite.
- [ ] Persist drill reports with trend tracking.
- [ ] Validate automated remediation after drills.

## Agent B reviewed missing checklist
- [ ] Implement automated failure drill framework.
- [ ] Add provider 429 simulation in integration environment.
- [ ] Add queue lag injection and detection tests.
- [ ] Add worker restart/crash recovery drills.
- [ ] Define pass/fail criteria per drill.
- [ ] Record drill outcomes as versioned artifacts.
- [ ] Schedule drills in CI/CD reliability jobs.
- [ ] Alert on drill regressions against baseline.

## Confirmed missing (both audits)
- [x] Create executable reliability drill framework.
- [x] Simulate provider 429 and queue lag failures.
- [x] Simulate restart/crash recovery behavior.
- [x] Define drill SLO-based pass/fail criteria.
- [x] Persist and trend drill outcomes.
- [x] Run drills automatically in CI/nightly jobs.
- [x] Alert on drill quality regression.
- [x] Verify remediation behavior under drills.

## Confirmed implemented in this pass
- [x] Add isolated feature package scaffold under `src/scale_out_api_mcp_plugin_platform_features/feature_23_scale_failure_drills_provider_429_queue_lag_restart/`.
- [x] Implement deterministic failure-drills gate runtime and strict report contract validation.
- [x] Add unified executable `preflight`/`ci` command at `scripts/failure_drills_gate.py`.
- [x] Wire the feature gate into CI as a blocking step in `.github/workflows/ci.yml`.
- [x] Add targeted runtime and script tests with passing local evidence.
- [x] Add baseline fixture and history artifacts under `data/failure_drills/`.

## Remaining blockers to 100%
- None in current repository scope.

## Company-OS multi-agent execution packet (implemented)
- **FeatureName**: Scale failure drills (provider 429, queue lag, restart)
- **BlueprintSections**: `docs/superpowers/specs/2026-04-22-mcp-plugin-scale-solution.md` sections 4, 5, 7 and `docs/superpowers/specs/2026-04-22-10m-dau-api-choke-points-solution.md` sections 3, 4.
- **CurrentCompletionPercent**: `100`
- **PrimaryCodePaths**:
  - `src/scale_out_api_mcp_plugin_platform_features/feature_23_scale_failure_drills_provider_429_queue_lag_restart/runtime.py`
  - `src/scale_out_api_mcp_plugin_platform_features/feature_23_scale_failure_drills_provider_429_queue_lag_restart/contracts.py`
  - `scripts/failure_drills_gate.py`
- **ContractsAndInvariants**:
  - Fail closed on malformed scenario telemetry/timestamps/runbook references.
  - Derive pass/fail from measured drill metrics against SLO thresholds.
  - Enforce regression signaling and remediation runbook verification.
  - Persist deterministic report, event timeline, and trend rows per run.
- **RequiredTests**:
  - `uv run pytest tests/scale_out_api_mcp_plugin_platform/test_feature_23_failure_drills.py`
- **RequiredEvidenceArtifacts**:
  - `data/failure_drills/latest_report.json`
  - `data/failure_drills/drill_events.jsonl`
  - `data/failure_drills/trend_history.jsonl`
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
  - Runtime is deterministic simulation in repo scope; production chaos orchestration adapters remain environment-specific integration work.

## Research papers/patterns applied
- Chaos engineering steady-state + controlled fault injection:
  - [Principles of Chaos Engineering paper](https://arxiv.org/pdf/1702.05843)
- Drill execution model and automation inspiration:
  - [Netflix Simian Army](https://netflixtechblog.com/the-netflix-simian-army-16e57fbab116)
  - [LitmusChaos repository](https://github.com/litmuschaos/litmus)
- Overload/retry guardrails used in SLO/regression checks:
  - [Google SRE handling overload](https://sre.google/sre-book/handling-overload/)
  - [AWS retries/backoff/jitter](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/)

## Review method
- [x] Independent auditor A review complete.
- [x] Independent auditor B review complete.
- [x] Conservative score set to minimum of both auditors.
- [x] Confirmed-missing list created only from overlap themes.

## Additional implemented in latest pass
- [x] Replace boolean-only drill simulation checks with structured scenario validation for provider-429, queue-lag, and restart drill sets.
- [x] Enforce explicit drill framework identity (`framework_version`) in runtime gate semantics.
- [x] Enforce structured SLO threshold fields (`max_429_error_rate_pct`, `max_queue_lag_seconds`, `max_restart_recovery_seconds`) and persisted drill-run identity (`last_drill_run_id`).
- [x] Enforce schedule semantics (`execution_schedule`) and non-empty alert routing channels for regression alerting checks.
- [x] Enforce remediation verification evidence (`verified_runbook_ids`) rather than marker-only booleans.
- [x] Add fail-closed regression coverage for invalid scenario outcomes.
- [x] Enforce cross-scenario-set uniqueness of scenario names across provider-429, queue-lag, and restart drills to prevent duplicate scenario identity reuse.
- [x] Add fail-closed regression coverage for duplicate scenario names across drill scenario sets.
- [x] Enforce persisted-drill coherence by requiring aligned non-empty `last_drill_run_id` across SLO and remediation artifacts.
- [x] Add fail-closed regression coverage for `last_drill_run_id` drift across SLO/remediation artifacts.
