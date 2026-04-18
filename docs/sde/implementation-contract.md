# SDE implementation contract

**In plain words:** this is the **checklist of files and stages** a baseline run is expected to produce. Think “**if these files are missing or empty, the run is incomplete**,” not product marketing. For stricter **V1+** rules (extra artifacts, hard-stops), see **`docs/coding-agent/execution.md`**.

---

## Contract

- In scope: local CLI MVP with `run`, `benchmark`, `report`, and **`replay`**.
- Out of scope: UI, cloud deployment, and production architecture refactors (see also **`what.md`** “Out of scope”).
- Guardrails: input validation, output schema validation, refusal policy, retry cap, timeout cap, token cap, **static code gates** (AST + security patterns + optional `ruff` / `bandit` / `basedpyright` or `pyright` on `PATH`).
- Pipeline stages (sequential, never skipped): `planner_doc -> planner_prompt -> executor -> verifier -> executor_fix(optional, max 1) -> verifier_fix(optional) -> finalize`.
- Required artifacts:
  - per-run traces: `traces.jsonl`, `summary.json`, `report.md`
  - per-run run log: `orchestration.jsonl`, `run.log`
  - per-run **manifest**: `run-manifest.json` (always for `sde run`; task + mode for replay / audit)
  - CTO / V1 gate files: `review.json`, `token_context.json`, **`static_gates_report.json`** (successful parse path)
  - per-run generated outputs (when applicable): `answer.txt`, `generated_script.py`
  - per-run pipeline artifacts (guarded_pipeline): `planner_doc.md`, `executor_prompt.txt`, `verifier_report.json`
- Benchmark runs additionally persist **`benchmark-manifest.json`** and incremental **`benchmark-checkpoint.json`** (per-task progress); CLI supports **`--max-tasks`**, **`--continue-on-error`**, and **`--resume-run-id`** (same `outputs/runs/<id>` directory; suite path and mode must match the manifest).
- Required metrics: pass rate, reliability, p50/p95 latency, estimated cost, validity rate, retry frequency.

**Feature status vs upstream harnesses:** [`core-features-and-upstream-parity.md`](core-features-and-upstream-parity.md).

## Assumptions

- Local runtime uses Ollama by default.
- Implementation model is `qwen3:14b`; support model is `gemma 4`.
- API provider exists only as fallback and must be explicitly justified in report.

## Risks

- Missing local model pulls can block benchmark execution.
- Non-JSON model outputs can fail closed and reduce pass rate.
- Latency may regress under guarded mode due to extra stages.
