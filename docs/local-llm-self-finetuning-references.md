# Local LLM self-fine-tuning references

This document curates research papers, engineering references, and implementation repositories for self-fine-tuning local LLMs.

Scope:
- Local or single-node friendly post-training methods.
- Synthetic/self-generated data bootstrapping methods.
- Preference optimization methods that do not require full RLHF stacks.
- Practical OSS training toolchains for LoRA/QLoRA and preference tuning.

## What "self-fine-tuning" means here

In this repo context, self-fine-tuning means one or more of:
- generating synthetic instructions or examples from a model and re-training on filtered outputs,
- using model- or user-preference pairs to improve behavior,
- running lightweight local post-training (LoRA/QLoRA) instead of full model retraining.

It does not imply unconstrained autonomous self-modification in production.

## High-confidence core papers

### Parameter-efficient local tuning

- LoRA (foundational):
  - [LoRA: Low-Rank Adaptation of Large Language Models (arXiv)](https://arxiv.org/abs/2106.09685)
  - Why it matters: introduces low-rank adapters so only a small parameter subset is trained.

- QLoRA (practical local scaling):
  - [QLoRA: Efficient Finetuning of Quantized LLMs (arXiv)](https://arxiv.org/abs/2305.14314)
  - Why it matters: 4-bit quantized base + LoRA adapters enables much larger models on limited VRAM.

### Self-generated data bootstrapping

- Self-Instruct:
  - [Self-Instruct: Aligning Language Models with Self-Generated Instructions (arXiv)](https://arxiv.org/abs/2212.10560)
  - [ACL Anthology version](https://aclanthology.org/2023.acl-long.754)
  - Why it matters: canonical pipeline for generating, filtering, and training on synthetic instruction data.

### Preference tuning without RL loops

- DPO:
  - [Direct Preference Optimization: Your Language Model is Secretly a Reward Model (arXiv)](https://arxiv.org/abs/2305.18290)
  - Why it matters: directly optimizes preference pairs without PPO-style RLHF complexity.

- DPO landscape surveys:
  - [Comprehensive Survey of DPO (arXiv)](https://arxiv.org/abs/2410.15595)
  - [Survey of DPO (arXiv)](https://arxiv.org/abs/2503.11701)
  - Why it matters: helps select variants and identify known failure modes.

## Practical OSS toolchains (local-first)

- Axolotl:
  - [Axolotl GitHub](https://github.com/axolotl-ai-cloud/axolotl)
  - [Axolotl Docs](https://docs.axolotl.ai/)
  - Why useful: mature post-training framework for LoRA/QLoRA and preference tuning.

- Self-Instruct reference code:
  - [yizhongw/self-instruct](https://github.com/yizhongw/self-instruct)
  - Why useful: concrete synthetic data generation and filtering workflow.

- Unsloth docs (practical optimization guidance):
  - [Fine-tuning guide](https://unsloth.ai/docs/get-started/fine-tuning-llms-guide)
  - [LoRA/QLoRA hyperparameter guide](https://unsloth.ai/docs/get-started/fine-tuning-llms-guide/lora-hyperparameters-guide)
  - Why useful: local-first workflows and practical hyperparameter defaults.

## Recommended adoption sequence

1. Baseline with LoRA, then QLoRA only if VRAM-constrained.
2. Start with supervised fine-tuning on high-quality task data.
3. Add synthetic data generation with strict filtering and dedupe.
4. Add preference tuning (DPO) once pairwise preference data exists.
5. Continuously evaluate against held-out regression suites before promotion.

## Key risks to control

- Synthetic data feedback loops:
  - Risk: model reinforces its own errors and style artifacts.
  - Guardrail: mixed-data training (human + synthetic), similarity filtering, and quality gates.

- Catastrophic forgetting:
  - Risk: improved niche behavior but degraded general behavior.
  - Guardrail: hold-out benchmark set and no-regression pass/fail gates.

- Reward/preference overfitting:
  - Risk: model optimizes narrow preference signal at expense of truthfulness.
  - Guardrail: multi-axis eval (helpfulness, factuality, safety, refusal quality).

- Evaluation leakage:
  - Risk: test data leaks into synthetic generation or training corpus.
  - Guardrail: strict train/eval split hygiene and dataset provenance tracking.

- Unsafe autonomous loops:
  - Risk: self-improving loops push unstable weights without review.
  - Guardrail: human review and deterministic promotion gates for every model update.

## Suggested minimum local experiment protocol

- Keep a frozen baseline model + adapter pair.
- Track dataset versions and generation prompts as immutable artifacts.
- Train adapters, not full base weights, by default.
- Run deterministic eval suite before and after tuning.
- Promote only if no-regression checks pass and targeted metric improves.

## Source quality notes

- Prefer `official` paper and repo docs for architecture decisions.
- Use community blog posts for operational hints only.
- Do not adopt numeric claims (speed/quality gains) without local reproduction.
