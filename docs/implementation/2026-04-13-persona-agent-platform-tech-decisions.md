# Persona Agent Platform Technology Decisions (Production)

## Decision Framework
Selection criteria:
- deterministic workflow orchestration,
- strong typed contracts and validation,
- local-first inference support with routing flexibility,
- robust observability and replay,
- operational simplicity for one-quarter delivery.

## Final Stack
### Workflow and Agent Orchestration
- **LangGraph** for stateful workflow orchestration with checkpoints and resumability.
- **AutoGen AgentChat** for step-level triad collaboration (`architect`, `implementer`, `reviewer`).

Rationale:
- LangGraph gives deterministic state transitions and persistence-friendly execution flow.
- AutoGen triad aligns directly with the persona execution contract in the base spec.

### Model Routing and Inference
- **LiteLLM** for unified model client and backend routing policy.
- **Ollama** and **vLLM** as co-equal local backends.
- Adaptive routing and speculative decoding policy managed in inference control layer.

Rationale:
- Preserves local runtime flexibility while preventing hard backend lock-in.
- Supports latency/quality trade-offs under explicit SLO controls.

### Contracts and Validation
- **Pydantic v2** for typed request/response contracts and schema validation.
- Validator chain for input, action, output, and temporal checks.

Rationale:
- Strong runtime type safety and predictable integration boundaries.
- Easier machine-checkable acceptance criteria at step gates.

### Memory and Storage
- **Postgres + pgvector** for durable episodic, semantic, procedural, and failure memory.
- Hierarchical summaries for long-horizon memory compaction.
- Add a generative-memory pilot interface (MemGen-inspired) behind feature flags.

Rationale:
- Production-ready relational durability plus semantic retrieval in one platform.
- Supports tenant isolation and auditable memory promotion policies.

### Observability and Evaluation
- **OpenTelemetry** for traces/metrics foundation.
- Structured logs for auditable run diagnostics.
- Evaluation harness for regression replay and policy/prompt promotion.
- OTel-trace eval layer support for `agentevals`-style offline reliability scoring.
- Optional metric instrumentation compatible with `TruLens` for groundedness and relevance checks.

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

## Quality and Self-Improvement Techniques (Adoption Decision)
- **Adopt now:** trajectory-reflection heuristics (ERL-style), reliability stress tests (`pass^k`, perturbations, fault injection), and SLO-aware speculative decoding tuning.
- **Pilot:** generative latent memory (MemGen-style) and reflective prompt evolution pipelines (GEPA-style) under feature flags.
- **Backlog:** multi-level speculative routing chains (SpecRouter-style) until production-grade implementations mature.

## Compatibility and Integration Policies
- All inter-component contracts are versioned and backward compatible for one quarter minimum.
- Fail-closed behavior for validator timeouts, policy uncertainty, or schema mismatches.
- Capability-scoped tool gateway enforces least privilege for step execution.

## Ownership
- **Tech Lead:** final technical decisions and trade-off accountability.
- **Inference DRI:** routing policy and backend benchmark governance.
- **Data/Memory DRI:** schema, retention, and promotion safety.
- **Observability DRI:** telemetry completeness and auditability.
