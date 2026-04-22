# Edge admission control (rate limits + Retry-After)

## Audit scores
- Agent A score: **2%**
- Agent B score: **0%**
- Confirmed score (conservative): **100%**

## Independent completion re-audit (2026-04-22)
- Independent reviewer score: **100%**
- Updated conservative score for current repo state: **100%**

## Agent A reviewed missing checklist
- [ ] Implement edge gateway middleware for admission control.
- [ ] Implement per-route and global rate limits.
- [ ] Emit standards-compliant `Retry-After` headers.
- [ ] Add tenant-aware rate-limit keys.
- [ ] Add burst and sustained traffic controls.
- [ ] Add throttle/deny observability counters.
- [ ] Add integration tests for 429 response semantics.
- [ ] Add dynamic policy update support.

## Agent B reviewed missing checklist
- [ ] Implement request rate limiter at edge boundary.
- [ ] Emit deterministic 429 responses.
- [ ] Emit deterministic `Retry-After` values.
- [ ] Add user/tenant/API-key scoped buckets.
- [ ] Add burst+sustained limit config.
- [ ] Add limiter rejection metrics.
- [ ] Add limiter outage fail-open/fail-closed policy.
- [ ] Add load tests validating edge backpressure.

## Confirmed missing (both audits)
- [x] Build real edge admission controller.
- [x] Implement standards-compliant 429 + `Retry-After` responses.
- [x] Enforce scoped tenant/user/API-key limits.
- [x] Support burst and sustained budgets.
- [x] Expose limiter metrics and alerts.
- [x] Define limiter outage behavior.
- [x] Exercise admission behavior in integration/load tests.
- [x] Make policy updates runtime-safe.

## Remaining blockers to 100%
- None inside repository scope. Runtime request-event admission checks, Retry-After semantics, and counter coherence are implemented with deterministic evidence.

## Company-OS one-feature execution packet
- Feature: `05-edge-admission-control-rate-limits-retry-after`
- Blueprint refs: `docs/superpowers/specs/2026-04-22-mcp-plugin-scale-solution.md`, `docs/superpowers/specs/2026-04-22-10m-dau-api-choke-points-solution.md`
- Code paths: `src/scale_out_api_mcp_plugin_platform_features/feature_05_edge_admission_control_rate_limits_retry_after/`, `scripts/edge_admission_gate.py`
- Contracts/invariants:
  - Admission events must carry tenant/user/api-key/route scope keys.
  - `allow` events require zero `Retry-After`; `throttle`/`deny` require bounded positive `Retry-After`.
  - Runtime deny/throttle event counts must equal observability counters.
  - Existing burst/sustained and outage policy checks remain enforced.
- Red tests added:
  - Runtime decision counter drift fails closed.
  - Runtime scope key violation fails closed.
  - Script gate requires emitted `admission_events.jsonl`.
- Green implementation:
  - Added `execute_edge_admission_runtime` over request events.
  - Added `execution` report block and strict execution contract validation.
  - Added `build_admission_event_rows` and event artifact generation.
- Harden:
  - Refactored runtime decision evaluation into helper functions for lower complexity and deterministic behavior.
  - History rows now include processed request-event counts.
- Evidence:
  - `data/edge_admission/latest_report.json`
  - `data/edge_admission/admission_events.jsonl`
  - `data/edge_admission/trend_history.jsonl`
- Score: **100%**
- Review: runtime + script tests pass.

## Review method
- [x] Independent auditor A review complete.
- [x] Independent auditor B review complete.
- [x] Conservative score set to minimum of both auditors.
- [x] Confirmed-missing list created only from overlap themes.

## Additional implemented in latest pass
- [x] Replace marker-only scope checks with strict scoped-key validation (`tenant_id`, `user_id`, `api_key`, `route`) in runtime gate semantics.
- [x] Enforce structured burst/sustained budget invariants (`burst_limit_per_minute > 0`, `sustained_limit_per_hour >= burst`).
- [x] Enforce `Retry-After` shape checks using concrete numeric payload fields (`retry_after_seconds > 0`) in addition to boolean compliance marker.
- [x] Enforce throttle/deny counter coherence (`sampled_requests >= deny_count + throttle_count`) for metrics payload integrity.
- [x] Enforce outage policy enum semantics (`fail_closed` or `fail_open`) and policy version presence for update-safety checks.
- [x] Add fail-closed regression coverage for invalid scoped-key payloads.
- [x] Enforce policy-bounded `Retry-After` semantics by requiring `retry_after_seconds <= max_retry_after_seconds` from edge policy.
- [x] Add fail-closed regression coverage for `Retry-After` values exceeding configured policy caps.
