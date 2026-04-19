# Stable libraries and products (2025–2026) — narrow slices for SDE / company OS

**In plain words:** this is a **practitioner brief**: which **mature, narrow** tools map to **small parts** of the north star (orchestration, memory, RAG, jobs, sandboxes, observability) so you can **reuse** in a **greenfield** implementation — **without** changing the **law** (`docs/sde/implementation-contract.md`, `src/sde_gates/`, artifact contracts). Delivery scope is tracked per feature in [`../versioning/`](../versioning/) (`plans/`, `README`, `INDEX`).

**Rule (same as [self-improvement-research-alignment.md](self-improvement-research-alignment.md)):** libraries inform **implementation**; they **do not** relax hard-stops or precedence in [`action-plan.md`](../onboarding/action-plan.md).

---

## 1. Selection criteria (when a dependency earns its place)

| Criterion | Question |
|-----------|----------|
| **Narrow surface** | Does it solve **one** problem (e.g. retrieval, checkpointing) behind a **port**? |
| **Stability signal** | **v1+**, active security patches, clear upgrade policy, license compatible with your distribution model. |
| **Operability** | Runs in **`local-prod`** or documented path; no mandatory opaque cloud for core flows unless you explicitly accept that. |
| **Escape hatch** | Feature-flag off; core `sde` path still works without the group. |
| **Evidence** | You can prove behavior with tests tied to **`docs/sde/`** contracts and **`src/sde_gates/`** (and OSV plan sign-off where used). |

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

1. [`../sde/what.md`](../sde/what.md) — product surface and constraints.  
2. [`../versioning/README.md`](../versioning/README.md) — per-feature version plans (`plans/`).  
3. [self-improvement-research-alignment.md](self-improvement-research-alignment.md) — papers ↔ gates.  
4. This file — **which product/library** per slice.

---

## 6. Changelog

- **2026-04-18:** Dropped references to removed migration doc; framed for **greenfield** + versioning plans only.
- **2026-04-18:** Initial brief (LangGraph 1.0, Temporal, Instructor, LlamaIndex, Mem0, E2B, OTel) with pros/cons and stability framing; links are primary evidence — **re-verify versions** before pinning in `pyproject.toml`.
