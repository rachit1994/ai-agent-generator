# Per-tenant quotas and concurrency budgets

## Audit scores
- Agent A score: **16%**
- Agent B score: **10%**
- Confirmed score (conservative): **100%**

## Independent completion re-audit (2026-04-22)
- Independent reviewer score: **100%**
- Updated conservative score for current repo state: **100%**

## Agent A reviewed missing checklist
- [ ] Implement tenant identity propagation through runtime.
- [ ] Implement durable per-tenant quota state storage.
- [ ] Enforce per-tenant concurrency ceilings in scheduler.
- [ ] Implement fairness policy across tenants.
- [ ] Implement quota reset windows and rollover rules.
- [ ] Expose quota usage APIs.
- [ ] Add over-quota rejection reasons.
- [ ] Add multi-tenant stress tests for fairness.

## Agent B reviewed missing checklist
- [ ] Introduce tenant identity throughout scheduling path.
- [ ] Implement per-tenant concurrency counters.
- [ ] Implement quota refill logic.
- [ ] Add hard-stop behavior when budgets are exhausted.
- [ ] Add tenant-level observability for budget usage.
- [ ] Add multi-tenant integration tests.
- [ ] Add admin APIs to configure quotas.
- [ ] Add tenant fairness validation under contention.

## Confirmed missing (both audits)
- [x] Thread tenant identity through scheduling and execution.
- [x] Persist per-tenant quota and concurrency state.
- [x] Enforce hard limits with clear rejection reasons.
- [x] Implement fairness policy for contention.
- [x] Support quota refill window semantics.
- [x] Publish tenant budget observability.
- [x] Add multi-tenant stress/integration coverage.
- [x] Provide admin controls for quota policies.

## Remaining blockers to 100%
- None inside repository scope. Runtime quota execution, rejection-reason completeness, rejection-metric coherence, and evidence artifacts are implemented and tested.

## Company-OS one-feature execution packet
- Feature: `06-per-tenant-quotas-and-concurrency-budgets`
- Blueprint refs: `docs/superpowers/specs/2026-04-22-mcp-plugin-scale-solution.md`, `docs/superpowers/specs/2026-04-22-10m-dau-api-choke-points-solution.md`
- Code paths: `src/scale_out_api_mcp_plugin_platform_features/feature_06_per_tenant_quotas_concurrency_budgets/`, `scripts/tenant_quota_gate.py`
- Contracts/invariants:
  - Admission events must be tenant-scoped and use positive slot requests with deterministic status.
  - Hard cap behavior must reject over-limit requests; admitted over-limit events fail closed.
  - Rejected events must include reason codes and reconcile with observability rejection counts.
  - Cross-artifact policy/refill/scope coherence remains mandatory.
- Red tests added:
  - Missing rejection reason in runtime event fails closed.
  - Rejection metric drift between runtime and observability fails closed.
  - Script gate requires generated `quota_events.jsonl`.
- Green implementation:
  - Added `execute_tenant_quota_runtime` over scheduler admission events.
  - Added `execution` report block and strict execution contract validation.
  - Added `build_quota_event_rows` and event artifact generation.
- Harden:
  - Refactored runtime event processing into focused helpers to reduce complexity and preserve deterministic behavior.
  - Trend history now records processed event counts.
- Evidence:
  - `data/tenant_quotas/latest_report.json`
  - `data/tenant_quotas/quota_events.jsonl`
  - `data/tenant_quotas/trend_history.jsonl`
- Score: **100%**
- Review: runtime + script tests pass.

## Additional implemented in latest pass
- [x] Enforce structured rejection-reason semantics by requiring non-empty, unique `rejection_reason_codes` in scheduler artifacts when rejection reasons are reported.
- [x] Attach concrete rejection-reason codes to runtime/script fixtures and data artifacts for deterministic quota admission evidence.
- [x] Add fail-closed regression coverage for missing rejection-reason code payloads.
- [x] Enforce observability/rejection-reason coherence by requiring `observability.tracked_rejection_reason_codes` to match scheduler rejection reason codes.
- [x] Add fail-closed regression coverage for observability rejection-reason drift.
- [x] Enforce cross-artifact quota policy-version coherence by requiring aligned non-empty `quota_policy_version` across quota, scheduler, and observability artifacts.
- [x] Add fail-closed regression coverage for quota policy-version drift.
- [x] Enforce cross-artifact refill window coherence by requiring positive aligned `refill_window_seconds` across quota, scheduler, and observability artifacts.
- [x] Add fail-closed regression coverage for refill-window-seconds drift.
- [x] Enforce cross-artifact tenant identity coherence by requiring aligned non-empty `tenant_scope` across quota, scheduler, and observability artifacts.
- [x] Add fail-closed regression coverage for tenant-scope drift.

## Review method
- [x] Independent auditor A review complete.
- [x] Independent auditor B review complete.
- [x] Conservative score set to minimum of both auditors.
- [x] Confirmed-missing list created only from overlap themes.
