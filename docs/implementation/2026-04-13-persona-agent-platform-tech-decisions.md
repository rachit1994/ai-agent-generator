# Persona Agent Platform Technology Decisions (Production)

## Decision Framework
Selection criteria:
- deterministic workflow orchestration,
- strong typed contracts and validation,
- local-first inference support with routing flexibility,
- robust observability and replay,
- operational clarity for a **single** production exit (no MVP).

## Production workflow manifest
- Canonical inventory path: **`docs/implementation/production-workflow-manifest.md`**. All references to “100% of manifest” mean **every populated row** in that file at the release commit.

## Research and OSS source of truth
- Curated **papers (2024–Apr 2026)** and **OSS** split into **planned baseline** vs **optional**: `docs/implementation/2026-04-13-persona-agent-platform-research-and-oss-integration.md`.
- Swapping a **planned baseline** dependency requires a Tech Lead ADR and updated gate evidence; **optional** dependencies require ADR or Observability DRI approval as listed in that doc.

## Final Stack
### Workflow and Agent Orchestration
- **LangGraph** for stateful workflow orchestration with checkpoints and resumability.
- **`langgraph-checkpoint-postgres`** for **all** durable LangGraph checkpoints on the **same Postgres** cluster as memory (dedicated schema or tables; pooled connections).
- **AutoGen AgentChat** for step-level triad collaboration (`architect`, `implementer`, `reviewer`).
- **`TreeSearchPlanner` (LATS-style)** for auditable multi-branch planning before execution-heavy steps, integrated with the run engine and checkpoints.

Rationale:
- LangGraph gives deterministic state transitions and persistence-friendly execution flow.
- AutoGen triad aligns directly with the persona execution contract in the base spec.
- Tree search addresses long-horizon reliability called out in the base design.

### Model Routing and Inference
- **LiteLLM** for unified model client and backend routing policy.
- **Ollama** and **vLLM** as co-equal local backends.
- Adaptive routing and speculative decoding policy managed in inference control layer.

Rationale:
- Preserves local runtime flexibility while preventing hard backend lock-in.
- Supports latency/quality trade-offs under explicit SLO controls.

### Contracts and Validation
- **Pydantic v2** for typed request/response contracts and schema validation.
- **Instructor** for **default** structured LLM outputs (planner, reviewer, typed tool arguments) with validation retries; bypass only per-step ADR.
- Validator chain for input, action, output, and temporal checks.

Rationale:
- Strong runtime type safety and predictable integration boundaries.
- Easier machine-checkable acceptance criteria at step gates.

### Memory and Storage
- **Postgres + pgvector** for durable episodic, semantic, procedural, failure, and **generative** memory with explicit promotion rules and tenant isolation.
- **Graphiti** (optional, Apache-2.0) only when Phase 1 ADR selects Postgres + temporal graph; **Mem0** (optional) only with ADR naming Postgres as system of truth—see research/OSS doc.
- Hierarchical summaries for long-horizon memory compaction.

Rationale:
- Production-ready relational durability plus semantic retrieval in one platform.
- Generative memory is **in scope for production exit**, delivered through a governed promotion ladder (shadow → eval → canary → active), not deferred as a “phase 2 product.”

### Observability and Evaluation
- **OpenTelemetry** for traces/metrics foundation (required export path for all runs).
- Structured logs for auditable run diagnostics.
- **promptfoo** for **all** prompt and policy regression and red-team suites in CI; gate packets include promptfoo artifacts for promotion.
- **agentevals** for **default** scoring from OTel traces (promotion, soak review, incident triage without full re-run where sufficient).
- **DeepEval** for **default** pytest-bound LLM quality gates; **RAGAS** metrics wherever semantic memory is validated as RAG.
- **Langfuse** (MIT core, self-hosted) **optional**: Observability DRI may enable for trace UX, datasets, and experiments; never replaces OTel requirement.
- **openai-guardrails-python** as the **default** guardrail configuration and pipeline pattern for input/output/tool checks that fit the library model; tenant, policy version, and temporal proofs remain platform-owned.
- Regression replay and policy/prompt promotion workflows are implemented **through** promptfoo + agentevals + DeepEval so evidence stays **repeatable and CI-blocking**.
- `TruLens` compatibility remains optional when it does not duplicate required OTel evidence.

Rationale:
- Required for confidence in autonomous behavior and release readiness.
- Enables gate-level evidence collection and post-incident analysis.

## Alternatives Considered
- Single-agent orchestration without triad roles: rejected due to weaker quality gate independence.
- Proprietary hosted-only inference backend: rejected due to local-first requirement and cost control.
- Vector DB only memory layer: rejected due to insufficient transactional and governance controls.

## Constraints
- Local inference hardware variability can affect benchmark consistency.
- `vLLM` and speculative decoding tuning requires guarded rollout to avoid quality regressions.
- Cross-backend behavior parity must be measured continuously, not assumed.
- Reflective prompt evolution techniques can overfit without a held-out reliability suite.

## Environment Parity Contract (Release Blocking)
- Parity dimensions tracked per candidate:
  - backend (`ollama`, `vllm`),
  - pinned model/version and quantization profile,
  - hardware class (dev-laptop, CI-runner, canary-node, prod-node),
  - runtime versions (Python, LiteLLM, LangGraph, AutoGen),
  - prompt-policy and validator bundle versions,
  - **promptfoo** suite revision (or config hash) and pinned **agentevals** / **DeepEval** versions used for gate evidence.
- Release-blocking parity checks:
  - no critical safety divergence across backend pair on release corpus,
  - gate outcome parity >= 99% across backends on **100%** of the production workflow manifest,
  - p95 latency delta between canary and baseline <= 20%,
  - memory retrieval parity top-k overlap >= 0.90 on seeded replay set.

## Quality and Self-Improvement Techniques (Adoption Decision)
- **Adopt now (production exit):** trajectory-reflection heuristics (ERL-style), reliability stress tests (`pass^k`, perturbations, fault injection), SLO-aware speculative decoding tuning, **generative latent memory (MemGen-style) with promotion governance**, and **reflective prompt evolution (GEPA-style)** with versioned registry, held-out suites, and rollback.
- **Controlled rollout (still required before exit):** capabilities that must ship behind flags and pass the same promotion ladder before being enabled in the **production** configuration counted for exit (documented per feature in the advancements doc).
- **Backlog:** multi-level speculative routing chains (SpecRouter-style) until production-grade implementations mature; requires EM + Tech Lead promotion to enter scope.

## Compatibility and Integration Policies
- All inter-component contracts are versioned with a **defined backward-compatibility window** (minimum 12 months unless superseded by an ADR).
- Fail-closed behavior for validator timeouts, policy uncertainty, or schema mismatches.
- Capability-scoped tool gateway enforces least privilege for step execution.
- Control-plane and runtime APIs require strong authentication (OIDC/JWT for users, service tokens or mTLS for service-to-service).
- Control-plane authorization is default-deny with role-scoped grants (`Operator`, `SafetyOwner`, `InferenceDRI`, `Auditor`, `ServiceAgent`).
- High-risk actions (`policy change`, `promotion`, `tenant override`, `manual release override`) require dual authorization and immutable approval records.
- Tenant isolation is enforced with `tenant_id`-scoped access patterns and row-level controls on memory tables.
- All tool calls must include signed context (`principal_id`, `tenant_id`, `run_id`, `step_id`, `policy_version`) and are rejected on mismatch.

## Ownership
- **Tech Lead:** final technical decisions and trade-off accountability.
- **Inference DRI:** routing policy and backend benchmark governance.
- **Data/Memory DRI:** schema, retention, and promotion safety.
- **Observability DRI:** telemetry completeness and auditability.
