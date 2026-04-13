# Persona Agent Platform — Research Bibliography and OSS Integration (2024–Apr 2026)

## Purpose
Single place for **peer-reviewed and strong preprint research** (Jan 2024–Apr 2026) and **free/open-source software**. **Planned baseline usage** (what implementers ship unless an ADR explicitly replaces it) is defined in lockstep with `docs/implementation/2026-04-13-persona-agent-platform-tech-decisions.md`. Research **adopt-now / controlled-rollout / backlog** for techniques remains in `docs/implementation/2026-04-13-persona-agent-platform-quality-self-improvement-advancements.md`.

## OSS integration strategy (avoid reinventing the wheel)
- **Prefer composition** over rebuilding: LangGraph checkpointing, OTel-first traces, CI-bound eval harnesses, and optional memory/graph layers that respect **Postgres + tenant isolation** as the system of record.
- **One primary memory architecture:** either **Postgres + pgvector (+ RLS)** as the sole source of truth, or **Postgres + one** temporal/graph layer (for example Graphiti) with explicit boundaries. Avoid stacking **Mem0 + Graphiti + bespoke tables** without an ADR that names the owner of truth and migration path.
- **Self-hosted cost:** “Free license” does not mean free operations (for example Langfuse needs Postgres, ClickHouse, blob storage). Record infra ownership in the risk register before adoption.

### Planned baseline OSS (ship unless ADR replaces)

| Area | Project | License (verify on repo) | Planned usage |
|------|---------|--------------------------|----------------|
| Checkpoints | [`langgraph-checkpoint-postgres`](https://github.com/langchain-ai/langgraph) | Ecosystem OSS | **All** LangGraph graphs use Postgres-backed checkpointing on the same database cluster as memory (isolated schema/namespace). |
| Prompt/policy CI | [promptfoo](https://github.com/promptfoo/promptfoo) | MIT | **Default** prompt and policy regression suites, CI blocking, and red-team fixtures; promotion packets attach promptfoo outputs. |
| Trace scoring | [agentevals](https://github.com/agentevals-dev/agentevals) | Apache-2.0 | **Default** scorer on exported **OpenTelemetry** traces for promotion and incident review (reduces full re-execution). |
| LLM pytest | [DeepEval](https://github.com/confident-ai/deepeval) | Apache-2.0 | **Default** pytest-integrated LLM gate tests for step and subsystem contracts. |
| RAG-style memory tests | [RAGAS](https://github.com/explodinggradients/ragas) | Apache-2.0 | **Used wherever** semantic retrieval is tested as RAG (faithfulness, context precision/recall). |
| Structured LLM I/O | [Instructor](https://github.com/jxnl/instructor) | MIT | **Default** for structured model outputs at planner, reviewer, and typed tool-argument boundaries (Pydantic-aligned). |
| Guardrail pipeline | [openai-guardrails-python](https://github.com/openai/openai-guardrails-python) | OSS (see repo) | **Default** configurable pipeline for input/output/tool guard patterns; **tenant binding, policy versioning, and temporal SMT logic** stay in platform code and call into or wrap this layer as needed. |

### Optional OSS (ADR or Observability DRI approval)

| Area | Project | When it is used |
|------|---------|-----------------|
| Trace UX + datasets | [Langfuse](https://github.com/langfuse/langfuse) | Self-hosted when Observability DRI accepts ops footprint; does **not** replace OTel export requirement. |
| Temporal knowledge graph | [Graphiti](https://github.com/getzep/graphiti) | Only if Phase 1 ADR selects “Postgres + Graphiti” for time-aware graph memory. |
| Memory orchestration API | [Mem0](https://github.com/mem0ai/mem0) | Only if ADR explicitly adds Mem0 **above** Postgres; never without single declared source of truth. |
| Patterns / UX reference | [Letta](https://github.com/letta-ai/letta) / [letta-code](https://github.com/letta-ai/letta-code) | Design reference only unless ADR adopts components. |

**Already core stack (not duplicated here):** LangGraph, AutoGen AgentChat, LiteLLM, Ollama, vLLM, Pydantic v2, Postgres, pgvector, OpenTelemetry — see `README.md` and tech decisions.

---

## Research — long-term and structured memory (selected)

| Paper | URL |
|--------|-----|
| Episodic Memory is the Missing Piece for Long-Term LLM Agents | https://arxiv.org/abs/2502.06975 |
| Echo: LLM with Temporal Episodic Memory | https://arxiv.org/abs/2502.16090 |
| Agentic Memory (AgeMem) | https://arxiv.org/abs/2601.01885 |
| A-MEM: Agentic Memory for LLM Agents | https://arxiv.org/abs/2502.12110 |
| MemGen (ICLR 2026) | https://arxiv.org/abs/2509.24704 |
| G-Memory: Hierarchical Memory for Multi-Agent Systems | https://arxiv.org/abs/2506.07398 |
| Oblivion: Decay-Driven Agentic Memory Control | https://arxiv.org/abs/2604.00131 |
| SimpleMem: Efficient Lifelong Memory | https://arxiv.org/abs/2601.02553 |
| Hindsight: Retains, Recalls, Reflects | https://arxiv.org/abs/2512.12818 |
| Memori: Persistent Memory Layer | https://arxiv.org/abs/2603.19935 |
| How Memory Management Impacts LLM Agents (empirical) | https://arxiv.org/abs/2505.16067 |
| Rethinking Memory in LLM-based Agents (survey) | https://arxiv.org/abs/2505.00675 |
| MetaReflection | https://arxiv.org/abs/2405.13009 |

---

## Research — self-improvement, trajectories, skills

| Paper | URL |
|--------|-----|
| Experiential Reflective Learning (ERL) | https://arxiv.org/abs/2603.24639 |
| AgentHER | https://arxiv.org/abs/2603.21357 |
| Trace2Skill | https://arxiv.org/abs/2603.25158 |
| AutoSkill | https://arxiv.org/abs/2603.01145 |
| SkillX | https://arxiv.org/abs/2604.04804 |
| GEPA | https://arxiv.org/abs/2507.19457 |
| Agent-R | https://arxiv.org/abs/2501.11425 |
| Synthetic self-reflected trajectories + masking | https://arxiv.org/abs/2505.20023 |
| SAGE (RL + skill library) | https://arxiv.org/abs/2512.17102 |
| SAMULE (EMNLP 2025) | https://arxiv.org/abs/2509.20562 |
| AgentDebug | https://arxiv.org/abs/2509.25370 |
| SkillFlow | https://arxiv.org/abs/2504.06188 |

---

## Research — reliability, evaluation, promotion gates

| Paper | URL |
|--------|-----|
| τ-bench | https://arxiv.org/abs/2406.12045 |
| τ²-bench | https://arxiv.org/abs/2506.07982 |
| SWE-Bench Pro | https://arxiv.org/abs/2509.16941 |
| ReliabilityBench | https://arxiv.org/abs/2601.06112 |
| MAS-FIRE | https://arxiv.org/abs/2602.19843 |
| Replayable Financial Agents (DFAH) | https://arxiv.org/abs/2601.15322 |
| AgenTracer | https://arxiv.org/abs/2509.03312 |
| PALADIN | https://arxiv.org/abs/2509.25238 |
| G-Pass@k (ACL 2025 Findings) | https://aclanthology.org/2025.findings-acl.905/ |
| Don’t Pass@k (Bayesian) | https://arxiv.org/abs/2510.04265 |
| When Does Verification Pay Off? | https://arxiv.org/abs/2512.02304 |
| Multi-turn agent evaluation survey | https://arxiv.org/abs/2503.22458 |

---

## Research — planning and tree search

| Paper | URL |
|--------|-----|
| LATS (ICML 2024 proceedings) | https://proceedings.mlr.press/v235/zhou24r.html |
| LATS (arXiv) | https://arxiv.org/abs/2310.04406 |
| MASTER | https://arxiv.org/abs/2501.14304 |
| Cost-Aware Tree-Search LLM Planning | https://arxiv.org/abs/2505.14656 |
| ToolTree | https://arxiv.org/abs/2603.12740 |
| ReAcTree | https://arxiv.org/abs/2511.02424 |
| ChatHTN | https://proceedings.mlr.press/v288/munoz-avila25a.html |
| Pre-Act | https://arxiv.org/abs/2505.09970 |
| ReflAct | https://arxiv.org/abs/2505.15182 |
| StateAct | https://aclanthology.org/2025.realm-1.27/ |
| Web agents world model | https://arxiv.org/abs/2411.06559 |
| SimuRA | https://arxiv.org/abs/2507.23773 |
| ProAct | https://arxiv.org/abs/2602.05327 |

---

## Research — safety, temporal policy, tool chains, audit

| Paper | URL |
|--------|-----|
| GuardAgent | https://arxiv.org/abs/2406.09187 |
| Enforcing Temporal Constraints for LLM Agents (Agent-C) | https://arxiv.org/abs/2512.23738 |
| Solver-Aided Verification of Policy Compliance | https://arxiv.org/abs/2603.20449 |
| Progent | https://arxiv.org/abs/2504.11703 |
| AgentSpec | https://arxiv.org/abs/2503.18666 |
| STAC (tool chains) | https://arxiv.org/abs/2509.25624 |
| AgentHarm | https://arxiv.org/abs/2410.09024 |
| Structured generation attack surface | https://arxiv.org/abs/2503.24191 |
| LLM ecosystem jailbreak survey | https://arxiv.org/abs/2506.15170 |
| Stackelberg agentic defense | https://arxiv.org/abs/2507.08207 |
| R-Judge | https://arxiv.org/abs/2401.10019 |
| AgentPoison | https://arxiv.org/abs/2407.12784 |
| PROV-AGENT | https://arxiv.org/abs/2508.02866 |

---

## Cross-links to existing platform docs
- Base design and URL list: `docs/superpowers/specs/2026-04-13-persona-agent-platform-design.md`
- Adoption tiers and evidence packs: `docs/implementation/2026-04-13-persona-agent-platform-quality-self-improvement-advancements.md`
- Stack and parity: `docs/implementation/2026-04-13-persona-agent-platform-tech-decisions.md`
- Release gate and no-repeat-failure: `docs/implementation/2026-04-13-persona-agent-platform-release-gate-spec.md`

## Maintenance
- **Tech Lead** and **Data/Memory DRI** review this file on a fixed cadence (**at least every 12 weeks** while the program is active) or whenever a subsystem plateaus; new entries require one-line rationale and link. (This is a **review cadence**, not a product “quarter” or release train.)
- Verify **arXiv version** and **venue claims** on the primary PDF or publisher page before citing externally.
