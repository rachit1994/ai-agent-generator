# Swarm Token and Minimum System Requirements Math (Master-Aligned)

**In plain words:** this page is **spreadsheet thinking in sentences** — how to budget **tokens and money**, protect room for **safety and evaluation**, and size a **local machine** when many model calls run in parallel. Skim the **headings** first; dive into formulas only when you are sizing a workload.

This model is aligned to `docs/architecture/AI-Professional-Evolution-Master-Architecture.md`:

- equal quality/cost objective arbitration,
- protected learning/practice quotas,
- local-prod deterministic constraints,
- hard release-gate budgets and fail-closed behavior.

## 1) Balanced Utility (Equal Quality and Cost Effectiveness)

Per role or service lane `i`:

- `Q_i` quality score in `[0, 1]` (reliability-weighted, repeated-run aware)
- `C_i` USD per successful trajectory
- `CE_i = 1 / C_i`

Normalize in current planning window:

- `Qn_i = (Q_i - Q_min) / (Q_max - Q_min + eps)`
- `CEn_i = (CE_i - CE_min) / (CE_max - CE_min + eps)`

Equal distribution utility:

- `U_i = 0.5 * Qn_i + 0.5 * CEn_i`

Budget weight:

- `W_i = U_i / sum(U_k)`

Constraint:

- if role `i` is protected (`safety`, `evaluation`, `learning`, `practice`),
  `W_i` must respect hard floors (Section 4).

## 2) Swarm Token Throughput Math

Per role `i`:

- `A_i` concurrent agents
- `R_i` requests/minute/agent
- `T_in_i`, `T_out_i` average tokens per request

Throughput:

- `TPM_i = A_i * R_i * (T_in_i + T_out_i)`
- `TPH_i = 60 * TPM_i`

Global:

- `TPM_total = sum(TPM_i)`
- `TPH_total = sum(TPH_i)`
- `T_day = 24 * TPH_total`

## 3) Token Cost Math

Per role `i` pricing:

- `P_in_i` USD / 1M input tokens
- `P_out_i` USD / 1M output tokens

Role spend:

- `Cost_h_i = A_i * R_i * 60 * (T_in_i * P_in_i + T_out_i * P_out_i) / 1_000_000`
- `Cost_d_i = 24 * Cost_h_i`

Swarm spend:

- `Cost_h_total = sum(Cost_h_i)`
- `Cost_d_total = sum(Cost_d_i)`

## 4) Master Required Budget Floors (Non-Negotiable)

To preserve safety, evaluation, and long-horizon growth:

- `W_safety + W_policy + W_identity_authz >= 0.15`
- `W_evaluation + W_observability >= 0.15`
- `W_learning + W_practice >= 0.20` (protected practice capacity contract)
- `W_incident_ops + W_chaos >= 0.05`

Remaining share:

- `W_execution + W_review + W_management + W_specialist + W_strategy`
  gets `<= 0.45`, distributed by `U_i`.

These floors are enforced before utility-based redistribution.

## 5) Quality-Constrained Cost Optimization

Minimize:

- `min sum(Cost_h_i)`

Subject to:

- `sum(W_i * Q_i) >= Q_target`
- `sum(W_i) = 1`
- all hard floors from Section 4
- `UnsafeActionRate <= 0.02`
- `ResourceBudgetBreaches == 0`

If constraints are infeasible:

1. Reduce execution throughput first.
2. Keep protected floors unchanged.
3. Trigger scale-up or model router fallback policy.

## 6) Minimum System Requirements Math (local-prod)

Variables:

- `N` total active agents
- `lambda` requests/second/agent
- `S_tok` tokens/request
- `tau` effective tokens/second/core
- `m` GB memory/active agent
- `b` baseline memory GB
- `d` GB storage per 1M tokens
- `sf_cpu`, `sf_mem` safety factors

### 6.1 CPU

- `TR = N * lambda * S_tok`
- `Cores_min = ceil((TR / tau) * sf_cpu)`

### 6.2 Memory

- `RAM_min_GB = ceil((b + N * m) * sf_mem)`

### 6.3 Storage

- `Disk_day_GB = (T_day / 1_000_000) * d`
- `Disk_30d_GB = 30 * Disk_day_GB`
- `Disk_total_GB = Disk_30d_GB * (1 + oh)` where `oh` is index/snapshot overhead

### 6.4 Network

- `Net_Bps = TR * bt * nf`
- `Net_Mbps = (Net_Bps * 8) / 1_000_000`
- `Bandwidth_min = p95(Net_Mbps) * 1.5`

## 7) Example - Master-Compatible Mid Swarm

Assume:

- `N = 30`
- `lambda = 0.07`
- `S_tok = 3200`
- `tau = 190`
- `m = 0.40`
- `b = 8`
- `sf_cpu = 1.30`
- `sf_mem = 1.25`
- `d = 0.85`
- `oh = 0.30`
- `bt = 6`
- `nf = 1.40`

Compute:

- `TR = 30 * 0.07 * 3200 = 6720 tokens/s`
- `Cores_min = ceil((6720 / 190) * 1.30) = ceil(45.98) = 46`
- `RAM_min_GB = ceil((8 + 30 * 0.40) * 1.25) = ceil(25) = 25`

If `T_day = 580,608,000` tokens/day:

- `Disk_day_GB = 580.608 * 0.85 = 493.52 GB/day`
- `Disk_30d_GB = 14,805.6 GB`
- `Disk_total_GB = 14,805.6 * 1.30 = 19,247.28 GB`

Minimum practical envelope:

- `48 vCPU`
- `32 GB RAM`
- `20 TB usable disk`
- `1 Gbps NIC`

## 8) Role Allocation Template (Master Role Set)

Use these lanes for weights:

- execution: `junior`, `midlevel`, `senior`, `architect`
- review and governance: `reviewer`, `evaluator`, `manager`
- growth: `learning`, `practice`, `career-strategy`
- reliability and safety services: `safety`, `policy`, `identity-authz`,
  `incident-ops`, `chaos`, `observability`

Daily allocation algorithm:

1. Compute `U_i` from observed quality and cost.
2. Apply hard floors from Section 4.
3. Distribute remaining budget by normalized `U_i`.
4. Recompute expected gates (`UnsafeActionRate`, resource breaches).
5. If any gate fails, reject plan and reallocate (fail-closed).

## 9) Operational SLO Guardrails

- p95 token utilization <= `70%`
- p95 CPU <= `65%`
- incident detect p95 <= `60s`
- containment p95 <= `180s`
- rollback activation p95 <= `120s`
- rollback verification p95 <= `15m`
- `ReplayCriticalDriftCount == 0`
- `CriticalPolicyDriftIncidents == 0`

Any breach freezes promotion/autonomy expansion budgets until green again.

## 10) Recommended LLM Stack (Cloud + Local)

Use a tiered router so each role gets the cheapest model that still satisfies
quality and safety gates.

### 10.1 Model Tiers

- Tier A (high-risk, high-reasoning): architecture, evaluator final pass, safety decisions.
- Tier B (balanced): normal execution, review, learning synthesis.
- Tier C (low-cost, high-throughput): formatting, summaries, lightweight retries.
- Tier L (local/private path): deterministic local-prod fallback and privacy-sensitive workloads.

### 10.2 Suggested Cloud Models by Tier

Map by capability class, not vendor lock-in:

- Tier A:
  - OpenAI `o3` or `gpt-5` class
  - Anthropic `Claude Opus` class
  - Google `Gemini 2.5 Pro` class
- Tier B:
  - OpenAI `gpt-4.1` class
  - Anthropic `Claude Sonnet` class
  - Google `Gemini 2.5 Flash` class
- Tier C:
  - OpenAI `gpt-4.1-mini` class
  - Anthropic `Claude Haiku` class
  - Google `Gemini Flash-lite` class

### 10.3 Suggested Local LLMs

For local-first and cost control (use **published** Ollama tags only; verify with `ollama pull <tag>` before relying on them in CI):

- reasoning local:
  - `qwen3:32b` or `qwen3:30b` (when GPU budget allows; see [Ollama `qwen3`](https://ollama.com/library/qwen3))
  - `Llama 3.3 70B Instruct` (when GPU budget allows)
- balanced local:
  - `qwen3:14b` (matches SDE default in `src/sde_pipeline/config.py`)
  - `Mistral Small` class
- throughput local:
  - `qwen3:8b` or `qwen3:4b`
  - `Llama 3.1 8B Instruct`
- legacy fallback (still on registry): `qwen2.5:*-instruct` if you must pin the prior generation.

Embedding/rerank local pair:

- embeddings: `bge-m3` or `e5-large`
- rerank: `bge-reranker-v2`

### 10.4 Role -> Model Routing Recommendation

- `safety`, `policy`, `identity-authz`, promotion committee decisions:
  - primary Tier A cloud, fallback Tier A/B local (if policy allows).
- `evaluator`, `reviewer`, `architect`, `career-strategy`:
  - primary Tier A/B, fallback Tier B.
- `senior`, `midlevel`, `learning`, `practice`:
  - primary Tier B, fallback Tier C/local balanced.
- `junior`, low-risk execution retries, summarization:
  - primary Tier C or local throughput.
- `incident-ops` during active containment:
  - Tier A required for decision quality; Tier B for non-critical support tasks.

### 10.5 Budget Split Across Model Tiers (Equal Quality/Cost Policy)

Practical default starting point aligned with Sections 1-5:

- Tier A: `20-25%` of tokens (quality-critical paths only)
- Tier B: `45-55%` of tokens (main production work)
- Tier C: `15-20%` of tokens (bulk low-risk tasks)
- Tier L local: `10-20%` baseline, increase as local quality reaches gates

Keep protected-role floors from Section 4 unchanged while optimizing.

### 10.6 Minimum Local Hardware by Model Class

Indicative baseline for inference-only deployment:

- 8B class:
  - 1 GPU with `>=16 GB` VRAM (or CPU-only with lower throughput)
- 14B class:
  - 1 GPU with `>=24 GB` VRAM
- 32B class:
  - 2x48 GB GPU or 4x24 GB GPU
- 70B class:
  - 4x80 GB GPU (or equivalent distributed setup)

If local GPU is constrained, keep Tier A on cloud and shift Tier C first to local.

### 10.7 Failover Policy

- Step 1: same tier fallback (provider/model switch).
- Step 2: one tier down only if role risk class permits.
- Step 3: if quality floor fails, escalate/defer (do not force completion on cheaper model).
- Step 4: log route decision artifact in event lineage for replay and audit.
