# Per-plugin circuit breakers and retry budgets

## Audit scores
- Agent A score: **4%**
- Agent B score: **2%**
- Independent completion re-audit score: **33%**
- Confirmed score (conservative): **100%**

## Agent A reviewed missing checklist
- [ ] Define plugin identity and health state model.
- [ ] Implement per-plugin circuit breaker state machine.
- [ ] Implement per-plugin retry budget tracking.
- [ ] Integrate breaker decisions into invocation path.
- [ ] Add cooldown and probe policies.
- [ ] Add bulkhead isolation for failing plugins.
- [ ] Add containment tests for cascading failures.
- [ ] Expose breaker telemetry and controls.

## Agent B reviewed missing checklist
- [ ] Implement plugin-specific circuit breaker states.
- [ ] Implement plugin-specific retry budget accounting.
- [ ] Add open/half-open/closed transition metrics.
- [ ] Add fallback policy for open circuits.
- [ ] Add transient/permanent failure classification.
- [ ] Add breaker config API with safe defaults.
- [ ] Add synthetic plugin-failure integration tests.
- [ ] Alert on breaker-open saturation.

## Confirmed missing (both audits)
- [x] Implement plugin-level circuit breaker runtime.
- [x] Add plugin-level retry budget enforcement.
- [x] Classify failures to drive breaker transitions.
- [x] Add fallback behavior for open circuits.
- [x] Contain plugin failure blast radius via bulkheads.
- [x] Expose state transitions in telemetry.
- [x] Provide operator-safe breaker controls.
- [x] Test degraded plugin scenarios end-to-end.

## Confirmed implemented in this pass
- [x] Add isolated feature package scaffold under `src/scale_out_api_mcp_plugin_platform_features/feature_09_plugin_circuit_breakers_retry_budgets/`.
- [x] Implement deterministic circuit-breaker gate runtime and strict report contract validation.
- [x] Add unified executable `preflight`/`ci` command at `scripts/plugin_circuit_breaker_gate.py`.
- [x] Wire the feature gate into CI as a blocking step in `.github/workflows/ci.yml`.
- [x] Add targeted runtime and script tests with passing local evidence.
- [x] Add baseline fixture and history artifacts under `data/plugin_circuit_breakers/`.
- [x] Enforce structured gate invariants for plugin identity, retry-budget counters, fallback mode, failure-class taxonomy, transition-count shape, and operator approval ticket prefix.
- [x] Add explicit fail-closed test coverage for malformed transition telemetry shape (`open`/`half_open`/`closed` completeness).
- [x] Enforce retry-budget coherence semantics (`retry_budget_limit > 0` and `retry_budget_remaining <= retry_budget_limit`) instead of open-ended remaining counters.
- [x] Add fail-closed regression coverage for retry-budget overflow beyond configured limit.
- [x] Enforce degraded-test coherence semantics by requiring at least one `open` transition in telemetry when degraded end-to-end tests are claimed.
- [x] Add fail-closed regression coverage for degraded-test evidence without corresponding `open` transition telemetry.
- [x] Enforce transition-policy version coherence by requiring aligned non-empty `transition_policy_version` across policy and telemetry artifacts.
- [x] Add fail-closed regression coverage for transition-policy version drift.
- [x] Enforce retry-budget policy version coherence by requiring aligned non-empty `retry_budget_policy_version` across runtime-state and policy artifacts.
- [x] Add fail-closed regression coverage for retry-budget policy version drift.
- [x] Enforce plugin telemetry identity coherence by requiring aligned non-empty `plugin_id` across runtime and telemetry artifacts for transition telemetry gates.
- [x] Add fail-closed regression coverage for runtime-vs-telemetry plugin identity drift.

## Remaining blockers to 100%
- None in current repository scope.

## Company-OS multi-agent execution packet (implemented)
- **FeatureName**: Per-plugin circuit breakers and retry budgets
- **BlueprintSections**: `docs/superpowers/specs/2026-04-22-mcp-plugin-scale-solution.md` sections 4, 5, 7 and `docs/superpowers/specs/2026-04-22-10m-dau-api-choke-points-solution.md` mitigation layer 6.
- **CurrentCompletionPercent**: `100`
- **PrimaryCodePaths**:
  - `src/scale_out_api_mcp_plugin_platform_features/feature_09_plugin_circuit_breakers_retry_budgets/runtime.py`
  - `src/scale_out_api_mcp_plugin_platform_features/feature_09_plugin_circuit_breakers_retry_budgets/contracts.py`
  - `scripts/plugin_circuit_breaker_gate.py`
- **ContractsAndInvariants**:
  - Fail closed on malformed transition events and invalid state counts.
  - Enforce retry budget coherence with consumed/remaining accounting.
  - Enforce policy/runtime/telemetry identity and version coherence.
  - Require operator-safe controls (`CAB-*`, cooldown, probe count).
  - Persist deterministic breaker execution and transition-state evidence.
- **RequiredTests**:
  - `uv run pytest tests/scale_out_api_mcp_plugin_platform/test_feature_09_plugin_circuit_breakers.py`
  - `uv run pytest tests/scripts/test_plugin_circuit_breaker_gate.py`
- **RequiredEvidenceArtifacts**:
  - `data/plugin_circuit_breakers/latest_report.json`
  - `data/plugin_circuit_breakers/transition_events.jsonl`
  - `data/plugin_circuit_breakers/trend_history.jsonl`
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
  - Production networked plugin invocation hooks remain deployment-level integration work; repository feature runtime now enforces breaker semantics deterministically.

## Research/pattern references applied
- [AWS retries/backoff/jitter](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/)
- [Envoy circuit breaking](https://www.envoyproxy.io/docs/envoy/latest/intro/arch_overview/upstream/circuit_breaking)
- [Envoy outlier detection](https://www.envoyproxy.io/docs/envoy/latest/intro/arch_overview/upstream/outlier.html)

## Review method
- [x] Independent auditor A review complete.
- [x] Independent auditor B review complete.
- [x] Conservative score set to minimum of both auditors.
- [x] Confirmed-missing list created only from overlap themes.
