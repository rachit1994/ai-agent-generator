# Self-improvement, self-training, and alignment research — alignment with coding-agent specs

This document summarizes **peer-reviewed and widely cited preprints** relevant to **self-learning**, **iterative refinement**, **self-training / self-fine-tuning**, and **governance of model improvement**. It maps each line of work to this repository’s staged specs under [docs/coding-agent/](../coding-agent/) so implementers can justify techniques and **benchmarks** with external evidence.

**Rule:** Nothing here relaxes hard-stops or safety floors in [execution.md](../coding-agent/execution.md); research informs **how** to collect signal, **when** to train, and **what** to measure—not **whether** to skip gates.

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

- **Self-Refine:** output → self-feedback → refined output in multiple rounds. Maps to [planning.md](../coding-agent/planning.md) **learning synthesis**, **doc review**, and [completion.md](../coding-agent/completion.md) **per-step review** loops: keep **feedback text and verdict** in artifacts, not only final answers.
- **EVOLVE:** self-refinement may **not** emerge reliably unless **training and inference** are co-designed; if the product later adds **small fine-tunes** or adapters, pair them with the same **evaluation harness** used at inference (per spec gates).

### 2.2 Self-training and self-fine-tuning (weight update)

- **STaR:** generate rationales → **filter** with verifier → **SFT on successes** → repeat. Maps to any future **train-on-own-traces** path: only **verified** rows enter the training set; lineage in [events.md](../coding-agent/events.md).
- **ReST^EM:** **E-step** (sample + reward filter) / **M-step** (train on accepted). Same mapping; reward = tests, linters, human evaluator, or hybrid—aligned with [completion.md](../coding-agent/completion.md) `verification_bundle.json`.
- **ReST-MCTS\***:** use **search + process rewards** to collect higher-quality traces before training. Useful when **code reasoning** depth matters; costlier—fits **offline** improvement jobs behind V6 canary.

### 2.3 When iterative self-training collapses (monitoring)

- **B-STaR:** over iterations, **exploration** (diversity of candidates) and **reward usefulness** can **decay**. Mitigations for our specs:
  - Track **diversity metrics** (e.g. edit distance between proposed patches, n-gram novelty of rationales) in `learning/canary_report.json` / evolution artifacts.
  - Rotate **holdout tasks** and **OOD** checks before promoting bundles (ties to [evolution.md](../coding-agent/evolution.md) **HS28** and master architecture §18).

### 2.4 Fundamental limit: generation–verification gap

- **Mind the Gap:** self-improvement is bounded by how well the model **verifies** vs **generates**; gap relates to pretraining scale. **Implication:** never promote self-training data unless **verifier strength** on that slice is explicitly measured (holdout + adversarial examples). Reinforces [completion.md](../coding-agent/completion.md) verification and [evolution.md](../coding-agent/evolution.md) independent evaluator signals.

### 2.5 Code-specific solver–verifier co-training

- **Learning to Solve and Verify:** joint improvement of **code and tests**. Directly reinforces [completion.md](../coding-agent/completion.md): **tests as first-class artifacts** in the verification bundle before any “learned update” is trusted.

### 2.6 Selective self-supervision for generalization

- **S3FT:** mixing **gold** labels with **model-generated correct** responses reduces over-specialization vs naive SFT. Maps to [memory.md](../coding-agent/memory.md) write policy: prefer **quarantine → promote** with **dual sources** (human + verified model) for long-lived facts.

### 2.7 Governance-shaped self-critique (RLAIF / constitutional)

- **Constitutional AI / RLAIF:** critique → revise → preference modeling from **principles**, reducing pure human label load. Maps to [planning.md](../coding-agent/planning.md) **doc review** and [evolution.md](../coding-agent/evolution.md) **reflection bundles**: principles = **CTO + product constraints** encoded as checklists, not free-form model taste.
- **Why Does RLAIF Work At All?** (theory): reminds that **AI preference** can track latent training objectives—**independent evaluator** and **human veto** remain justified ([evolution.md](../coding-agent/evolution.md) **HS26**, master §15 arbitration).

### 2.8 Inference-time faithfulness

- **DSVD:** dynamic **self-verify decoding** to reduce hallucination. Optional upstream of `learning_events` / doc generation: bad drafts **fail before** they are logged as “truth” in memory.

---

## 3. Mapping: research → repository specs

| Spec file | Research leverage |
|-----------|-------------------|
| [planning.md](../coding-agent/planning.md) | Self-Refine + Constitutional AI for **learning_events**, **synthesis**, **doc review**; EVOLVE if later adding **adapter** training co-designed with gates. |
| [completion.md](../coding-agent/completion.md) | Sol-Ver + ReST^EM + Mind the Gap: **verification bundle** as verifier; no self-train promotion without **gap-aware** eval. |
| [events.md](../coding-agent/events.md) | STaR / ReST: every accepted training row must have **replayable event id**; HS17–HS20 for contract and drift. |
| [memory.md](../coding-agent/memory.md) | S3FT + contradiction literature: **selective promotion**, provenance, quarantine. |
| [evolution.md](../coding-agent/evolution.md) | B-STaR + CAI + ReST-MCTS\*: **canary**, exploration metrics, **independent** promotion signals, causal closure. |
| [organization.md](../coding-agent/organization.md) | Indirect: multi-agent **credit assignment** and **evaluator isolation** align with federated safety in master architecture; keep **IAM** boundaries when running distributed self-improve jobs. |

---

## 4. Suggested benchmark extensions (optional, for “Success is not assumed” style gates)

When implementing benchmarks (see each spec’s acceptance / success language), consider **explicit** rows for:

1. **Verification gap proxy:** accuracy of a **frozen verifier** (tests + lint + small model judge if used) on a **holdout** suite before vs after a learning bundle.
2. **Exploration metric:** diversity of proposed patches or rationales across iterations (B-STaR).
3. **Data purity:** fraction of self-training rows with **dual** verification (test pass + independent check) vs single signal.
4. **Decode-time faithfulness:** optional DSVD-style check on user-visible doc outputs before `doc_pack_manifest` hash lock.

These are **not** new hard-stop IDs by default; they are **recommended metrics** until the program office pins them in `summary.json` / evolution artifacts.

---

## 5. Changelog

- **2026-04-17:** Initial bibliography and mapping for coding-agent planning, completion, events, memory, and evolution specs.
