# Quality and Self-Improvement Advancements (2026 Update)

## Objective
Capture recent research and ecosystem advancements that materially improve reliability, quality assurance, and autonomous self-improvement for the persona platform. **Production exit** includes governed adoption of these techniques where tagged below—not a reduced “MVP” subset.

**Normative tie-breaks** (`agentevals` floors, observability phase split, parity): `docs/implementation/2026-04-13-persona-agent-platform-doc-precedence.md`.

**Canonical paper lists and OSS projects:** `docs/implementation/2026-04-13-persona-agent-platform-research-and-oss-integration.md`

**Evidence tooling (planned usage):** promotion and gate evidence use **promptfoo**, **agentevals** (on OTel traces), and **DeepEval** / **RAGAS** as described in `docs/implementation/2026-04-13-persona-agent-platform-tech-decisions.md` and the delivery process.

**How to run the program day to day:** `docs/implementation/2026-04-13-persona-agent-platform-execution-playbook.md`

## Adoption Tiers
### Adopt Now (Production Exit)
1. **Trajectory reflection with reusable heuristics (ERL-style)**
   - Why: strong transfer of lessons across tasks and measurable reliability gains.
   - Integrate: extract heuristics from trajectory outcomes and inject during planning context build.
   - Owner: Quality Owner.
   - Primary success metric: +2 percentage-point uplift in repeated-run reliability (`pass^k`) on the **production workflow manifest**.
2. **Reliability stress evaluation beyond single-run success**
   - Why: production failures often appear under perturbation and tool-fault stress, not baseline tests.
   - Integrate: add repeated-run consistency (`pass^k`), semantic perturbation tests, and controlled fault-injection tests in CI/nightly.
   - Owner: Tech Lead.
   - Primary success metric: stress-suite pass rates meet SLO thresholds for consistency, robustness, and fault tolerance across the manifest.
3. **SLO-aware adaptive speculative decoding**
   - Why: improves latency while maintaining SLO attainment under dynamic load.
   - Integrate: tune draft/verifier strategy based on live load profiles and track quality regressions.
   - Owner: Inference DRI.
   - Primary success metric: p95 latency within SLO with no safety or reliability regression over two consecutive weekly operating windows.
4. **Generative latent memory (MemGen-inspired)**
   - Why: long-horizon adaptation beyond literal retrieval-only patterns.
   - Integrate: governed write path, tenant isolation, promotion rules, and safety non-regression suite before activation in production configuration.
   - Owner: Data/Memory DRI.
   - Primary success metric: measurable trajectory-quality uplift on held-out scenarios with zero safety regression and auditable promotion history.
5. **Reflective prompt evolution (GEPA-style)**
   - Why: efficient prompt/program optimization from rich trajectory feedback.
   - Integrate: held-out regression suite, safety non-regression constraints, rollback-capable prompt registry, and promotion tied to release gate spec.
   - Owner: Tech Lead.
   - Primary success metric: offline + canary candidate win rate versus baseline with mandatory safety replay green.

### Controlled Rollout (Required Before Exit When Listed)
- Items here ship behind flags and ladders but **must** reach the agreed **production configuration** (documented in the gate packet) before production exit. They are not optional deferrals after promotion; if none are listed for exit, this section is empty.

### Backlog / Research Watch
1. **Multi-level speculative chain routing (SpecRouter-style)**
   - Why: promising latency/cost profile, but ecosystem maturity is early for production-critical paths.
   - Trigger to revisit: stable production implementation with clear rollback and observability support.
   - Owner: Inference DRI.

## Required Governance Changes
- Any quality/self-improvement technique must map to:
  - named owner,
  - measurable KPI or SLO delta,
  - safety non-regression test,
  - rollback procedure.
- Promotion policy:
  - sandbox -> shadow -> canary -> production,
  - automatic demotion on reliability or safety threshold breach.

## Evidence Pack Requirements Per Technique
- Baseline vs candidate metrics on held-out suite.
- Reliability stress results (`pass^k`, perturbations, fault injection).
- Safety gate comparisons and incident impact analysis.
- Cost and latency deltas with confidence intervals.

## References
- ERL: https://arxiv.org/abs/2603.24639
- ReliabilityBench: https://arxiv.org/abs/2601.06112
- MemGen: https://arxiv.org/abs/2509.24704
- AdaSpec: https://arxiv.org/abs/2503.05096
- SpecRouter: https://arxiv.org/abs/2505.07680
- GEPA: https://arxiv.org/abs/2507.19457
- DSPy optimizers (GEPA/MIPRO): https://dspy.ai/learn/optimization/optimizers
- AgentEvals: https://github.com/agentevals-dev/agentevals
- promptfoo: https://github.com/promptfoo/promptfoo
- DeepEval: https://github.com/confident-ai/deepeval
- RAGAS: https://github.com/explodinggradients/ragas
- Graphiti: https://github.com/getzep/graphiti
- Mem0: https://github.com/mem0ai/mem0
- TruLens: https://trulens.org/
- Full tables: `docs/implementation/2026-04-13-persona-agent-platform-research-and-oss-integration.md`
