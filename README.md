# Persona Agent Platform

## North star (read this first)

We are building **one** integrated system: **persona agents** that run **locally by default**, follow **typed workflows** compiled from your persona library, pass **machine-checkable quality and safety gates**, use **long-lived memory** (including failure memory so the same class of mistake is harder to repeat), and participate in a **governed self-improvement loop** (eval → promote or demote → audit — not “vibes” or silent prompt edits).

Production readiness is defined **up front**: we ship **only after** a **single**, evidence-backed promotion when **every** workflow listed in the production manifest is proven end-to-end — **including** on **both** inference backends we support (**Ollama** and **vLLM**). There is **no** “MVP in prod” or “we will finish the rest later” branch of the program.

---

## What you are trying to achieve (outcomes)

When the program reaches **production exit**, a reader should be able to verify all of the following — with **links, packets, and sign-offs**, not narrative:

- **Inventory honesty:** Every shipped persona workflow is listed in `docs/implementation/production-workflow-manifest.md`; the manifest is the same full set as release SLO scope (**no hidden side lists**).
- **Compile-time and runtime contracts:** Personas compile to **stable `workflow_id`s and step schemas**; steps run through an **architect → implementer → reviewer** triad with **validators and temporal rules before tools execute**.
- **Memory that behaves:** Reads and writes for episodic, semantic, procedural, failure, and **governed** generative memory follow the design’s write rules; retrieval is ordered correctly relative to planning and execution.
- **Quality is continuous:** CI and scheduled suites cover **stress, regression, and red-team** paths; **OpenTelemetry** traces feed **agentevals** where required; **promptfoo**, **DeepEval**, and **RAGAS** (where RAG is in scope) block sloppy merges when you wire them as blockers.
- **Inference parity:** Routing, speculative decoding, and load are real concerns — improvements must still hold when switching between **Ollama** and **vLLM**, with **parity evidence** captured for reviewers.
- **Operate and learn without heroics:** API, CLI, and schedules exist so runs are **repeatable and auditable**; improvement (memory lanes, prompts/policies) is **versioned, gated, and reversible**.

---

## How we get there (method, not calendar)

Work is organized as **Phases 0–10** and milestones **M1–M4** in the implementation roadmap. Phases are **dependencies and ordering**, not a promise to finish a phase per week: **time is not traded for shrinking scope**.

At a glance:

| Stage | Plain-English intent |
|-------|----------------------|
| **Phase 0** | Machines, lockfiles, Postgres + pgvector, CI can run the toolchains (pytest, DeepEval, OTel export, promptfoo); **owners** named for harness and observability. |
| **Phase 1** | Contracts, manifest rows, RACI, gate templates — **who** may change what, and **what evidence** reviewers expect. |
| **Phase 2** | **Compiler**: every manifest workflow compiles to typed steps; CI blocks schema and quality regressions. |
| **Phases 3–5** | **Runtime + tree search + checkpoints**, then **safety and time ordering**, then **memory** — the substrate that makes “learning” traceable instead of a blob of logs. |
| **Phases 6–7** | **Eval + stress + improvement flywheel**, then **routing and decoding** under SLOs — learning must survive real local operation. |
| **Phases 8–10** | **Observability and replay**, **operator surfaces** (API/CLI/schedule), then **one** promotion with soak, rollback proof, and **immutable gate packets**. |

**Single checklist** that folds in roadmap, playbook, delivery process, release gate spec, and design “done” language:  
`docs/implementation/2026-04-13-persona-agent-platform-phased-checklist.md`

**Doc conflicts:**  
`docs/implementation/2026-04-13-persona-agent-platform-doc-precedence.md` wins after this README for literals, parity math, `agentevals` floors, observability boundaries, and gate packet rules.

---

## What we are doing differently

Typical agent projects optimize for a **demo**: one happy path, one model, best-effort prompts, and “we will add tests later.” This program optimizes for **defensible production** and **continuous improvement without silent risk**:

- **No partial production:** One promotion window; **100%** of manifest workflows must pass the agreed gates; **no MVP** carve-out that leaves part of the library unproven.
- **Manifest-driven truth:** If it is not in `docs/implementation/production-workflow-manifest.md` with evidence, it does not count toward “done.” **Zero rows ⇒ no 100% manifest claims.**
- **Evidence-first culture:** Gate packets, immutable URLs, dashboard links, pinned tool versions, and **named verifiers** — see the **Evidence bar** after each phase in the phased checklist — so “phase complete” is **reviewable**, not a status meeting opinion.
- **Learning is a closed loop, not a feature flag story:** Signals from runs → stored memory and metrics → **governed** changes to prompts/policies/memory → **measured** non-regression → **demotion** when something regresses; safety and temporal rails are **never** bypassed to ship a heuristic.
- **Dual-backend discipline:** “Works on my laptop model” is insufficient; **Ollama** and **vLLM** parity (and documented dimensions: pins, hardware class, bundles) is part of the honesty model.
- **Local-first, enterprise-grade bar:** Default posture is **local** operation with the same rigor you would expect from controlled rollout: SLOs, soak, rollback drills, waivers rules, and subsystem ownership.

---

## Delivery model (non-negotiable)

- **One shot to production:** a **single** production exit when **all** design outcomes and **100%** of the **production workflow manifest** pass gates. **No MVP** and **no partial production**.
- **Time is not a constraint for scope:** the program continues until exit criteria are satisfied; phases in the roadmap are **ordering and dependencies**, not calendar commitments.
- **`critical_workflows` (SLOs)** and the **production workflow manifest** are the **same full set**; see `docs/implementation/2026-04-13-persona-agent-platform-release-gate-spec.md`.

---

## First-time execution (read this if you are new to the program)

Phase 0 checklist step **5** requires this order **before** treating other implementation docs as authoritative:

1. Read **`README.md` (this file)** for program summary and non-negotiables — at minimum **North star**, **What you are trying to achieve**, **How we get there**, **What we are doing differently**, **Delivery model**, **First-time execution**, and **Project documents**.
2. Read `docs/implementation/2026-04-13-persona-agent-platform-doc-precedence.md` — **single source of truth** for conflicts, literals, failure-signature hashing, `agentevals` floors, observability phase boundaries, and persona-library contract scope.
3. Open `docs/implementation/2026-04-13-persona-agent-platform-execution-playbook.md` and follow **Read in this order (do not skip)** and the **corner-case** table literally (items 1–13; playbook item 1 is this README).
4. Keep `docs/implementation/production-workflow-manifest.md` current (column literals and inventory rules are defined there and in doc-precedence). **Zero data rows ⇒ no “100% manifest” claims.**

---

## Core libraries and runtime stack

### Orchestration and agent runtime

- Python 3.13+
- LangGraph (workflow state machine and checkpoints) with **`langgraph-checkpoint-postgres`** for durable checkpoints on Postgres
- AutoGen AgentChat (step-level triad: architect, implementer, reviewer)
- **Instructor** for structured planner, reviewer, and tool-argument outputs aligned to Pydantic

### Inference and routing

- LiteLLM (model abstraction and routing)
- Ollama (local model serving)
- vLLM (high-performance local serving)

### Contracts, memory, and data

- Pydantic v2 (strict schema contracts)
- Postgres + pgvector (episodic, semantic, procedural, failure, and governed generative memory)

### Observability and evaluation

- OpenTelemetry (traces and metrics) as the **required** export path
- Structured logging (audit and replay diagnostics)
- **agentevals** for default scoring from OTel traces (promotion and incident workflows)
- **promptfoo** for default prompt and policy regression CI
- **DeepEval** and **RAGAS** (where semantic memory is tested as RAG) for pytest quality gates
- Optional self-hosted **Langfuse** for trace UX and datasets when Observability DRI approves (does not replace OTel)
- Optional TruLens-compatible instrumentation (non-gating for production exit if core OTel evidence is complete)

### Safety and guardrails

- **openai-guardrails-python** as the default pipeline pattern for input/output/tool checks that fit the library; tenant scope, policy version pins, and temporal proofs remain platform-owned.

### Optional / ADR-gated OSS (see integration doc)

- **Graphiti** (temporal knowledge graph) and **Mem0** (memory API layer) only when an ADR selects them; **Letta** patterns for reference. Full paper lists and license notes: `docs/implementation/2026-04-13-persona-agent-platform-research-and-oss-integration.md`.

---

## Research foundations (with citations)

The design and quality model are informed by recent research and production-oriented benchmarks:

- **Experiential Reflective Learning (ERL)** for trajectory reflection and reusable heuristics: [arXiv:2603.24639](https://arxiv.org/abs/2603.24639)
- **ReliabilityBench** for reliability stress testing (`pass^k`, perturbation, fault injection): [arXiv:2601.06112](https://arxiv.org/abs/2601.06112)
- **MemGen** for generative memory beyond retrieval-only patterns: [arXiv:2509.24704](https://arxiv.org/abs/2509.24704)
- **AdaSpec** for SLO-aware adaptive speculative decoding in serving: [arXiv:2503.05096](https://arxiv.org/abs/2503.05096)
- **SpecRouter** for adaptive multi-level speculative routing (research-watch): [arXiv:2505.07680](https://arxiv.org/abs/2505.07680)
- **GEPA / prompt evolution direction** via DSPy optimizers: [DSPy Optimizers](https://dspy.ai/learn/optimization/optimizers)

**Extended bibliography (2024–Apr 2026) and planned OSS stack:** `docs/implementation/2026-04-13-persona-agent-platform-research-and-oss-integration.md`

---

## Production quality model

- No milestone exits with failed critical gates.
- Safety checks run before tool execution (input/action/output + temporal constraints).
- Reliability must be validated under repeated-run and fault conditions, not only single-run pass rate.
- **One** promotion window requires SLO-compliant canary behavior and rollback readiness.

---

## Project documents

- Documentation precedence and zero-gap norms: `docs/implementation/2026-04-13-persona-agent-platform-doc-precedence.md`
- Plain-English phased checklist (all steps): `docs/implementation/2026-04-13-persona-agent-platform-phased-checklist.md`
- Base system design: `docs/superpowers/specs/2026-04-13-persona-agent-platform-design.md`
- Master implementation plan: `docs/implementation/2026-04-13-persona-agent-platform-master-plan.md`
- Tech decisions: `docs/implementation/2026-04-13-persona-agent-platform-tech-decisions.md`
- Delivery process: `docs/implementation/2026-04-13-persona-agent-platform-delivery-process.md`
- Implementation roadmap: `docs/implementation/2026-04-13-persona-agent-platform-implementation-roadmap.md`
- Risk register: `docs/implementation/2026-04-13-persona-agent-platform-risk-register.md`
- Metrics and SLOs: `docs/implementation/2026-04-13-persona-agent-platform-metrics-and-slos.md`
- Quality/self-improvement advancements: `docs/implementation/2026-04-13-persona-agent-platform-quality-self-improvement-advancements.md`
- Release gate specification: `docs/implementation/2026-04-13-persona-agent-platform-release-gate-spec.md`
- Research bibliography and OSS integration: `docs/implementation/2026-04-13-persona-agent-platform-research-and-oss-integration.md`
- Execution playbook (reading order, glossary, corner cases): `docs/implementation/2026-04-13-persona-agent-platform-execution-playbook.md`
- Production workflow manifest (inventory template): `docs/implementation/production-workflow-manifest.md`

---

## High-level architecture

1. Persona specs are compiled into typed workflow steps.
2. A planner generates/updates execution trajectories.
3. The step triad collaborates per step under validator gates.
4. Memory retrieval occurs before planning and execution.
5. Policy and temporal constraints gate tool actions.
6. Observability + evaluation loops drive safe continuous improvement.

---

## Current scope

- **Full** production program aligned to the design spec and production workflow manifest.
- Quality-first and self-improving agent behavior (including governed generative memory and prompt-policy evolution as part of production exit).
- Local-first runtime with dual backend support (`Ollama` + `vLLM`).

---

## Next steps

- Phase 0 machine evidence (Python 3.13 lockfile, Postgres+pgvector, CI pytest/DeepEval/OTel/promptfoo): `docs/implementation/phase-0-developer-runbook.md`.
- Phase 0 checklist item **3** (Ollama + vLLM HTTP reachability on evidence hosts): `./scripts/verify_phase0_inference_backends.sh` (optional URL overrides `PHASE0_OLLAMA_TAGS_URL`, `PHASE0_VLLM_MODELS_URL` — see the runbook).
- Execute `docs/implementation/2026-04-13-persona-agent-platform-implementation-roadmap.md` until production exit.
- Integrate reflective heuristics, generative memory promotion paths, and promotion-safe prompt policy evolution under the single release gate spec.
