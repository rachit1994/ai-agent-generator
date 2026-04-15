# Contract

- In scope: local CLI MVP with `run`, `benchmark`, and `report`.
- Out of scope: UI, cloud deployment, and production architecture refactors.
- Guardrails: input validation, output schema validation, refusal policy, retry cap, timeout cap, token cap.
- Pipeline stages: `plan -> execute -> verify -> repair(optional) -> finalize`.
- Required artifacts: `traces.jsonl`, `summary.json`, `report.md`.
- Required metrics: pass rate, reliability, p50/p95 latency, estimated cost, validity rate, retry frequency.

# Assumptions

- Local runtime uses Ollama by default.
- Implementation model is `qwen2.5:7b-instruct`; support model is `gemma 4`.
- API provider exists only as fallback and must be explicitly justified in report.

# Risks

- Missing local model pulls can block benchmark execution.
- Non-JSON model outputs can fail closed and reduce pass rate.
- Latency may regress under guarded mode due to extra stages.
