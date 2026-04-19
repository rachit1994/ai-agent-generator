# Self-improvement, self-training, and alignment research — notes for this repo

**In plain words:** this is a **reading list with commentary**. It says “paper X is about Y; here is how that idea could **help** our **runtime**.” It does **not** change the law: **HS01–HS06 and the rest of the gates in `src/sde_gates/` still win.** Use it when you want **citations** or **benchmark ideas**, not when you want to skip gates.

This document summarizes **peer-reviewed and widely cited preprints** relevant to **self-learning**, **iterative refinement**, **self-training / self-fine-tuning**, and **governance of model improvement**. It maps ideas to **this repository’s code and SDE docs** (`docs/sde/implementation-contract.md`, `src/sde_gates/`, harness layers under `src/sde_pipeline/runner/`) so implementers can justify techniques and **benchmarks** with external evidence.

**Rule:** Nothing here relaxes hard-stops or safety floors enforced in **`src/sde_gates/`**; research informs **how** to collect signal, **when** to train, and **what** to measure—not **whether** to skip gates. **Global precedence** for planning vs execution is fixed in [action-plan.md](../onboarding/action-plan.md) §2: **V1 (HS01–HS06) always dominates** motivated self-learning and speed.

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
- **ReST^EM:** **E-step** (sample + reward filter) / **M-step** (train on accepted). Reward = tests, linters, human evaluator, or hybrid—aligned with **`verification_bundle.json`** and **`src/sde_gates/`** outcomes.
- **ReST-MCTS\***:** use **search + process rewards** to collect higher-quality traces before training. Useful when **code reasoning** depth matters; costlier—fits **offline** improvement jobs behind evolution / canary artifacts.

### 2.3 When iterative self-training collapses (monitoring)

- **B-STaR:** over iterations, **exploration** and **reward usefulness** can **decay**. Mitigations:
  - Track **diversity metrics** in evolution / canary artifacts under `outputs/`.
  - Rotate **holdout tasks** and **OOD** checks before promoting bundles (ties to **HS28** in `src/sde_gates/hard_stops_evolution.py` and master architecture §18).

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
| `src/sde_pipeline/` guarded pipeline + reviews | Self-Refine + Constitutional AI patterns for iterative critique. |
| `verification_bundle.json`, `src/sde_gates/` | Sol-Ver + ReST^EM + Mind the Gap: verification as verifier. |
| `event_lineage_layer.py`, `hard_stops_events.py` | STaR / ReST: replayable lineage for accepted training rows. |
| `memory_artifact_layer.py`, `hard_stops_memory.py` | S3FT + contradiction handling: selective promotion, quarantine. |
| `evolution_layer.py`, `hard_stops_evolution.py` | B-STaR + CAI + ReST-MCTS\*: canary, exploration, promotion signals. |
| `organization_layer.py`, `hard_stops_organization.py` | Multi-agent credit assignment and evaluator isolation. |

---

## 3b. Engineering stack choices (optional libraries; gates unchanged)

Optional **LangGraph**, **Mem0-class long-term memory**, **RAG**, and **async self-learning jobs** must still respect hard-stops and contracts if you adopt them in a **from-scratch** build. Mem0 (scalable extract / consolidate / retrieve) is summarized in [arXiv:2504.19413](https://arxiv.org/abs/2504.19413) and fits the **governed memory** story when combined with quarantine and provenance (`memory_artifact_layer`, `hard_stops_memory.py`).

**Stable products / pros–cons (2025–2026 snapshot):** **[`stable-libraries-advancements-2026.md`](stable-libraries-advancements-2026.md)** — LangGraph 1.0, Temporal, Instructor, LlamaIndex, Mem0, E2B, OpenTelemetry, etc., with **when to use / defer**. Version scope lives under **[`../versioning/`](../versioning/)** (`plans/`, `README`).

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

- **2026-04-18:** Removed versioning migration doc pointer from §3b; stack choices point at **[`stable-libraries-advancements-2026.md`](stable-libraries-advancements-2026.md)** and **`../versioning/`** only.
- **2026-04-18:** Added link in §3b to **[`stable-libraries-advancements-2026.md`](stable-libraries-advancements-2026.md)** (stable products, pros/cons).
- **2026-04-18:** Removed links to deleted **`docs/coding-agent/*`** specs; maps to **code paths** instead.
- **2026-04-17:** Initial bibliography and mapping.
