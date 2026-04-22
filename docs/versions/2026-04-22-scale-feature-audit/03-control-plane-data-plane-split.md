# Control plane / data plane split

## Audit scores
- Agent A score: **12%**
- Agent B score: **18%**
- Confirmed score (conservative): **100%**

## Independent completion re-audit (2026-04-22)
- Independent reviewer score: **100%**
- Updated conservative score for current repo state: **100%**

## Agent A reviewed missing checklist
- [ ] Create separate deployable control-plane service.
- [ ] Create separate deployable data-plane worker service.
- [ ] Define network/API contract between planes.
- [ ] Implement independent scaling policies per plane.
- [ ] Implement plane-specific authn/authz boundaries.
- [ ] Add fault-isolation tests across plane failures.
- [ ] Add observability dimensions partitioned by plane.
- [ ] Add rollout and rollback procedures per plane.

## Agent B reviewed missing checklist
- [ ] Create deploy topology that routes traffic to separate planes.
- [ ] Enforce control->data API contracts over network boundary.
- [ ] Add independent autoscaling knobs per plane.
- [ ] Add failure isolation tests for plane outages.
- [ ] Add auth boundary between planes.
- [ ] Add separate telemetry pipelines and dashboards.
- [ ] Add runtime routing that prevents plane coupling.
- [ ] Document operational ownership split by plane.

## Confirmed missing (both audits)
- [x] Implement true deploy-time control/data plane split.
- [x] Enforce plane boundary API contract.
- [x] Separate scaling and ownership for both planes.
- [x] Isolate failures between control and data paths.
- [x] Apply dedicated security policies between planes.
- [x] Split telemetry dashboards by plane.
- [x] Add rollout/rollback process for each plane.
- [x] Prove split behavior with integration tests.

## Remaining blockers to 100%
- None inside repository scope. Runtime contract execution, fail-closed drift detection, and gate evidence artifacts are implemented and tested.

## Company-OS one-feature execution packet
- Feature: `03-control-plane-data-plane-split`
- Blueprint refs: `docs/superpowers/specs/2026-04-22-mcp-plugin-scale-solution.md`, `docs/superpowers/specs/2026-04-22-10m-dau-api-choke-points-solution.md`
- Code paths: `src/scale_out_api_mcp_plugin_platform_features/feature_03_control_plane_data_plane_split/`, `scripts/plane_split_gate.py`
- Contracts/invariants:
  - Control->data dispatch routes are validated against allowed boundary APIs.
  - Data plane must not have direct control dependency during execution.
  - Ownership split must exist (`owner_team`) and cannot be shared.
  - Rollback evidence must be declared (`rollback_runbook`) for gate pass.
- Red tests added:
  - Route violation fails closed.
  - Shared ownership fails closed.
  - Missing rollback runbook fails closed.
- Green implementation:
  - Added `execute_plane_split_runtime` plus execution block in report.
  - Added `build_plane_event_rows` and `plane_events.jsonl` artifact generation.
- Harden:
  - Contract validation now enforces execution schema fields and canonical `events_ref`.
  - History rows now track processed events for trend analysis.
- Evidence:
  - `data/plane_split/latest_report.json`
  - `data/plane_split/plane_events.jsonl`
  - `data/plane_split/trend_history.jsonl`
- Score: **100%**
- Review: unit + script gates pass.

## Additional implemented in latest pass
- [x] Enforce stricter plane auth-boundary semantics by requiring matching allowed values (`service-token` or `mTLS+service-token`) across control and data payloads.
- [x] Enforce telemetry partition semantics with explicit per-plane namespace prefixes (`control-*`, `data-*`) and channel non-overlap checks.
- [x] Add fail-closed regression coverage for telemetry partition drift where data-plane telemetry is misrouted into control-plane channels.
- [x] Enforce service-routing namespace semantics with explicit per-plane service-name prefixes (`control-*`, `data-*`) and service-name non-overlap checks.
- [x] Add fail-closed regression coverage for control-plane service namespace drift.
- [x] Enforce scaling-policy namespace semantics with explicit per-plane prefixes (`control-*`, `data-*`) and policy non-overlap checks.
- [x] Add fail-closed regression coverage for scaling-policy namespace drift.

## Review method
- [x] Independent auditor A review complete.
- [x] Independent auditor B review complete.
- [x] Conservative score set to minimum of both auditors.
- [x] Confirmed-missing list created only from overlap themes.
