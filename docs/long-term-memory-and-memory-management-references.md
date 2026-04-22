# Long-term memory and memory management references

This document curates research and implementation references for long-term memory in LLM agents, with focus on memory lifecycle management (write, consolidate, retrieve, update, forget, and evaluate).

## Why this matters

Agent quality collapses at scale without disciplined memory management. Typical failure modes include:
- context-window overflow and recency bias,
- stale or contradictory facts,
- high-latency retrieval paths,
- privacy and retention failures,
- overconfident recall instead of abstention.

## Core papers and benchmarks

### Foundational memory architectures

- MemGPT:
  - [MemGPT: Towards LLMs as Operating Systems (arXiv)](https://arxiv.org/abs/2310.08560)
  - Key idea: OS-style hierarchical memory and "virtual context" with explicit paging between short context and external stores.

- Generative Agents:
  - [Generative Agents: Interactive Simulacra of Human Behavior (arXiv)](https://arxiv.org/abs/2304.03442)
  - Key idea: memory stream + reflection + retrieval scoring by recency, importance, and relevance.

- RAG:
  - [Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks (NeurIPS 2020)](https://proceedings.neurips.cc/paper/2020/hash/6b493230205f780e1bc26945df7481e5-Abstract.html)
  - [arXiv version](https://arxiv.org/abs/2005.11401)
  - Key idea: combine parametric memory (model weights) with non-parametric memory (retrieval index).

- LongMem:
  - [Augmenting Language Models with Long-Term Memory (arXiv)](https://arxiv.org/abs/2306.07174)
  - Key idea: decoupled long-term memory bank with retrieval/reader module; frozen backbone + adaptive side network.

### Memory-focused surveys

- [A Survey on the Memory Mechanism of LLM-based Agents (arXiv)](https://arxiv.org/html/2404.13501v1)
- [Memory for Autonomous LLM Agents: Mechanisms, Evaluation, and Emerging Frontiers (arXiv)](https://arxiv.org/abs/2603.07670v1)

### Memory evaluation benchmarks

- LongMemEval:
  - [LongMemEval paper (arXiv)](https://arxiv.org/abs/2410.10813v2)
  - [LongMemEval repo](https://github.com/xiaowu0162/LongMemEval)
  - Coverage: information extraction, multi-session reasoning, temporal reasoning, knowledge updates, abstention.

## Practical design patterns for this repo

Treat memory as a strict lifecycle, not a passive log:

1. **Write path (ingest)**
   - Capture only high-value events (decisions, outcomes, errors, user constraints).
   - Attach metadata: `run_id`, `tenant_id`, `timestamp`, `source`, `confidence`, `privacy_class`.
   - Reject low-signal or malformed writes at boundary.

2. **Consolidation path (summarize / reflect)**
   - Periodically summarize bursts of events into durable higher-level facts.
   - Preserve provenance links to raw evidence artifacts.
   - Avoid replacing raw evidence with summaries; keep both.

3. **Retrieval path**
   - Use hybrid retrieval (semantic + metadata filters).
   - Rank with recency + relevance + confidence.
   - Return citation-ready snippets, not opaque blobs.

4. **Update and contradiction handling**
   - Version memory facts; never silently overwrite.
   - Mark superseded facts and keep lineage.
   - On conflict, prefer newest high-confidence evidence or abstain.

5. **Forgetting and retention**
   - Define TTL by memory class (ephemeral/session/long-term/compliance).
   - Enforce deletion and redaction jobs deterministically.
   - Keep audit logs of retention actions.

6. **Read-time safety**
   - Require authorization checks before retrieval.
   - Support abstention when evidence is weak or conflicting.
   - Never expose cross-tenant memory slices.

## Suggested memory taxonomy

- `working_memory`: context-window resident task state.
- `episodic_memory`: event timeline of runs/sessions.
- `semantic_memory`: consolidated facts, preferences, constraints.
- `procedural_memory`: reusable plans, prompts, and tool-use heuristics.

## Minimum memory quality gates

Before claiming memory feature completion, require:

- Write gate:
  - schema-valid memory writes only,
  - tenant and provenance fields always present.

- Retrieval gate:
  - recall@k and precision@k tracked on fixed benchmark queries,
  - latency p95 within budget.

- Consistency gate:
  - contradiction detection test suite,
  - update semantics preserve lineage.

- Safety gate:
  - cross-tenant isolation tests,
  - retention/deletion policy tests,
  - abstention behavior tests for uncertain memory.

## Implementation references (code)

- MemGPT:
  - [MemGPT project site](https://memgpt.ai)

- LongMem:
  - [Victorwz/LongMem](https://github.com/Victorwz/LongMem)

- LongMemEval benchmark:
  - [xiaowu0162/LongMemEval](https://github.com/xiaowu0162/LongMemEval)

## Adoption roadmap (practical)

1. Add strict memory write schema + provenance metadata.
2. Add hybrid retrieval with recency/relevance scoring.
3. Add consolidation and contradiction-resolution policies.
4. Add retention classes with deterministic deletion jobs.
5. Add LongMemEval-style regression suite and promote only on no-regression.

## Source quality notes

- Prefer `paper` and `official` sources for architecture decisions.
- Use repos as implementation references, not proof of suitability for your threat model.
- Treat blog claims as hypotheses until reproduced in local evaluation.
