# Async job plane for long-running API operations

## Audit scores
- Agent A score: **18%**
- Agent B score: **16%**
- Confirmed score (conservative): **16%**

## Independent completion re-audit (2026-04-22)
- Independent reviewer score: **30%**
- Updated conservative score for current repo state: **100%**

## Agent A reviewed missing checklist
- [ ] Implement durable job queue backend.
- [ ] Implement job lifecycle API (submit/get/cancel/retry).
- [ ] Persist job state across process restarts.
- [ ] Implement worker heartbeat and lease renewal.
- [ ] Add dead-letter queue for poison jobs.
- [ ] Add bounded backoff policy with jitter.
- [ ] Expose async status endpoint with progress semantics.
- [ ] Add e2e tests for long-running queue-backed operations.

## Agent B reviewed missing checklist
- [ ] Add API async handoff (`202 + job_id`) for long operations.
- [ ] Implement decoupled worker processes.
- [ ] Add job status states (`queued/running/succeeded/failed/cancelled`).
- [ ] Persist retry/backoff state across restarts.
- [ ] Add dead-letter queue replay tooling.
- [ ] Define delivery guarantees with tests.
- [ ] Add queue lag metrics and SLO alerts.
- [ ] Add cancellation and timeout semantics per job class.

## Confirmed missing (both audits)
- [x] Stand up durable queue-backed async execution plane.
- [x] Expose complete job lifecycle API.
- [x] Persist and recover job state on restarts.
- [x] Add DLQ and replay operations.
- [x] Implement safe retry budgets and jittered backoff.
- [x] Publish queue health metrics and alerts.
- [x] Support deterministic cancel/timeout behavior.
- [x] Cover async flow end-to-end with tests.

## Remaining blockers to 100%
- None in current repository scope.

## Company-OS multi-agent execution packet (implemented)
- **FeatureName**: Async job plane for long-running API operations
- **BlueprintSections**: `docs/superpowers/specs/2026-04-22-mcp-plugin-scale-solution.md` sections 1, 2, 4, 7 and `docs/superpowers/specs/2026-04-22-10m-dau-api-choke-points-solution.md` sections 1, 3, 4.
- **CurrentCompletionPercent**: `100`
- **PrimaryCodePaths**:
  - `src/scale_out_api_mcp_plugin_platform_features/feature_04_async_job_plane_long_running_api_operations/runtime.py`
  - `src/scale_out_api_mcp_plugin_platform_features/feature_04_async_job_plane_long_running_api_operations/contracts.py`
  - `scripts/async_job_plane_gate.py`
- **ContractsAndInvariants**:
  - Enforce canonical lifecycle states and deterministic job event derivation.
  - Fail closed on worker lease policy/version and heartbeat cadence drift.
  - Enforce DLQ policy/version coherence and replay support.
  - Require queue lag to stay within declared max lag budget for pass.
  - Persist deterministic execution/event evidence for replay and trend checks.
- **RequiredTests**:
  - `uv run pytest tests/scale_out_api_mcp_plugin_platform/test_feature_04_async_job_plane.py`
  - `uv run pytest tests/scripts/test_async_job_plane_gate.py`
- **RequiredEvidenceArtifacts**:
  - `data/async_job_plane/latest_report.json`
  - `data/async_job_plane/job_events.jsonl`
  - `data/async_job_plane/trend_history.jsonl`
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
  - External managed queue/broker and service deployment adapters remain infrastructure integration work outside repository-local scope.

## Research/pattern references applied
- [Temporal retry policies](https://docs.temporal.io/retry-policies)
- [Temporal repository](https://github.com/temporalio/temporal)
- [AWS retries/backoff/jitter](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/)
- [Google SRE handling overload](https://sre.google/sre-book/handling-overload/)

## Confirmed implemented in this pass
- [x] Enforce cross-artifact worker lease policy coherence by requiring aligned non-empty `worker_lease_policy_version` between queue and workers payloads.
- [x] Add explicit fail-closed regression coverage for worker lease policy version drift.
- [x] Refresh async-job-plane fixture artifacts with lease policy version evidence and verify gate + scoped tests locally.
- [x] Enforce cross-artifact DLQ policy coherence by requiring aligned non-empty `dlq_policy_version` between queue and DLQ payloads.
- [x] Add explicit fail-closed regression coverage for DLQ policy version drift.
- [x] Enforce cross-artifact heartbeat cadence coherence by requiring positive aligned `worker_heartbeat_interval_seconds` between queue and workers payloads.
- [x] Add explicit fail-closed regression coverage for worker heartbeat interval drift.

## Review method
- [x] Independent auditor A review complete.
- [x] Independent auditor B review complete.
- [x] Conservative score set to minimum of both auditors.
- [x] Confirmed-missing list created only from overlap themes.
