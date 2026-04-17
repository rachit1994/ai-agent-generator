# Phase Gates

Use this with `00-master-sequence.md` to control progression.

## Phase 0 (Prompts 01-02)
- Contract is consistent with `docs/sde/what.md`.
- Provider defaults to `ollama`.
- Fallback triggers are explicit.
- `gemma 4` is used for this non-implementation phase.

## Phase 1 (Prompts 03-05)
- CLI commands parse correctly.
- Run-id and output directory logic are stable.
- Adapter supports provider abstraction with metadata.
- Implementation uses Python package paths (`src/orchestrator/runtime/...`) rather than TS paths.
- `qwen2.5:7b-instruct` is used for implementation prompts.

## Phase 2 (Prompts 06-07)
- Baseline writes `traces.jsonl` and `summary.json`.
- Input validation fails closed.
- `qwen2.5:7b-instruct` is used for implementation prompts.

## Phase 3 (Prompts 08-12)
- Guarded stage order is enforced.
- Retry cap, timeout cap, token cap, and schema guardrails are enforced.
- Evaluator metrics are deterministic.
- `qwen2.5:7b-instruct` is used for implementation prompts.

## Phase 4 (Prompts 13-16)
- A/B benchmark runs on same suite/provider settings.
- `report.md` verdict is threshold-driven and reproducible.
- `qwen2.5:7b-instruct` is used for implementation prompts.

## Phase 5 (Prompts 17-24)
- Security and performance passes complete.
- Final quality gates pass.
- Final evidence bundle is complete.
- Python test/lint gates are used (`pytest`, Python compile/lint checks).
- `gemma 4` is used for non-implementation/support prompts in this phase.
