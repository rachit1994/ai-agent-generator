# AI Professional Evolution System - CTO Architecture Blueprint

**In plain words:** This repo is both a **big design** for a professional-grade “AI engineering organization” and a **small, runnable tool** (`sde`) that already runs tasks and writes proof to disk. The **Markdown in `docs/`** says what “good” means; the **Python in `src/`** implements the **early** slices. Later stages (roughly **V4–V7**) are often **specified first** so code can catch up without guessing.

This repository still holds the **full production architecture** story: local-first, event-sourced, policy-governed operation — with agents treated as **junior contributors** who need **process, review, and evidence**, not a single chat transcript.

**Where to start (pick one):**

- **Words first, no code yet:** `docs/onboarding/start-here-reading-the-docs.md`
- **Code tree first:** `docs/onboarding/start-here-reading-the-code.md`
- **Engineer path:** `docs/onboarding/developer-walkthrough.md` then `docs/README.md`

Primary sources of truth:
- `docs/architecture/AI-Professional-Evolution-Master-Architecture.md` — **full platform** blueprint (long; use as reference).
- `docs/onboarding/action-plan.md` — **what we are building toward** and **in what order** (V1–V7 as **one** roadmap; **safety before** shortcuts).
- `docs/architecture/architecture-goal-completion.md` — **what “all specs done” does and does not mean** next to the master doc.

Supporting docs (implementation and specs):
- `docs/onboarding/start-here-reading-the-docs.md` — **gentle** glossary and reading order.
- `docs/onboarding/start-here-reading-the-code.md` — **where files live** and what is runnable vs planned.
- `docs/onboarding/developer-walkthrough.md` — **hands-on** map: CLI, `outputs/`, tests, safe changes.
- `docs/architecture/operating-system-folder-structure.md` — **target** folder tree for the full OS; compares to this repo.
- `docs/architecture/swarm-token-and-system-requirements-math.md` — **budgets and sizing** math for swarms and hardware.
- `docs/coding-agent/execution.md` — **V1:** what each run must **write** and which **checks (HS01–HS06)** must pass.
- `docs/coding-agent/planning.md` — **V2:** plan and docs **before** big coding; learning log; **HS07–HS12**.
- `docs/coding-agent/completion.md` — **V3:** small steps, reviews, tests, “done” definition; **HS13–HS16**.
- `docs/coding-agent/events.md` — **V4:** append-only **event log** and replay; **HS17–HS20**.
- `docs/coding-agent/memory.md` — **V5:** governed **memory** across runs; **HS21–HS24**.
- `docs/coding-agent/evolution.md` — **V6:** reflection, practice, promotion, canary; **HS25–HS28**.
- `docs/coding-agent/organization.md` — **V7:** **many agents**, permissions, leases; **HS29–HS32**.
- `docs/README.md` — **map of all docs** and cumulative hard-stop index.
- `docs/research/self-improvement-research-alignment.md` — **papers → our specs** (never overrides V1).
- `docs/sde/pipeline-plan.md` — **order of work** to ship the execution slice.
- `docs/sde/multi-agent-build.md` — **who owns which module** for multi-role delivery.
- `docs/templates/sde-demo/` — **copy-paste seed** for local demos under gitignored `demo_apps/`

---

# 1. Executive Objective

Build an AI Professional Operating System that enables:
- autonomous execution,
- autonomous learning,
- autonomous promotion,
- autonomous career strategy,
- multi-agent organizational growth.

All behavior must remain:
- deterministic,
- replayable,
- auditable,
- safe under long-horizon operation.

---

# 2. Why This System Exists

Most agent systems fail at long-term growth because they:
- optimize one-off task quality over capability trajectory,
- treat memory as cache instead of governed institutional knowledge,
- lack lifecycle promotion governance,
- cannot causally explain behavior change.

This architecture solves those gaps with explicit contracts, governance, and closed-loop evolution.

---

# 3. Core Design Principles

- Professional evolution is the product.
- Event-sourced lineage is mandatory.
- Autonomy is policy-gated and reversible.
- Deterministic evaluation is required for high-impact change.
- `local-prod` is the only production runtime profile.
- Objective arbitration across safety/quality/velocity/autonomy is explicit and machine-enforced.

---

# 4. Human Professional Evolution Model

Canonical growth loop:

`Task -> Execution -> Review -> Metrics -> Reflection -> Learning Update -> Deliberate Practice -> Capability Delta -> Next Task`

Career progression:

`New -> Junior -> Mid-level -> Senior -> Architect -> Manager/Specialist`

Human-to-agent mapping includes:
- mentorship operating model,
- performance review cycle contract,
- deliberate practice capacity protection,
- institutional memory.

---

# 5. Agent Organization and Roles

Execution roles:
- `JuniorAgent`, `MidLevelAgent`, `SeniorAgent`, `ArchitectAgent`, `SpecialistAgent`

Governance and learning roles:
- `ReviewerAgent`, `EvaluatorAgent`, `LearningAgent`, `PracticeAgent`, `ManagerAgent`

Strategy role:
- `CareerStrategyAgent`

Critical constraints:
- no self-approval for promotion or autonomy increases,
- all handoffs are schema-validated,
- single-writer task ownership via lease + heartbeat.

---

# 6. Lifecycle and Promotion Governance

Lifecycle:

`NewAgent -> JuniorAgent -> MidLevelAgent -> SeniorAgent -> ArchitectAgent -> SpecialistAgent|ManagerAgent`

Promotion requires:
- capability prerequisites,
- sustained reliability windows,
- replay-verifiable lineage evidence,
- independent committee signal,
- probation completion.

System includes:
- demotion rules,
- promotion rollback during probation,
- recertification for high-risk capabilities,
- stagnation detection and intervention ladder.

---

# 7. Capability Model

Capability graph:
- nodes = atomic capabilities,
- edges = prerequisite dependencies,
- maturity levels = `L0..L5`.

Scoring combines:
- outcomes,
- review quality,
- regression behavior,
- transfer performance.

High-risk capabilities use:
- decay,
- recertification,
- dependency-aware promotion limits.

---

# 8. Memory Architecture

Memory classes:
- episodic,
- semantic,
- skill/procedural.

Policy model:
- write/defer/discard/retrieve-more actions,
- provenance and confidence requirements,
- contradiction quarantine,
- safety-gated writes.

Lifecycle:
- hot/warm/cold tiers,
- compaction and retention controls,
- memory quality metrics and harmful-noise tracking.

---

# 9. Learning and Evolution Engine

Learning loop:

`Episode -> Reflection -> Lesson Proposal -> Validation -> Approved Update -> Practice -> Capability Verification`

Mandatory controls:
- causal closure proof for durable updates,
- rollback-ready learning updates,
- policy-gated canary rollout,
- protected learning/practice capacity.

---

# 10. Workflow Pipelines

Production pipeline:

`Task -> Execution -> Review -> Evaluate -> Learn -> Practice -> Promote`

Strategy overlay:

`CareerStrategy -> TaskPortfolioPlanning -> Production Pipeline`

State machines are explicit for:
- task execution,
- learning update rollout,
- incident recovery.

Retry, failure, and improvement loops are reason-coded and bounded.

---

# 11. Guardrails and Safety

Safety controls include:
- dual control for irreversible actions,
- severity-based review gating,
- risk-tier permission matrix,
- rollback-first operations,
- objective constraints that never trade safety for speed.

`SafetyController` retains final veto authority.

---

# 12. Event-Sourced Backbone

Event store is immutable and append-only, with:
- monotonic sequencing,
- idempotency semantics,
- replay fail-closed behavior,
- hash-chain integrity,
- mandatory lineage:
  `event -> reflection -> update -> evaluation -> rollout`.

---

# 13. Evaluation and Success Criteria

Evaluation layers:
- offline replay,
- online shadow/canary,
- regression,
- promotion evaluation.

Core hard gates:
- `CriticalRegressionCount == 0`
- `UnsafeActionRate <= 0.02`
- `ReplayCriticalDriftCount == 0`
- `RollbackDrillPass == true`
- `ResourceBudgetBreaches == 0`

---

# 14. Production Architecture (`local-prod`)

Runtime and infrastructure:
- deterministic Python-first execution runtime,
- federated orchestration,
- Postgres event store + projections,
- local vector-backed retrieval,
- identity/authz plane with scoped high-risk approvals,
- observability stack with replay and lineage visualization.

No cloud dependency in critical loops.

---

# 15. Component and Service Architecture

The master architecture defines five planes:
- control,
- data,
- learning,
- evaluation/safety,
- operations.

Major services include:
- `orchestrator`,
- `objective-policy-engine`,
- `lifecycle-governance`,
- `identity-authz`,
- `policy-management`,
- `memory-lifecycle`,
- `canary-rollout`,
- `evaluation`,
- `quota-scheduler`,
- `model-router`,
- `incident-ops`,
- `chaos-simulator`.

---

# 16. Repository Structure

Canonical OS-style structure is defined in:
- `docs/architecture/operating-system-folder-structure.md`

In **this** repository, `src/` is intentionally **flat** (`orchestrator` + `sde_*` packages only); empty scaffold folders from the master diagram are omitted until implemented — see the “This repository” section in the doc above.

Key roots (master vision):
- `contracts/` (versioned schemas),
- `services/` (extraction-ready service units),
- `agents/` (role executors),
- `runtime/` (deterministic worker + local-prod profile),
- `libraries/`, `data/`, `infra/`, `tests/`, `tools/`.

Non-bypass ownership rules:
- only `memory-lifecycle` mutates memory,
- only `lifecycle-governance` changes promotion/autonomy state,
- only `policy-management` activates policy bundles,
- only `safety-controller` issues final high-risk veto,
- only `identity-authz` issues scoped approval tokens.

---

# 17. Contract Closure Requirements

Mandatory contract additions include:
- objective arbitration contract,
- common service RPC contract,
- orchestration hierarchy contract,
- deadlock detection/recovery contract,
- deterministic worker contract,
- policy bundle governance contract.

CI and runtime admission are fail-closed for contract violations.

---

# 18. Security Hardening

Production security requirements:
- cryptographic workload identity,
- deny-by-default ABAC+RBAC authorization,
- prompt-injection/jailbreak containment gateway,
- tool firewall with strict argument validation,
- trust-channel mTLS + anti-replay controls,
- threshold-signed policy activation,
- centralized short-lived secret management.

Security release gates are mandatory and binary.

---

# 19. Reliability and Resilience

Critical reliability closure:
- learning rollback contract,
- promotion cascade breaker,
- memory poisoning sentinel,
- policy drift contract,
- binary release gate engine.

Operational discipline:
- runbook-grade incident flows,
- signed evidence bundles,
- chaos qualification per release window,
- reliability SLO/SLA targets with promotion/autonomy freeze on breach.

---

# 20. Scalability and Performance

Scaling model includes:
- hierarchical compute quota scheduling,
- protected learning/practice capacity,
- model routing with bounded fallback attempts,
- circuit-breakers and budget caps,
- replay window/snapshot strategy,
- memory/event growth thresholds,
- mandatory KPI dashboards.

Performance release thresholds are binary and fail-closed.

---

# 21. Swarm Budget and System Requirement Math

Quantitative planning model is defined in:
- `docs/architecture/swarm-token-and-system-requirements-math.md`

It provides:
- balanced utility function (equal quality/cost effectiveness),
- token throughput and spend math,
- protected budget floors for safety/evaluation/learning,
- local-prod CPU/RAM/disk/network sizing formulas,
- SLO-aligned operating envelopes.

---

# 22. Full Build Order (Not MVP)

Stages:
- A: Foundations and contract freeze
- B: Deterministic runtime + identity core
- C: Event/projection/observability backbone
- D: Orchestration hierarchy and deadlock safety
- E: Capability and lifecycle governance
- F: Memory governance and defense
- G: Learning causal-closure + canary rollback
- H: Evaluation/resilience/security hardening
- I: Curriculum and cold-start acceleration
- J: Long-horizon evolution and federation readiness

Production claim requires Stage A-H completion with evidence.

---

# 23. Production Readiness Program

Readiness program requires:
- single execution tracker with owner/approver/evidence fields,
- weighted 100-point scoring model,
- P0/P1 score caps until closure,
- weekly governance cadence and decision logs,
- two consecutive all-green windows for 100/100 claim.

Hard program gates:
- `OpenP0 == 0`
- `OpenP1 == 0`
- release gates from architecture Sections 14 and 26 pass,
- lineage completeness = 100% for promotion/autonomy decisions.

---

# 24. What "Production-Grade 100/100" Means Here

A valid 100/100 claim means:
- architecture is fully implemented (not only documented),
- all contract, security, reliability, and performance gates pass,
- evidence artifacts are complete and auditable,
- rollout/rollback operations are proven via drills and replay.

If any hard gate fails, production claim is automatically blocked.

---

# 25. Document Index

Primary architecture:
- `docs/architecture/AI-Professional-Evolution-Master-Architecture.md`

Implementation structure:
- `docs/architecture/operating-system-folder-structure.md`

Capacity and budget planning math:
- `docs/architecture/swarm-token-and-system-requirements-math.md`

---

End of README.
