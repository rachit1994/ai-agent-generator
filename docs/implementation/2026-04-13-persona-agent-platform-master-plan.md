# Persona Agent Platform Master Plan (Production)

## Purpose
This package defines how we deliver a **production-ready** persona agent platform in **one shot**: a single production-quality program that runs until **all** exit criteria pass. There is **no MVP**, **no quarter-bound partial scope**, and **no production promotion** until the full design and manifest-backed workflow set are implemented and gated.

## Scope
- Build and operationalize the hybrid, local-first persona platform defined in `docs/superpowers/specs/2026-04-13-persona-agent-platform-design.md`.
- Deliver **full** production capability described in that design and in the **production workflow manifest** (complete inventory from persona sources).
- Cover architecture decisions, delivery process, implementation roadmap, risk controls, and SLO governance.
- Lock program scope to committed production outcomes; experimental tracks cannot weaken or replace required outcomes.

## Production Outcomes (Program Exit)
- **All** workflows in the production workflow manifest compile and execute with gate pass/fail evidence.
- **Dual-backend parity:** every manifest workflow is validated on both `Ollama` and `vLLM` with evidence packets per `docs/implementation/2026-04-13-persona-agent-platform-tech-decisions.md`.
- Unsafe actions are blocked before execution through policy and temporal constraints.
- Failure-memory retrieval prevents repeat incidents from passing unchallenged; **no-repeat-failure** rules per `docs/implementation/2026-04-13-persona-agent-platform-release-gate-spec.md` are enforced.
- **Tree-search planning**, **local runtime API/CLI/scheduling**, **`langgraph-checkpoint-postgres`**, **Instructor**, **openai-guardrails-python**, **promptfoo**, **agentevals**, and **DeepEval**/**RAGAS**-backed gates are live as specified in the base design and tech decisions.
- Observability and replay are available for run-level diagnostics and audits.
- Generative memory and prompt-policy evolution operate under governance (shadow → promotion) as **part of** production, not a separate product phase.
- Release operations support a **single** canary window, promotion, and rollback with owned runbooks.

## Document Map
- `docs/implementation/2026-04-13-persona-agent-platform-doc-precedence.md` (**read second after `README.md`; overrides conflicting prose**)
- `docs/implementation/2026-04-13-persona-agent-platform-tech-decisions.md`
- `docs/implementation/2026-04-13-persona-agent-platform-delivery-process.md`
- `docs/implementation/2026-04-13-persona-agent-platform-implementation-roadmap.md`
- `docs/implementation/2026-04-13-persona-agent-platform-risk-register.md`
- `docs/implementation/2026-04-13-persona-agent-platform-metrics-and-slos.md`
- `docs/implementation/2026-04-13-persona-agent-platform-quality-self-improvement-advancements.md`
- `docs/implementation/2026-04-13-persona-agent-platform-release-gate-spec.md`
- `docs/implementation/2026-04-13-persona-agent-platform-research-and-oss-integration.md`
- `docs/implementation/2026-04-13-persona-agent-platform-execution-playbook.md`
- `docs/implementation/production-workflow-manifest.md`
- `docs/implementation/2026-04-13-persona-agent-platform-phased-checklist.md` (single plain-English step list by phase)

## Quality and Self-Improvement Upgrade Policy
- Research-driven upgrades are tracked in the advancements document and triaged as `adopt-now`, `controlled-rollout`, or `backlog`.
- **`adopt-now`** items are mandatory for **production exit** and must map to a roadmap phase, owner, and measurable gate or SLO delta.
- **`controlled-rollout`** items ship behind flags and promotion ladders but are still **required** to reach configured production modes before exit (not optional post-launch work).
- **`backlog`** items are explicitly out of production exit until promoted with EM + Tech Lead sign-off.
- Experimental techniques that are not yet in `adopt-now` must run in shadow or canary and **must not** influence promotion decisions until promoted per policy.

## Governance Model
- **Engineering Manager (Accountable):** delivery, quality gate enforcement, staffing, risk posture.
- **Tech Lead (Responsible):** architecture integrity, interface contracts, technical decision records.
- **Subsystem DRIs (Responsible):** planner, run engine, memory, safety, observability, evaluation harness.
- **Quality Gate Owners (Responsible):** test gate, policy gate, performance gate, release gate.
- **Product/Operations Stakeholders (Consulted/Informed):** acceptance and rollout readiness.

## Named Ownership Matrix (Required Before Phase 2 Execution)
| Function | Primary DRI | Secondary DRI | Response SLA | Escalation |
|---|---|---|---|---|
| Planner | Tech Lead delegate | Backup platform engineer | 4h business / 30m incident | Tech Lead -> EM |
| Run Engine | Runtime DRI | Backup runtime engineer | 4h business / 30m incident | Tech Lead -> EM |
| Safety and Policy | Safety Owner | Security backup | 1h incident | Safety Owner -> EM |
| Memory and Data | Data/Memory DRI | Backup data engineer | 4h business / 30m incident | Data/Memory DRI -> Tech Lead |
| Observability | Observability DRI | SRE backup | 30m incident | SRE/Operations Owner -> EM |
| Release Gate | SRE/Operations Owner | EM delegate | 30m incident | EM final decision |

## Decision Policy
- No milestone exits with unresolved critical defects, failed policy checks, or missing evidence.
- Gate waivers require explicit accountable owner, expiry date, and compensating controls.
- **Single** production promotion to the target environment only after canary SLO adherence and incident-free soak window.
- Release gate terminology and numeric thresholds are defined in `docs/implementation/2026-04-13-persona-agent-platform-release-gate-spec.md` and are authoritative across all implementation docs.

## Program Cadence
- Weekly planning and risk review.
- Midweek architecture and implementation checkpoint.
- End-of-week gate review with pass/block decisions.
- Monthly operating review on trend metrics and risk burndown.

## Dependencies and Preconditions
- Local inference environments (`Ollama`, `vLLM`) available and benchmarkable.
- Shared Postgres infrastructure with `pgvector` extension available.
- Baseline observability stack configured before high-volume test runs.
- Test harness and regression suite ownership assigned before **Phase 2** execution.

## Acceptance Rules for This Package
- All linked documents contain explicit owners and measurable exit criteria.
- No ambiguous phrases such as "later", "future", or "TBD" in required sections.
- Cross-document consistency between roadmap, gates, risks, and SLO thresholds.
- **Executable by any trained contributor:** implementation follows `docs/implementation/2026-04-13-persona-agent-platform-execution-playbook.md` reading order; manifest and gate packets are never optional artifacts.
