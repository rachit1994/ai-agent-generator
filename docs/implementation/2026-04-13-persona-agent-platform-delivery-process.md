# Persona Agent Platform Delivery Process (Production)

## Operating Principle
This program ships only production-ready increments. Every milestone must satisfy engineering, safety, reliability, and operations gates before progression.

## Roles and Accountability
- **Engineering Manager (A):** scope governance, staffing, gate enforcement, release decision authority.
- **Tech Lead (R):** architecture consistency, contract quality, integration sequencing.
- **Feature DRIs (R):** implementation and validation evidence for assigned subsystem.
- **Quality Owner (R):** test strategy and pass-rate governance.
- **Safety Owner (R):** policy and temporal constraint assurance.
- **SRE/Operations Owner (R):** rollout, monitoring, and rollback readiness.

## Lifecycle
### 1) Definition of Ready
Entry criteria:
- clear objective and machine-checkable acceptance criteria,
- interface contracts with versioning impacts,
- dependency map and critical-path acknowledgement,
- security/threat risks and mitigations logged,
- rollback strategy and telemetry requirements defined.

Exit criteria:
- EM and TL sign-off with named DRI and due window.

### 2) Build (TDD-Enforced)
- Red: create failing tests for each acceptance criterion.
- Green: implement minimum production-quality logic to pass tests.
- Refactor: improve maintainability while keeping all tests green.
- No skipped tests and no unresolved critical lint/type/security issues.

### 3) Validation Gates
Gate 1: **Contract and Schema Gate**
- API/input/output schemas validated and compatibility checks passed.

Gate 2: **Quality Gate**
- unit, integration, and targeted E2E tests pass with stable repeatability.

Gate 3: **Safety Gate**
- input/action/output policy checks and temporal constraints pass.

Gate 4: **Performance Gate**
- latency and resource targets satisfy current SLO budgets.

Gate 5: **Observability Gate**
- traces, logs, and key metrics emitted and queryable in dashboards.

### 4) Release Readiness
Required before deployment promotion:
- canary plan with explicit success/failure thresholds,
- on-call and escalation roster confirmed,
- rollback procedure tested on latest artifact,
- release notes and runbook updates completed.

### 5) Post-Release Review
- verify SLO compliance during soak period,
- capture incidents and near misses,
- convert repeated failure patterns into prevention checks.

## Weekly Cadence
- **Monday:** scope lock, dependency/risk review, DOR checks.
- **Wednesday:** architecture and integration checkpoint with gate pre-read.
- **Friday:** gate board review; decision = pass, block, or rollback prep.

## Block Policy
- Any failed critical gate blocks progression.
- Waivers require accountable owner, expiry date, and mitigation plan.
- Repeated waiver use on same subsystem triggers escalation to EM and TL.

## Evidence Requirements
Every milestone submission must include:
- test report links,
- policy validation output,
- performance benchmark results,
- telemetry dashboard links,
- sign-off records by gate owners.
