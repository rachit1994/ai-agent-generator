# Persona Agent Platform Delivery Process (Production)

## Operating Principle
This program ships **once** to production configuration when **all** gates pass for the **full** production workflow manifest. Milestones are integration checkpoints with evidence; they are **not** separately releasable MVPs.

**Contributor execution guide:** `docs/implementation/2026-04-13-persona-agent-platform-execution-playbook.md` (reading order, glossary, machine prerequisites, evaluator corner cases).

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
- unit, integration, and **full-manifest** E2E tests pass with stable repeatability across the **production workflow manifest**.
- **DeepEval** (pytest) suites pass in CI with pinned dependencies; **RAGAS** metrics pass where semantic retrieval is in scope.
- **promptfoo** prompt and policy suites pass for every suite version pinned in the release candidate; failures block.
- **agentevals** scores on sampled **OpenTelemetry** traces meet thresholds defined in the gate packet, **or** a **Tech Lead-signed** full re-run evaluation is attached that meets the **identical** pass/fail criteria (see execution playbook—silent omission fails the gate).

Gate 3: **Safety Gate**
- input/action/output policy checks and temporal constraints pass.

Gate 4: **Performance Gate**
- latency and resource targets satisfy current SLO budgets.

Gate 5: **Observability Gate**
- traces, logs, and key metrics emitted and queryable in dashboards (OTel backend or **Langfuse** if deployed).
- OTel export remains mandatory; Langfuse is supplementary when enabled.

### 4) Release Readiness
Required before **the single** deployment promotion:
- canary plan with explicit success/failure thresholds,
- on-call and escalation roster confirmed,
- rollback procedure tested on latest artifact,
- release notes and runbook updates completed.
- rollback units verified for runtime build, prompt-policy bundle, validator bundle, routing policy, and memory schema.

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
- Safety gate waivers are not allowed for production promotion.

## Evidence Requirements
Every milestone submission must include:
- test report links,
- policy validation output,
- performance benchmark results,
- telemetry dashboard links,
- sign-off records by gate owners.
- **promptfoo** run artifacts (or CI links) for the pinned suite revision,
- **DeepEval** / CI test report links and, where used, **RAGAS** metric tables,
- **agentevals** (or documented substitute) outputs when trace-based scoring is claimed,
- and explicit coverage mapping from evidence to **every** workflow in the production workflow manifest.

## Evaluator and tooling edge cases
- **RAGAS:** if no RAG-style retrieval is under test for a suite, attach **Quality Owner-signed N/A** in the gate packet; other DeepEval tests still run.
- **promptfoo / CI flakes:** maximum **three** deterministic retries per workflow per pipeline run; then block and open a defect.
- **Langfuse unavailable:** not a gate failure if OTel evidence is complete; Langfuse is supplementary only.

## Dependency Failure Behavior Matrix (Required)
- For each dependency (`Ollama`, `vLLM`, Postgres/`pgvector`, telemetry sink), define and test behavior for `happy`, `nil`, `empty`, and `error` states.
- Mandatory behavior contracts:
  - inference backend outage -> fallback to healthy backend or fail-closed for safety-critical flows,
  - memory retrieval empty result -> continue only with explicit `no-memory` marker and stricter reviewer gate,
  - policy/validator timeout -> fail-closed,
  - telemetry sink outage -> release is blocked and runtime can proceed only with local buffered audit logs.
