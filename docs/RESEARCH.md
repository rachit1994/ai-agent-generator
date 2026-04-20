# Research notes (papers, libraries)

**Rule:** research informs **how** to measure and build; it does **not** relax **`src/guardrails_and_safety/`** or artifact contracts. **V1 / HS01–HS06** precedence from the master architecture still dominates motivated self-learning.

**Related:** [`UNDERSTANDING-THE-CODE.md`](UNDERSTANDING-THE-CODE.md) · [`AI-Professional-Evolution-Master-Architecture.md`](AI-Professional-Evolution-Master-Architecture.md)

---

## 1. Self-improvement, self-training, and alignment

# Self-improvement, self-training, and alignment research — notes for this repo

**In plain words:** this is a **reading list with commentary**. It says “paper X is about Y; here is how that idea could **help** our **runtime**.” It does **not** change the law: **HS01–HS06 and the rest of the gates in `src/guardrails_and_safety/` still win.** Use it when you want **citations** or **benchmark ideas**, not when you want to skip gates.

This document summarizes **peer-reviewed and widely cited preprints** relevant to **self-learning**, **iterative refinement**, **self-training / self-fine-tuning**, and **governance of model improvement**. It maps ideas to **this repository’s code and SDE docs** (`docs/UNDERSTANDING-THE-CODE.md` (implementation contract section), `src/guardrails_and_safety/`, harness layers under `src/workflow_pipelines/production_pipeline_task_to_promote/runner/`) so implementers can justify techniques and **benchmarks** with external evidence.

**Rule:** Nothing here relaxes hard-stops or safety floors enforced in **`src/guardrails_and_safety/`**; research informs **how** to collect signal, **when** to train, and **what** to measure—not **whether** to skip gates. **Global precedence** for planning vs execution is fixed in [`AI-Professional-Evolution-Master-Architecture.md`](AI-Professional-Evolution-Master-Architecture.md) §2: **V1 (HS01–HS06) always dominates** motivated self-learning and speed.

---

## 1. Paper and resource index

| Topic | Reference | Link |
|--------|-----------|------|
| Iterative refinement without weight updates | Madaan et al., *Self-Refine: Iterative Refinement with Self-Feedback*, 2023 | [https://arxiv.org/abs/2303.17651](https://arxiv.org/abs/2303.17651) |
| Training–inference synergy for refinement | *Evolving LLMs' Self-Refinement Capability via Synergistic Training-Inference Optimization* (EVOLVE), 2025 | [https://arxiv.org/abs/2502.05605](https://arxiv.org/abs/2502.05605) |
| Bootstrapped reasoning + fine-tune on verified traces | Zelikman et al., *STaR: Bootstrapping Reasoning With Reasoning*, NeurIPS 2022 | [https://arxiv.org/abs/2203.14465](https://arxiv.org/abs/2203.14465) |
| EM-style self-training from reward filtering | Gulcehre et al., *Reinforced Self-Training (ReST^EM)*, 2023 | [https://arxiv.org/abs/2312.06585](https://arxiv.org/abs/2312.06585) |
| Reward-guided search + self-training | *ReST-MCTS\**: LLM Self-Training via Reward Guided Search*, 2024 | [https://arxiv.org/abs/2406.03816](https://arxiv.org/abs/2406.03816) |
| Exploration vs exploitation in iterative self-improvement | *B-STaR*, ICLR 2025 | [https://proceedings.iclr.cc/paper_files/paper/2025/file/c8db30c6f024a3f667232ed7ba5b6d47-Paper-Conference.pdf](https://proceedings.iclr.cc/paper_files/paper/2025/file/c8db30c6f024a3f667232ed7ba5b6d47-Paper-Conference.pdf) |
| Formal limits: generation vs verification | Song et al., *Mind the Gap: Examining the Self-Improvement Capabilities of Large Language Models*, ICLR 2025 | [https://openreview.net/pdf?id=mtJSMcF3ek](https://openreview.net/pdf?id=mtJSMcF3ek) |
| Solver–verifier co-evolution (code + tests) | *Learning to Solve and Verify* (Sol-Ver-style pipeline), 2025 | [https://arxiv.org/abs/2502.14948](https://arxiv.org/abs/2502.14948) |
| Selective use of model’s own correct samples | *Selective Self-to-Supervised Fine-Tuning* (S3FT), NAACL 2025 Findings | [https://aclanthology.org/2025.findings-naacl.349/](https://aclanthology.org/2025.findings-naacl.349/) |
| Self-critique + principles → revised data | Bai et al., *Constitutional AI: Harmlessness from AI Feedback* | [https://arxiv.org/abs/2212.08073](https://arxiv.org/abs/2212.08073) |
| Extended CAI / RLAIF narrative | Anthropic, *Constitutional AI* (PDF) | [https://www-cdn.anthropic.com/7512771452629584566b6303311496c262da1006/Anthropic_ConstitutionalAI_v2.pdf](https://www-cdn.anthropic.com/7512771452629584566b6303311496c262da1006/Anthropic_ConstitutionalAI_v2.pdf) |
| Decoding-time self-verification | *DSVD: Dynamic Self-Verify Decoding for Faithful Generation*, 2025 | [https://arxiv.org/abs/2503.03149](https://arxiv.org/abs/2503.03149) |
| Theory note (RLAIF / latent preferences) | Young, *Why Does RLAIF Work At All?*, arXiv 2026 | [https://arxiv.org/abs/2603.03000](https://arxiv.org/abs/2603.03000) |

---

## 2. Core techniques (concise)

### 2.1 In-context self-improvement (no weight update)

- **Self-Refine:** output → self-feedback → refined output in multiple rounds. Maps to **review loops and artifacts** (guarded pipeline, `review.json`, verification) — keep **feedback text and verdict** on disk, not only final answers.
- **EVOLVE:** self-refinement may **not** emerge reliably unless **training and inference** are co-designed; if the product later adds **small fine-tunes** or adapters, pair them with the same **evaluation harness** used at inference (per gate code).

### 2.2 Self-training and self-fine-tuning (weight update)

- **STaR:** generate rationales → **filter** with verifier → **SFT on successes** → repeat. Maps to any future **train-on-own-traces** path: only **verified** rows enter the training set; lineage must tie to **`event_lineage_layer`** / `replay_manifest.json` when present.
- **ReST^EM:** **E-step** (sample + reward filter) / **M-step** (train on accepted). Reward = tests, linters, human evaluator, or hybrid—aligned with **`verification_bundle.json`** and **`src/guardrails_and_safety/`** outcomes.
- **ReST-MCTS\***:** use **search + process rewards** to collect higher-quality traces before training. Useful when **code reasoning** depth matters; costlier—fits **offline** improvement jobs behind evolution / canary artifacts.

### 2.3 When iterative self-training collapses (monitoring)

- **B-STaR:** over iterations, **exploration** and **reward usefulness** can **decay**. Mitigations:
  - Track **diversity metrics** in evolution / canary artifacts under `outputs/`.
  - Rotate **holdout tasks** and **OOD** checks before promoting bundles (ties to **HS28** in `src/guardrails_and_safety/risk_budgets/hard_stops_evolution.py` and master architecture §18).

### 2.4 Fundamental limit: generation–verification gap

- **Mind the Gap:** self-improvement is bounded by how well the model **verifies** vs **generates**. **Implication:** never promote self-training data unless **verifier strength** on that slice is explicitly measured. Reinforces **verification bundles** and independent evaluator signals in evolution gates.

### 2.5 Code-specific solver–verifier co-training

- **Learning to Solve and Verify:** joint improvement of **code and tests**. Reinforces **tests as first-class artifacts** in the verification bundle before any “learned update” is trusted.

### 2.6 Selective self-supervision for generalization

- **S3FT:** mixing **gold** labels with **model-generated correct** responses reduces over-specialization. Maps to **memory** write policy: prefer **quarantine → promote** with **dual sources** (human + verified model) for long-lived facts (`memory_artifact_layer`, `hard_stops_memory.py`).

### 2.7 Governance-shaped self-critique (RLAIF / constitutional)

- **Constitutional AI / RLAIF:** critique → revise → preference modeling from **principles**. Maps to **doc-style review** and **reflection bundles**: principles = **CTO + product constraints** encoded as checklists, not free-form model taste.
- **Why Does RLAIF Work At All?** (theory): **independent evaluator** and **human veto** remain justified (master §15 arbitration; evolution hard-stops).

### 2.8 Inference-time faithfulness

- **DSVD:** dynamic **self-verify decoding** to reduce hallucination. Optional upstream of doc generation: bad drafts **fail before** they are logged as “truth” in memory.

---

## 3. Mapping: research → code areas (no Markdown spec stack)

| Code / doc area | Research leverage |
|-----------------|-------------------|
| `src/workflow_pipelines/production_pipeline_task_to_promote/` guarded pipeline + reviews | Self-Refine + Constitutional AI patterns for iterative critique. |
| `verification_bundle.json`, `src/guardrails_and_safety/` | Sol-Ver + ReST^EM + Mind the Gap: verification as verifier. |
| `event_lineage_layer.py`, `hard_stops_events.py` | STaR / ReST: replayable lineage for accepted training rows. |
| `memory_artifact_layer.py`, `hard_stops_memory.py` | S3FT + contradiction handling: selective promotion, quarantine. |
| `evolution_layer.py`, `hard_stops_evolution.py` | B-STaR + CAI + ReST-MCTS\*: canary, exploration, promotion signals. |
| `organization_layer.py`, `hard_stops_organization.py` | Multi-agent credit assignment and evaluator isolation. |

---

## 3b. Engineering stack choices (optional libraries; gates unchanged)

Optional **LangGraph**, **Mem0-class long-term memory**, **RAG**, and **async self-learning jobs** must still respect hard-stops and contracts if you adopt them in a **from-scratch** build. Mem0 (scalable extract / consolidate / retrieve) is summarized in [arXiv:2504.19413](https://arxiv.org/abs/2504.19413) and fits the **governed memory** story when combined with quarantine and provenance (`memory_artifact_layer`, `hard_stops_memory.py`).

**Stable products / pros–cons (2025–2026 snapshot):** §2 of this file (stable libraries brief) — LangGraph 1.0, Temporal, Instructor, LlamaIndex, Mem0, E2B, OpenTelemetry, etc., with **when to use / defer**. Version scope lives under **[`../versioning/`](../versioning/)** (`plans/`, `README`).

---

## 4. Suggested benchmark extensions (optional)

When implementing benchmarks, consider **explicit** rows for:

1. **Verification gap proxy:** accuracy of a **frozen verifier** on a **holdout** suite before vs after a learning bundle.
2. **Exploration metric:** diversity of proposed patches or rationales across iterations (B-STaR).
3. **Data purity:** fraction of self-training rows with **dual** verification vs single signal.
4. **Decode-time faithfulness:** optional DSVD-style check on user-visible doc outputs.

These are **not** new hard-stop IDs by default; they are **recommended metrics** until pinned in artifacts / `summary.json`.

---

## 5. Changelog

- **2026-04-18:** Removed versioning migration doc pointer from §3b; stack choices point at §2 of this file (stable libraries brief) and **`../versioning/`** only.
- **2026-04-18:** Added link in §3b to §2 of this file (stable libraries brief) (stable products, pros/cons).
- **2026-04-18:** Removed links to deleted **`docs/coding-agent/*`** specs; maps to **code paths** instead.
- **2026-04-17:** Initial bibliography and mapping.

---

## 2. Stable libraries and products (2025–2026)

# Stable libraries and products (2025–2026) — narrow slices for SDE / company OS

**In plain words:** this is a **practitioner brief**: which **mature, narrow** tools map to **small parts** of the north star (orchestration, memory, RAG, jobs, sandboxes, observability) so you can **reuse** in a **greenfield** implementation — **without** changing the **law** (`docs/UNDERSTANDING-THE-CODE.md`, `src/guardrails_and_safety/`, artifact contracts). Delivery scope is tracked per feature in [`../versioning/`](../versioning/) (`plans/`, `README`, `INDEX`).

**Rule (same as [§1 below](#1-self-improvement-self-training-and-alignment-research--notes-for-this-repo)):** libraries inform **implementation**; they **do not** relax hard-stops or precedence in [`action-plan.md`](../onboarding/action-plan.md).

---

## 1. Selection criteria (when a dependency earns its place)

| Criterion | Question |
|-----------|----------|
| **Narrow surface** | Does it solve **one** problem (e.g. retrieval, checkpointing) behind a **port**? |
| **Stability signal** | **v1+**, active security patches, clear upgrade policy, license compatible with your distribution model. |
| **Operability** | Runs in **`local-prod`** or documented path; no mandatory opaque cloud for core flows unless you explicitly accept that. |
| **Escape hatch** | Feature-flag off; core `sde` path still works without the group. |
| **Evidence** | You can prove behavior with tests tied to **`docs/UNDERSTANDING-THE-CODE.md`** (contracts section) and **`src/guardrails_and_safety/`**. |

---

## 2. Summary table (recommendation at a glance)

| Slice | Primary pick | Alternates | Maturity / signal (2025–2026) |
|-------|----------------|-------------|-------------------------------|
| **Stateful orchestration / HITL** | **[LangGraph](https://www.langchain.com/blog/langchain-langgraph-1dot0)** (with `langchain-core`) | [Temporal](https://temporal.io/ai) for **hours–days** durable workflows; keep hand-rolled FSM for zero-deps | LangGraph **1.0 GA** (LangChain announcement: [blog](https://blog.langchain.com/langchain-langgraph-1dot0/); changelog: [GA post](https://changelog.langchain.com/announcements/langgraph-1-0-is-now-generally-available)) — explicit stability story until 2.x |
| **Structured model outputs** | **[Instructor](https://python.useinstructor.com/)** (Pydantic-native) | [Pydantic AI](https://ai.pydantic.dev/) (especially with Temporal per [Temporal + Pydantic AI](https://temporal.io/blog/build-durable-ai-agents-pydantic-ai-and-temporal)); manual JSON + retries | Instructor: multi-provider, **Ollama listed** in provider docs; reduces bespoke parse/retry glue |
| **RAG / ingestion-heavy** | **[LlamaIndex](https://www.llamaindex.ai/)** | LangChain/LangGraph retrieval chains; [Unstructured](https://docs.unstructured.io/) for parsing only | Third-party 2026 comparisons generally give LlamaIndex an edge on **data/RAG depth** vs general orchestration breadth ([PremAI comparison](https://blog.premai.io/langchain-vs-llamaindex-2026-complete-production-rag-comparison/) — independent; treat numbers as directional) |
| **Broad integrations + traces** | **LangSmith** (if you already use LangChain) | **OpenTelemetry** + Grafana Tempo/Jaeger ([self-hosted patterns](https://dev.to/rapidclaw/2026-opentelemetry-for-llm-observability-self-hosted-setup-335o)); LangSmith [OTLP ingestion](https://blog.langchain.com/end-to-end-opentelemetry-support-in-langsmith) | OTel is the **vendor-neutral** long bet; LangSmith wins when evaluations/datasets are LangChain-centric |
| **Long-term memory (product)** | **Mem0** ([GitHub](https://github.com/mem0ai/mem0), [paper](https://arxiv.org/abs/2504.19413)) | [Zep](https://www.getzep.com/); roll-your-own on **pgvector** + jobs | Mem0: OSS + managed path, explicit **v1** narrative in ecosystem; **must** still enforce **quarantine / provenance** in *your* gate layer |
| **Durable async jobs (canary / promote / eval)** | **[Temporal](https://temporal.io/)** | [Inngest](https://www.inngest.com/) (event-driven, simpler ops); cron + queue | Temporal: [AI tutorials](https://learn.temporal.io/tutorials/ai/durable-ai-agent/), [Replit public note on migration](https://temporal.io/ai) — strong for **long-running, retriable** pipelines |
| **Remote code sandbox** | **[E2B](https://e2b.dev/docs/)** | [Daytona](https://www.daytona.io/); self-host **Docker + gVisor** | E2B: documented SDKs ([docs](https://e2b.dev/docs/)); choose based on **data residency** and cost |
| **Experiment tracking (learning loop)** | **[MLflow](https://mlflow.org/)** | Weights & Biases; DVC for data | MLflow: OSS, self-host friendly |

---

## 3. Per-slice pros and cons (honest)

### 3.1 LangGraph (+ `langchain-core`)

**Pros:** First-class **checkpoints**, **interrupt/resume**, **human-in-the-loop**, explicit graph — maps well to guarded / phased pipelines and later **parallel lanes** ([GA announcement](https://blog.langchain.com/langchain-langgraph-1dot0/)). Large integration surface if you need it later.

**Cons:** **Dependency weight** and release cadence outside your control; risk of **hiding** gate transitions inside “magic” nodes if you are undisciplined; LangChain umbrella **vendor** alignment if you adopt LangSmith deeply.

**Use when:** You want **maintainable** multi-step graphs and are willing to own **parity tests** against current `traces.jsonl` / manifests.

**Defer when:** You must keep **`dependencies = []`** for the default wheel and cannot use optional groups yet.

---

### 3.2 Temporal (workflows)

**Pros:** **Durable execution** across crashes and deploys; natural fit for **canary → promote**, nightly evals, long backfills ([Temporal for AI](https://temporal.io/ai), [Python AI agent tutorial](https://learn.temporal.io/tutorials/ai/durable-ai-agent/)).

**Cons:** **Operational stack** (server or cloud); determinism rules for workflow code; learning curve vs in-process asyncio.

**Use when:** Jobs are **cross-run**, **hours-long**, or need **strict** at-least-once semantics beyond “CLI loop.”

**Defer when:** Everything fits in a **single process** and idempotent cron is enough.

---

### 3.3 Instructor (or Pydantic AI)

**Pros:** Typed **Pydantic** outputs, fewer malformed JSON surprises, provider patches including paths relevant to **local models** ([Instructor site](https://python.useinstructor.com/), [repo](https://github.com/instructor-ai/instructor)).

**Cons:** Another abstraction over your existing `invoke_model`; behavior still depends on **model** quality.

**Use when:** A specific stage (e.g. `phased_decompose`, verifier payloads) drives disproportionate parse failures.

---

### 3.4 LlamaIndex (RAG-heavy slice)

**Pros:** Strong **ingestion + index** ergonomics and RAG-focused patterns ([comparison landscape 2026](https://blog.premai.io/langchain-vs-llamaindex-2026-complete-production-rag-comparison/)).

**Cons:** Second large framework if you **also** adopt LangGraph; overlap if you use LangChain document loaders everywhere.

**Use when:** RAG is a **read-only** context builder for discovery/research with **citations** into traces and **no** verifier shortcut.

**Defer when:** You have no vector store / embedding ops story in `local-prod` yet.

---

### 3.5 Mem0 (long-term memory)

**Pros:** Aligns with **extract / consolidate / retrieve** research direction ([arXiv:2504.19413](https://arxiv.org/abs/2504.19413)); OSS + docs ([GitHub](https://github.com/mem0ai/mem0), [docs](https://docs.mem0.ai/llms.txt)); reduces DIY memory plumbing.

**Cons:** **External** truth defaults to Mem0 unless you wire **your** quarantine / promotion; **license** (Apache 2.0 per common OSS listing — verify at source before ship); needs **LLM** for memory ops → cost and failure modes.

**Use when:** You are ready to implement **`MemoryStore` port** and treat Mem0 as **one backend**, not the authority on safety.

---

### 3.6 E2B (sandboxes)

**Pros:** **Purpose-built** for agent code execution in isolation ([E2B docs](https://e2b.dev/docs/)); faster time-to-**OSV-WORKER-02** than building Firecracker orchestration yourself.

**Cons:** **Network egress**, **vendor lock-in**, **cost at scale**; keys and data leave pure on-laptop mode.

**Use when:** Target repos need **trusted** arbitrary code execution with SLAs.

**Defer when:** `local-prod` policy is **air-gapped** or only Docker-on-bare-metal is acceptable.

---

### 3.7 OpenTelemetry (+ collector / Tempo / Grafana)

**Pros:** **Vendor-neutral** traces/metrics; emerging **GenAI semantic conventions** ecosystem ([self-hosted LLM observability writeup](https://dev.to/rapidclaw/2026-opentelemetry-for-llm-observability-self-hosted-setup-335o)); pairs with any framework.

**Cons:** You own **dashboards and sampling**; less “batteries included” than LangSmith for LangChain-specific eval UI.

**Use when:** You need **portable** production telemetry without tying observability to one LLM vendor.

---

## 4. What we are **not** optimizing for here

- **Bleeding-edge** research stacks without upgrade policy.
- Replacing **`validate_execution_run_directory`** or CTO gates with “the model said it’s fine.”
- **Full** framework rewrites in one PR without matching tests and contract updates.

---

## 5. Suggested reading order in this repo

1. [`UNDERSTANDING-THE-CODE.md`](UNDERSTANDING-THE-CODE.md) — product surface and constraints.  
2. *(removed — see master architecture for scope)* — per-feature version plans (`plans/`).  
3. [§1 below](#1-self-improvement-self-training-and-alignment-research--notes-for-this-repo) — papers ↔ gates.  
4. This file — **which product/library** per slice.

---

## 6. Changelog

- **2026-04-18:** Dropped references to removed migration doc; framed for **greenfield** + versioning plans only.
- **2026-04-18:** Initial brief (LangGraph 1.0, Temporal, Instructor, LlamaIndex, Mem0, E2B, OTel) with pros/cons and stability framing; links are primary evidence — **re-verify versions** before pinning in `pyproject.toml`.
