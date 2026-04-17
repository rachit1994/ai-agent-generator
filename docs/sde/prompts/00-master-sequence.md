# Master Prompt Sequence

Use each prompt exactly in order. Do not move to the next prompt until the
current prompt's acceptance criteria are met.

Model assignment rule:
- Prompts 01-02 and 17-24 use `gemma 4` (non-implementation/support work).
- Prompts 03-16 use `qwen2.5:7b-instruct` (implementation and delivery work).

## Prompt 01

```text
Read and summarize implementation constraints from:
- docs/sde/what.md
- docs/sde/how-checklist.md

Then produce a concise implementation contract with:
1) scope in/out,
2) exact guardrails,
3) exact pipeline stages,
4) required artifacts and metrics.

Do not write code yet.
Acceptance criteria:
- contract is specific and actionable
- no contradictions with source docs
Output format:
- "Contract"
- "Assumptions"
- "Risks"
```

## Prompt 02

```text
Set up local-model foundation for MVP.
Tasks:
1) verify Ollama is available
2) verify model qwen2.5:7b-instruct availability
3) add or update project config/docs for provider=ollama defaults
4) define API fallback trigger thresholds exactly as documented in scope
```

## Prompt 03

```text
Implement CLI command surface skeleton:
- sde run
- sde benchmark
- sde report
Use Python package structure under `src/services/orchestrator/orchestrator/runtime/cli/`.
Add tests for command parsing and invalid argument handling.
```

## Prompt 04

```text
Implement run-id generation and output directory initialization.
Write deterministic, collision-safe run-id logic and create outputs/runs/<run-id>/.
Add tests for run-id format, uniqueness, and output directory creation behavior.
```

## Prompt 05

```text
Implement model adapter interface with provider abstraction:
- ollama provider (default)
- api provider (fallback-capable, not default)
Require metadata capture: provider, model, provider_base_url.
Add unit tests for provider selection and metadata serialization.
```

## Prompt 06

```text
Implement baseline mode execution:
task -> model -> output
Persist trace and summary minimum fields and validate schemas by tests.
```

## Prompt 07

```text
Add input-validation guardrails:
- non-empty task text
- payload shape validation
Fail closed on invalid inputs.
Add pass/fail tests for validation edge cases.
```

## Prompt 08

```text
Implement guarded pipeline stage 1 and 2:
- plan (ordered steps + acceptance checks)
- execute (candidate answer from steps)
Emit stage-level traces and test stage order.
```

## Prompt 09

```text
Implement guarded pipeline stage 3, 4, 5:
- verify against acceptance checks
- repair optional (max one retry)
- finalize with structured metadata
Add tests for retry cap and finalize schema.
```

## Prompt 10

```text
Implement output-schema guardrail and refusal policy.
Malformed model outputs must fail closed.
Unsafe/invalid actions must produce refusal with machine-readable reason.
```

## Prompt 11

```text
Implement timeout and token budget enforcement across baseline and guarded modes.
Add tests for timeout breach and token-cap breach.
```

## Prompt 12

```text
Implement evaluator primitives:
- pass/fail
- reliability score
- structured-output validity rate
- retry frequency
- latency stats
- estimated cost per task
Add deterministic unit tests.
```

## Prompt 13

```text
Create benchmark suite file at data/benchmark-tasks.jsonl with 10-30 tasks.
Include simple, medium, failure-prone categories and expected_checks field.
Add schema validation for suite rows.
```

## Prompt 14

```text
Implement benchmark runner:
- run suite in baseline
- run suite in guarded_pipeline
- keep provider/model constant per benchmark pass
Persist artifacts per run_id and add integration tests.
```

## Prompt 15

```text
Implement report generator that produces:
- summary.json with aggregate + per-task metrics
- report.md with verdict and recommendation
Implement threshold-driven verdict logic and tests.
```

## Prompt 16

```text
Run smoke validation:
1) sde run baseline
2) sde run guarded_pipeline
3) benchmark with small suite
4) generate report
Fix any failing path immediately.
```

## Prompt 17

```text
Harden error handling and observability:
- normalize error taxonomy
- include actionable error codes
- ensure all failure paths are traced
Add tests for representative failures.
```

## Prompt 18

```text
Security pass:
- verify no secrets are introduced
- verify no credential files are committed
- ensure refusal paths and input validation are never bypassed
```

## Prompt 19

```text
Performance pass:
- profile p50/p95 latency from benchmark outputs
- optimize obvious bottlenecks without changing architecture
- preserve metric correctness
```

## Prompt 20

```text
Determinism and reproducibility pass:
- capture config snapshot in run outputs
- capture provider/model identifiers
- freeze seed/time where feasible for tests
```

## Prompt 21

```text
Final quality gate run:
- python compile/lint checks
- unit tests
- integration tests
- benchmark smoke
Do not proceed if any gate fails; fix and rerun.
```

## Prompt 22

```text
Produce final MVP evidence bundle:
- outputs/runs/<run-id>/traces.jsonl
- outputs/runs/<run-id>/summary.json
- outputs/runs/<run-id>/report.md

Also produce a concise final decision memo in docs/sde/ summarizing:
- verdict
- confidence
- continue/pivot/stop recommendation
```

## Prompt 23 (Fallback: failing tests)

```text
You are in test-recovery mode.
1) list all failing tests
2) classify root causes
3) fix failures with minimal scope changes
4) rerun only affected tests, then full test suite
```

## Prompt 24 (Fallback: missing artifacts or metrics mismatch)

```text
You are in artifact-recovery mode.
1) identify why traces.jsonl / summary.json / report.md are missing or inconsistent
2) fix persistence or metric pipeline
3) regenerate outputs for the last run
4) validate schema and threshold logic
```
