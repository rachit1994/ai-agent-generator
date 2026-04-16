# MVP Overview (Single Source Of Truth)

## Goal

Build a local CLI MVP that tests whether guardrails + a staged execution
pipeline improve outcomes versus a plain one-shot baseline.

Implementation language/runtime:
- Python 3 CLI (`src/services/orchestrator/runtime/agent_mvp` package).

## Timebox And Environment

- Timebox: 2 days.
- Machine constraints:
  - OS: macOS 26.3.1 (Darwin 25.3.0)
  - CPU: Apple M1 (8 cores)
  - RAM: 16 GB
  - Disk available: ~29 GiB

## Model Strategy

- Primary runtime: local `ollama` (no API token required).
- Implementation model: `qwen2.5:7b-instruct` (all coding/execution agents).
- Non-implementation model: `gemma 4` (planning/review/research/support agents).
- Optional local alternate for implementation: `llama3.1:8b-instruct`.
- API fallback: allowed only when documented triggers fire.

## Agent Role Model Assignment

- Use `qwen2.5:7b-instruct` for implementation-critical tasks:
  - writing/refactoring code
  - test authoring and fixes
  - benchmark execution and artifact generation
- Use `gemma 4` for non-implementation tasks:
  - planning and breakdown
  - checklist tracking
  - review summaries and documentation polish
  - analysis and risk enumeration

Fallback triggers:
1. Guarded structured-output validity < 85% after stabilization.
2. Guarded pass rate remains below baseline after two iterations with clear
   model-quality failures.
3. Local median latency is impractical for MVP execution.

If fallback is used, rerun full A/B and document provider/model/reason in
`report.md`.

## Product Surface

CLI commands:
- `sde run --task "..."`
- `sde benchmark --suite ./data/mvp-tasks.jsonl`
- `sde report --run-id <id>`

Modes:
- `baseline`: `task -> model -> output`
- `guarded_pipeline`: `plan -> execute -> verify -> repair(optional) -> finalize`

## Required Guardrails

1. Input validation (non-empty + schema-valid task payload).
2. Output schema validation (fail closed on malformed outputs).
3. Retry cap (maximum one repair retry).
4. Timeout cap (per-task execution limit).
5. Token cap (per-task token budget).
6. Refusal policy for unsafe/invalid actions with machine-readable reason.

## Minimal Architecture

Components:
1. CLI entrypoint + command parser
2. Runner
3. Mode implementations (`baseline`, `guarded_pipeline`)
4. Guardrails
5. Model adapter (`ollama` default, `api` optional fallback)
6. Evaluator
7. Storage (`traces.jsonl`, `summary.json`)
8. Reporter (`report.md`)

Suggested code layout:

```text
src/
  services/
    orchestrator/
      api/
      runtime/
        agent_mvp/
          cli/
          modes/
          config.py
          runner.py
          benchmark.py
          report.py
          model_adapter.py
          safeguards.py
          eval.py
          storage.py
          types.py
      tests/
        unit/
data/
  mvp-tasks.jsonl
outputs/
  runs/<run-id>/
    traces.jsonl
    summary.json
    report.md
```

## Experiment And Verdict Rules

Task suite:
- 10-30 tasks
- includes simple, medium, and failure-prone tasks
- each row has `task_id`, `prompt`, `expected_checks`, `difficulty`

Primary metrics:
- pass rate
- reliability score

Secondary metrics:
- p50/p95 latency
- estimated cost per task
- retry frequency
- structured-output validity rate

Verdict:
- `supported` if pass-rate delta >= 10 points AND reliability improves AND
  median latency degradation <= 30%
- `partially supported` if pass improves but latency/cost degrade materially
- otherwise `rejected` or `inconclusive`

## Required Test Coverage

1. Guardrail unit tests (pass/fail cases for all guardrails).
2. Pipeline integration tests (stage order and trace emission).
3. Benchmark parity tests (same suite/settings/provider per pass).
4. Artifact integrity tests (`traces.jsonl`, `summary.json`, `report.md`).
5. Verdict logic tests (threshold branches).

## In Scope

- Local CLI MVP only.
- A/B benchmark and report generation.
- Traceability and measurable verdict.

## Out Of Scope

- Multi-agent lifecycle systems.
- Distributed/event-sourced production architecture.
- Cloud deployment and scaling.
- UI/dashboard work.
- Production-grade org authz/policy systems.

## Definition Of Done

1. `sde run` succeeds and returns run id.
2. `sde benchmark` runs both modes on same suite.
3. Required artifacts are written per run.
4. `sde report` emits clear verdict and recommendation.
5. Entire flow runs locally within machine constraints.
