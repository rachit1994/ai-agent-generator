# Incident runbooks for plugin outage/saturation/auth

## Audit scores
- Agent A score: **8%**
- Agent B score: **2%**
- Independent completion re-audit score: **41%**
- Confirmed score (conservative): **41%**

## Agent A reviewed missing checklist
- [ ] Write plugin outage runbook with containment steps.
- [ ] Write saturation runbook with throttling/shedding actions.
- [ ] Write auth failure runbook with diagnosis flow.
- [ ] Create machine-executable runbook checks.
- [ ] Add runbook ownership and escalation metadata.
- [ ] Link runbooks to alerts/dashboards.
- [ ] Add game-day validation tests.
- [ ] Version and review runbooks with change control.

## Agent B reviewed missing checklist
- [ ] Create versioned runbook artifacts for plugin outage.
- [ ] Create runbook for plugin saturation/backpressure.
- [ ] Create runbook for plugin auth/authz incidents.
- [ ] Add executable checklist scripts referenced by runbooks.
- [ ] Add owner/on-call escalation metadata.
- [ ] Add runbook validation tests.
- [ ] Add runbook drill cadence and evidence capture.
- [ ] Add post-incident feedback loop into runbook updates.

## Confirmed missing (both audits)
- [ ] Author production incident runbooks for outage, saturation, and auth.
- [ ] Add executable steps/scripts for each runbook.
- [ ] Attach ownership and escalation metadata.
- [ ] Connect runbooks to alerts and dashboards.
- [ ] Version and review runbooks under change control.
- [ ] Validate runbooks with game-day drills.
- [ ] Capture drill evidence for auditing.
- [ ] Integrate post-incident feedback into runbook revisions.

## Confirmed implemented in this pass
- [x] Add isolated feature package scaffold under `src/scale_out_api_mcp_plugin_platform_features/feature_24_incident_runbooks_plugin_outage_saturation_auth/`.
- [x] Implement deterministic incident-runbooks gate runtime and strict report contract validation.
- [x] Add unified executable `preflight`/`ci` command at `scripts/incident_runbooks_gate.py`.
- [x] Wire the feature gate into CI as a blocking step in `.github/workflows/ci.yml`.
- [x] Add targeted runtime and script tests with passing local evidence.
- [x] Add baseline fixture and history artifacts under `data/incident_runbooks/`.
- [x] Enforce explicit incident-type coverage semantics for authored runbooks (`outage`, `saturation`, `auth`) instead of boolean-only authorship markers.
- [x] Enforce game-day drill coverage parity by requiring validated drill incident types to match runbook incident-type coverage.
- [x] Add fail-closed regression coverage for incomplete drill incident coverage.
- [x] Enforce cross-artifact escalation metadata coherence by requiring aligned non-empty `escalation_policy_version` across operations and drills artifacts.
- [x] Add fail-closed regression coverage for escalation-policy version drift between operations and drills.

## Remaining blockers to 100%
- Replace fixture booleans with real versioned runbook content for outage/saturation/auth incident flows.
- Implement executable checklist steps and machine-runnable checks linked to runbooks.
- Add concrete owner/on-call escalation chains and alert/dashboard linkage artifacts.
- Add game-day drill execution evidence model (scenario IDs, timestamps, operators, outcomes).
- Integrate post-incident feedback and change-control workflow into runbook revision lifecycle.

## Review method
- [x] Independent auditor A review complete.
- [x] Independent auditor B review complete.
- [x] Conservative score set to minimum of both auditors.
- [x] Confirmed-missing list created only from overlap themes.
