# Persona Agent Platform Implementation Roadmap (Single Production Exit)

## Program Goal
Deliver **one** production-ready persona agent platform in a **single exit**: all design outcomes, all workflows in the production inventory, and all production gates green. There is **no MVP**, **no partial production**, and **no calendar-driven ship date**. Phases below define **order and gate dependencies** only; duration is **however long is required** until exit criteria are met.

## Production Workflow Inventory (Scope Lock)
- **Source of truth:** every workflow derived from `docs/personas` and `docs/more_personas` that the compiler supports, enumerated in the version-controlled file **`docs/implementation/production-workflow-manifest.md`** (no implicit subset).
- **Frozen** means change-controlled (additions require manifest update, DOR, and gate re-evidence), not “reduced scope.”
- **SLOs and parity tests** apply to **100%** of manifest workflows unless a workflow is explicitly deferred with EM + Tech Lead signed exception (exceptions are rare, time-bound, and tracked in the risk register).

## Milestone Structure (Ordering, Not Shippable Slices)
Milestones are **integration checkpoints**, not separately releasable products. Production promotion happens **once**, after the final milestone and global exit criteria pass.

- **M1:** foundation and contract hardening  
- **M2:** orchestration and safety enforcement  
- **M3:** memory, evaluation, and reliability loop  
- **M4:** production hardening, single promotion, and operations handoff  

## Milestone Owners
- **M1 Owner:** Tech Lead  
- **M2 Owner:** Safety Owner  
- **M3 Owner:** Data/Memory DRI + Quality Owner (joint)  
- **M4 Owner:** SRE/Operations Owner  

## Milestones ↔ phases (normative crosswalk)
| Milestone | Phases | Integration focus |
|-----------|--------|-------------------|
| **M1** | 1 | Contracts, ADRs, approved manifest. |
| **M2** | 2–4 | Compiler, run engine + triad + tree search, safety/temporal. |
| **M3** | 5–7 | Memory, evaluation/stress/self-improvement, inference routing. |
| **M4** | 8–10 | Production-grade observability/replay, runtime API/CLI/scheduling, single production exit. |

**Normative detail:** `docs/implementation/2026-04-13-persona-agent-platform-doc-precedence.md` §11 duplicates this table for precedence ordering.

## Phase Plan (Gate-Gated)
### Phase 1 — Contracts and inventory
- Finalize architecture contracts and subsystem ownership.
- Establish Definition of Ready templates and gate evidence format.
- Triage **research** and **OSS** candidates from `docs/implementation/2026-04-13-persona-agent-platform-research-and-oss-integration.md` into ADRs (no dependency without owner and rollback).
- Produce and approve **`docs/implementation/production-workflow-manifest.md`** with at least one row per in-scope workflow (complete inventory).
- **Contributor path:** follow `docs/implementation/2026-04-13-persona-agent-platform-execution-playbook.md` (reading order, prerequisites, evaluator corner cases) so Phase 1 outputs match gate expectations.
- **Acceptance:** signed contracts + RACI + approved gate board checklist + approved manifest.

### Phase 2 — Compiler and CI gates
- Implement workflow compiler and typed step schema boundaries.
- Baseline CI quality gates (types, lint, core tests, schema checks).
- Pin and wire **DeepEval** (and **RAGAS** where retrieval is tested) for the first pytest LLM gate tests on compiler outputs or golden fixtures.
- **Acceptance:** compiler succeeds for **100%** of manifest workflows; blocking CI gates with deterministic outcomes; DeepEval-backed tests run in CI.

### Phase 3 — Run engine, triad, and tree-search planning
- Integrate LangGraph run engine with **`langgraph-checkpoint-postgres`** so checkpoints and memory share governed Postgres infrastructure.
- Add triad orchestration (`architect`, `implementer`, `reviewer`) per step.
- Use **Instructor** (with Pydantic models) for structured planner, reviewer, and tool-argument payloads at the triad boundary unless a step-specific ADR exempts it.
- Implement and integrate **`TreeSearchPlanner`** (LATS-style tree search over plan branches) with auditable branch selection and persistence hooks, per design spec.
- **Acceptance:** resumable execution on **every** manifest workflow; step transitions include gate state and reviewer decision output; planner outputs are recorded and replayable for gate and incident review.

### Phase 4 — Safety and temporal enforcement
- Add policy validator chain and temporal constraint enforcement.
- Integrate **openai-guardrails-python** for configurable input/output/tool guard pipelines where applicable; keep tenant, policy version pins, and temporal proofs in platform-owned code.
- **Acceptance:** unsafe or sequence-invalid actions are blocked pre-execution on the full manifest suite.

### Phase 5 — Memory and retrieval
- Build memory primitives: episodic, semantic, procedural, failure, and **generative** paths with promotion controls.
- Add hierarchical summaries and retrieval integration before planning/execution.
- Add ERL-style heuristic extraction from trajectories.
- **Acceptance:** reads/writes correct by memory class; retrieval + generative promotion rules pass benchmarks; heuristic injection improves held-out reliability metrics without safety regression.

### Phase 6 — Evaluation, stress, and self-improvement
- Stand up evaluation replay harness and trajectory metrics.
- Add **promptfoo** as the **default** prompt/policy regression and red-team harness (CI-blocking, artifacts stored per manifest mapping).
- Wire **agentevals** to consume **OpenTelemetry** exports for trace-based scoring on promotion and incident paths.
- Expand **DeepEval** / **RAGAS** suites for step- and memory-quality gates tied to the manifest.
- Add reliability stress harness (`pass^k`), perturbation tests, and injected tool/API failure tests.
- Add reflective prompt-policy evolution (GEPA-style) with versioned registry, held-out suite, and rollback (evaluated via promptfoo + agentevals + DeepEval).
- **Acceptance:** candidate evaluation runs without manual patching; stress suite runs in CI/nightly; prompt/policy promotion path is proven with non-regression gates.
- **Prerequisite:** **Baseline observability** per `docs/implementation/2026-04-13-persona-agent-platform-doc-precedence.md` §8 must be satisfied before high-volume stress evidence is accepted; **production-grade** observability per §8 of that file remains mandatory before Phase 10.

### Phase 7 — Inference routing and SLO-aware serving
- Implement adaptive inference routing across `Ollama` and `vLLM`.
- Tune SLO-aware speculative decoding under variable load.
- **Acceptance:** routing logged and benchmarked against latency/quality SLOs with load-profile evidence on manifest workflows.

### Phase 8 — Observability and replay (production-grade)
- Expand observability to production-grade coverage (replay hooks, incident dashboards, alert tuning, audit completeness).
- Optionally deploy **Langfuse** self-hosted if Observability DRI approves; primary signals remain **OpenTelemetry** + structured logs + **agentevals** on exported traces.
- **Acceptance:** incident replay and root-cause drill succeed in the validation environment with a drill matrix that covers each subsystem failure mode and includes **at least one successful replay trace per manifest workflow** (batched scheduling allowed; **no workflow gaps**).

### Phase 9 — Local runtime surface and autonomous scheduling
- Ship **local runtime API**, **CLI**, and **scheduling** for unattended autonomous operation (design implementation sequence).
- **Acceptance:** operators can start, pause, resume, and audit runs from the CLI/API; schedules execute with the same gates and observability as interactive runs; documented runbook for local operations.

### Phase 10 — Single production exit
- Release readiness: one canary window, rollback validation, ops handoff.
- **Acceptance:** all global production exit criteria and `docs/implementation/2026-04-13-persona-agent-platform-release-gate-spec.md` satisfied; rollback drill passed on the promoting artifact.

## Critical Path Dependencies
- Manifest approval (Phase 1) gates all downstream implementation.
- Safety and temporal checks (Phase 4) gate broader integration and promotion logic.
- Observability baseline (Phase 6 prerequisite; defined in `docs/implementation/2026-04-13-persona-agent-platform-doc-precedence.md` §8) gates acceptance of high-volume stress evidence.
- Observability production-grade coverage (Phase 8) is required before **Phase 10** (single production exit).
- Local runtime API/CLI/scheduling (Phase 9) is required before **Phase 10** (single production exit).

## Production Exit Criteria (Program Complete)
- Full gate-based execution with evidence artifacts for **100%** of the production workflow manifest.
- Gate packets include **promptfoo** results, **agentevals** trace scores (where traces exist), and **DeepEval** (± **RAGAS**) outputs mapped to the manifest per `docs/implementation/2026-04-13-persona-agent-platform-delivery-process.md`.
- **All design done criteria** in `docs/superpowers/specs/2026-04-13-persona-agent-platform-design.md` are satisfied with evidence (including tree-search planning, governed generative memory, prompt-policy evolution, local API/CLI/scheduling, and no-repeat-failure behavior).
- Reliability stress suite stable with no critical regressions in two consecutive runs.
- No unresolved critical risks in the risk register.
- Release and rollback operations validated by owners on the artifact that promotes.
- **All** manifest workflows pass production gates on both local backends (`Ollama` and `vLLM`) with published evidence packets.
- Generative memory and prompt-policy evolution paths are **live under governance** (not deferred to a “phase 2 product”): shadow and promotion rules are implemented, audited, and meet safety non-regression gates.
- **No-repeat-failure contract:** a normalized critical failure signature cannot pass **twice** without retrieval, reviewer challenge, or an automated prevention check firing (see release gate spec for signature schema ownership).
