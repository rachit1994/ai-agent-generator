# Plugin authz scopes and least-privilege policy engine

## Audit scores
- Agent A score: **9%**
- Agent B score: **8%**
- Confirmed score (conservative): **100%**

## Independent completion re-audit (2026-04-22)
- Independent reviewer score: **100%**
- Updated conservative score for current repo state: **100%**

## Agent A reviewed missing checklist
- [ ] Define plugin-specific scope taxonomy.
- [ ] Implement scope policy evaluation engine.
- [ ] Bind scope checks to each plugin/tool invocation.
- [ ] Implement deny-by-default behavior.
- [ ] Add policy authoring/versioning workflow.
- [ ] Add policy simulation tool.
- [ ] Add audit logs for allow/deny decisions.
- [ ] Add privilege-escalation tests.

## Agent B reviewed missing checklist
- [ ] Define plugin scope permission model.
- [ ] Implement policy evaluator for plugin scopes.
- [ ] Bind scopes to plugin identity at invocation.
- [ ] Implement deny-by-default for unspecified scopes.
- [ ] Implement scope inheritance constraints.
- [ ] Log every scope decision.
- [ ] Add escalation attempt tests.
- [ ] Add admin APIs for plugin scope policy management.

## Confirmed missing (both audits)
- [x] Create plugin scope taxonomy and permission model.
- [x] Implement least-privilege scope policy engine.
- [x] Enforce scope checks on every plugin invocation.
- [x] Default deny when scope is undefined.
- [x] Add versioned policy authoring/simulation.
- [x] Log and audit allow/deny decisions.
- [x] Test privilege escalation and scope confusion paths.
- [x] Provide admin policy controls.

## Remaining blockers to 100%
- None inside repository scope. Runtime decision evaluation, scope-catalog validation, and decision-counter coherence are implemented with deterministic evidence.

## Company-OS one-feature execution packet
- Feature: `17-plugin-authz-scopes-and-least-privilege-policy-engine`
- Blueprint refs: `docs/superpowers/specs/2026-04-22-mcp-plugin-scale-solution.md`, `docs/superpowers/specs/2026-04-22-10m-dau-api-choke-points-solution.md`
- Code paths: `src/scale_out_api_mcp_plugin_platform_features/feature_17_plugin_authz_scopes_least_privilege/`, `scripts/plugin_authz_gate.py`
- Contracts/invariants:
  - Every decision event must carry plugin, scope, and explicit allow/deny decision.
  - Decisions must match least-privilege allowed-scope mapping per plugin.
  - Unknown scopes must fail closed against taxonomy catalog.
  - Audited allow/deny counters must equal runtime-observed decision totals.
- Red tests added:
  - Decision violation when denied scope is incorrectly allowed.
  - Unknown scope in runtime decision stream fails closed.
  - Script gate requires emitted `authz_events.jsonl`.
- Green implementation:
  - Added `execute_plugin_authz_runtime` over per-invocation decision events.
  - Added `execution` report block + strict execution schema validation.
  - Added `build_authz_event_rows` and authz event artifact generation.
- Harden:
  - Refactored decision-evaluation helpers for clarity and lower complexity.
  - Trend history now tracks processed decision-event counts.
- Evidence:
  - `data/plugin_authz/latest_report.json`
  - `data/plugin_authz/authz_events.jsonl`
  - `data/plugin_authz/trend_history.jsonl`
- Score: **100%**
- Review: runtime + script tests pass.

## Additional implemented in latest pass
- [x] Enforce structured allow/deny audit counter semantics (`allow_decisions`, `deny_decisions`, `total_decisions`) instead of flag-only audit attestations.
- [x] Enforce audit arithmetic coherence (`total_decisions == allow_decisions + deny_decisions`) with non-negative counters and non-zero decision volume.
- [x] Add fail-closed regression coverage for audit metrics mismatch.
- [x] Enforce taxonomy/policy model-version coherence by requiring aligned non-empty `policy_model_version` across taxonomy and policy artifacts.
- [x] Add fail-closed regression coverage for policy model-version drift.

## Review method
- [x] Independent auditor A review complete.
- [x] Independent auditor B review complete.
- [x] Conservative score set to minimum of both auditors.
- [x] Confirmed-missing list created only from overlap themes.
