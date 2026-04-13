# Persona Agent Platform

## What We Are Building
We are building a **production-ready, local-first persona agent platform** that compiles persona definitions into autonomous workflows with strict quality gates, safety guardrails, long-term memory, and continuous self-improvement loops.

The platform is designed to:
- run locally by default,
- enforce machine-checkable step acceptance criteria,
- prevent repeated failures through failure-memory retrieval,
- and improve over time with trajectory-based evaluation and reflective optimization.

## Delivery Model (Non-Negotiable)
- **One shot to production:** a **single** production exit when **all** design outcomes and **100%** of the **production workflow manifest** pass gates. **No MVP** and **no partial production**.
- **Time is not a constraint for scope:** the program continues until exit criteria are satisfied; phases in the roadmap are **ordering and dependencies**, not calendar commitments.
- **`critical_workflows` (SLOs)** and the **production workflow manifest** are the **same full set**; see `docs/implementation/2026-04-13-persona-agent-platform-release-gate-spec.md`.

## First-time execution (read this if you are new to the program)
1. Open `docs/implementation/2026-04-13-persona-agent-platform-execution-playbook.md` and follow the **reading order** and **corner-case** table literally.
2. Maintain the live inventory in `docs/implementation/production-workflow-manifest.md` (template explains columns). **No manifest rows ⇒ no “100% manifest” claims.**

## Core Libraries and Runtime Stack
### Orchestration and Agent Runtime
- Python 3.13+
- LangGraph (workflow state machine and checkpoints) with **`langgraph-checkpoint-postgres`** for durable checkpoints on Postgres
- AutoGen AgentChat (step-level triad: architect, implementer, reviewer)
- **Instructor** for structured planner, reviewer, and tool-argument outputs aligned to Pydantic

### Inference and Routing
- LiteLLM (model abstraction and routing)
- Ollama (local model serving)
- vLLM (high-performance local serving)

### Contracts, Memory, and Data
- Pydantic v2 (strict schema contracts)
- Postgres + pgvector (episodic, semantic, procedural, failure, and governed generative memory)

### Observability and Evaluation
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

## Research Foundations (With Citations)
The design and quality model are informed by recent research and production-oriented benchmarks:

- **Experiential Reflective Learning (ERL)** for trajectory reflection and reusable heuristics: [arXiv:2603.24639](https://arxiv.org/abs/2603.24639)
- **ReliabilityBench** for reliability stress testing (`pass^k`, perturbation, fault injection): [arXiv:2601.06112](https://arxiv.org/abs/2601.06112)
- **MemGen** for generative memory beyond retrieval-only patterns: [arXiv:2509.24704](https://arxiv.org/abs/2509.24704)
- **AdaSpec** for SLO-aware adaptive speculative decoding in serving: [arXiv:2503.05096](https://arxiv.org/abs/2503.05096)
- **SpecRouter** for adaptive multi-level speculative routing (research-watch): [arXiv:2505.07680](https://arxiv.org/abs/2505.07680)
- **GEPA / prompt evolution direction** via DSPy optimizers: [DSPy Optimizers](https://dspy.ai/learn/optimization/optimizers)

**Extended bibliography (2024–Apr 2026) and planned OSS stack:** `docs/implementation/2026-04-13-persona-agent-platform-research-and-oss-integration.md`

## Production Quality Model
- No milestone exits with failed critical gates.
- Safety checks run before tool execution (input/action/output + temporal constraints).
- Reliability must be validated under repeated-run and fault conditions, not only single-run pass rate.
- **One** promotion window requires SLO-compliant canary behavior and rollback readiness.

## Project Documents
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

## High-Level Architecture
1. Persona specs are compiled into typed workflow steps.
2. A planner generates/updates execution trajectories.
3. The step triad collaborates per step under validator gates.
4. Memory retrieval occurs before planning and execution.
5. Policy and temporal constraints gate tool actions.
6. Observability + evaluation loops drive safe continuous improvement.

## Current Scope
- **Full** production program aligned to the design spec and production workflow manifest.
- Quality-first and self-improving agent behavior (including governed generative memory and prompt-policy evolution as part of production exit).
- Local-first runtime with dual backend support (`Ollama` + `vLLM`).

## Next Steps
- Execute `docs/implementation/2026-04-13-persona-agent-platform-implementation-roadmap.md` until production exit.
- Stand up baseline CI gates and reliability stress harness.
- Integrate reflective heuristics, generative memory promotion paths, and promotion-safe prompt policy evolution under the single release gate spec.
