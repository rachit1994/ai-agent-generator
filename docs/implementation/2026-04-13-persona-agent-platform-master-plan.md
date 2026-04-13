# Persona Agent Platform Master Plan (Production)

## Purpose
This package defines how we will deliver a production-ready persona agent platform in one quarter, with hard quality gates, explicit owners, and measurable reliability outcomes.

## Scope
- Build and operationalize the hybrid, local-first persona platform defined in `docs/superpowers/specs/2026-04-13-persona-agent-platform-design.md`.
- Deliver usable production capability, not a pilot track and not an MVP-only scope.
- Cover architecture decisions, delivery process, roadmap, risk controls, and SLO governance.

## Production Outcomes (Quarter End)
- All targeted persona workflows compile and execute with gate pass/fail evidence.
- Unsafe actions are blocked before execution through policy and temporal constraints.
- Failure-memory retrieval prevents repeat incidents from passing unchallenged.
- Observability and replay are available for run-level diagnostics and audits.
- Release operations support canary promotion and rollback with owned runbooks.

## Document Map
- `docs/implementation/2026-04-13-persona-agent-platform-tech-decisions.md`
- `docs/implementation/2026-04-13-persona-agent-platform-delivery-process.md`
- `docs/implementation/2026-04-13-persona-agent-platform-roadmap-q1.md`
- `docs/implementation/2026-04-13-persona-agent-platform-risk-register.md`
- `docs/implementation/2026-04-13-persona-agent-platform-metrics-and-slos.md`
- `docs/implementation/2026-04-13-persona-agent-platform-quality-self-improvement-advancements.md`

## Quality and Self-Improvement Upgrade Policy
- Research-driven upgrades are tracked in the advancements document and triaged as `adopt-now`, `pilot`, or `backlog`.
- Any `adopt-now` item must map to a roadmap week, owner, and measurable gate or SLO delta.
- Experimental techniques must run in shadow or canary mode before they can influence release decisions.

## Governance Model
- **Engineering Manager (Accountable):** delivery, quality gate enforcement, staffing, risk posture.
- **Tech Lead (Responsible):** architecture integrity, interface contracts, technical decision records.
- **Subsystem DRIs (Responsible):** planner, run engine, memory, safety, observability, evaluation harness.
- **Quality Gate Owners (Responsible):** test gate, policy gate, performance gate, release gate.
- **Product/Operations Stakeholders (Consulted/Informed):** milestone acceptance and rollout readiness.

## Decision Policy
- No milestone exits with unresolved critical defects, failed policy checks, or missing evidence.
- Gate waivers require explicit accountable owner, expiry date, and compensating controls.
- Release to wider cohorts only after canary SLO adherence and incident-free soak window.

## Program Cadence
- Weekly planning and risk review.
- Midweek architecture and implementation checkpoint.
- End-of-week gate review with pass/block decisions.
- Monthly operating review on trend metrics and risk burndown.

## Dependencies and Preconditions
- Local inference environments (`Ollama`, `vLLM`) available and benchmarkable.
- Shared Postgres infrastructure with `pgvector` extension available.
- Baseline observability stack configured before high-volume test runs.
- Test harness and regression suite ownership assigned before milestone 2 starts.

## Acceptance Rules for This Package
- All linked documents contain explicit owners and measurable exit criteria.
- No ambiguous phrases such as "later", "future", or "TBD" in required sections.
- Cross-document consistency between roadmap, gates, risks, and SLO thresholds.
