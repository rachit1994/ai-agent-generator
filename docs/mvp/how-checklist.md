# MVP Atomic Checklist

Follow this checklist in order. Do not start a later phase until all checkboxes in the current phase are complete.

## Phase 0 - Preconditions

- [ ] Confirm machine constraints are documented for this run (OS, CPU, RAM, disk).
- [ ] Install Ollama locally.
- [ ] Start Ollama server.
- [ ] Pull local implementation model `qwen2.5:7b-instruct`.
- [ ] Pull local support-agent model `gemma 4`.
- [ ] Run a local health check with one Ollama generation.
- [ ] Set model provider to `ollama` for default benchmark runs.
- [ ] Set model policy: use `qwen2.5:7b-instruct` for implementation agents and `gemma 4` for non-implementation agents.
- [ ] Set a maximum token budget for one task execution.
- [ ] Set a maximum retry budget for one task execution.
- [ ] Set a timeout budget for one task execution.
- [ ] Create `data/` if it does not exist.
- [ ] Create `outputs/runs/` if it does not exist.
- [ ] Confirm out-of-scope work is excluded (UI, cloud deploy, production architecture refactor).
- [ ] Record fallback trigger rules for API model switch in run config.
  - Verification: config includes validity threshold, latency trigger, and rerun rule.

## Phase 1 - CLI Skeleton And Single Task Run

- [ ] Create CLI entrypoint module under `src/cli/`.
- [ ] Add `agent run` command parsing.
- [ ] Add `agent benchmark` command parsing.
- [ ] Add `agent report` command parsing.
- [ ] Create run-id generation utility.
- [ ] Create per-run output directory at `outputs/runs/<run-id>/`.
- [ ] Add model adapter invocation path.
- [ ] Wire `agent run --task "<text>" --mode baseline|guarded_pipeline` to runner input.
- [ ] Execute `agent run --task "hello" --mode baseline`.
  - Verification: CLI prints a result and a `run_id`.

## Phase 2 - Baseline Mode

- [ ] Implement baseline one-shot task execution path.
- [ ] Record `run_id` in trace output.
- [ ] Record `task_id` in trace output.
- [ ] Record `mode` in trace output.
- [ ] Record `model` in trace output.
- [ ] Record `started_at` in trace output.
- [ ] Record `ended_at` in trace output.
- [ ] Record `latency_ms` in trace output.
- [ ] Record `token_input` in trace output.
- [ ] Record `token_output` in trace output.
- [ ] Record `estimated_cost_usd` in trace output.
- [ ] Record `retry_count` in trace output.
- [ ] Record `errors[]` in trace output.
- [ ] Record `score` object in trace output.
- [ ] Write per-step trace events to `outputs/runs/<run-id>/traces.jsonl`.
- [ ] Write aggregate summary to `outputs/runs/<run-id>/summary.json`.
- [ ] Run 3 sample tasks in baseline mode.
  - Verification: each sample run writes both `traces.jsonl` and `summary.json`.

## Phase 3 - Guarded Pipeline Mode

- [ ] Implement planner stage that outputs ordered steps.
- [ ] Implement planner stage acceptance checks output.
- [ ] Implement executor stage that uses planner steps.
- [ ] Implement verifier stage that checks execution against acceptance checks.
- [ ] Implement optional repair stage with max one retry.
- [ ] Enforce output schema validation before finalize.
- [ ] Enforce retry budget cap for guarded mode.
- [ ] Enforce timeout budget cap for guarded mode.
- [ ] Emit stage-level trace entries for planner.
- [ ] Emit stage-level trace entries for executor.
- [ ] Emit stage-level trace entries for verifier.
- [ ] Emit stage-level trace entries for repair attempt (when used).
- [ ] Emit final structured metadata for guarded mode output.
- [ ] Run the same 3 sample tasks in guarded mode.
  - Verification: all runs complete and produce `traces.jsonl` plus `summary.json`.

## Phase 4 - Benchmark Harness

- [ ] Create task suite file at `data/mvp-tasks.jsonl`.
- [ ] Add `task_id` for each task row.
- [ ] Add `prompt` for each task row.
- [ ] Add `expected_checks` for each task row.
- [ ] Add `difficulty` for each task row.
- [ ] Ensure suite size is between 10 and 30 tasks.
- [ ] Ensure suite includes at least one simple task.
- [ ] Ensure suite includes at least one medium task.
- [ ] Ensure suite includes at least one failure-prone task.
- [ ] Execute `agent benchmark --suite ./data/mvp-tasks.jsonl` in baseline mode.
- [ ] Execute `agent benchmark --suite ./data/mvp-tasks.jsonl` in guarded_pipeline mode.
- [ ] Generate run summary JSON artifacts for both modes.
- [ ] Generate per-run markdown report artifact for both modes.

## Phase 5 - Metrics And Decision Report

- [ ] Compute task pass rate for baseline.
- [ ] Compute task pass rate for guarded_pipeline.
- [ ] Compute reliability score for baseline.
- [ ] Compute reliability score for guarded_pipeline.
- [ ] Compute p50 latency for baseline.
- [ ] Compute p50 latency for guarded_pipeline.
- [ ] Compute p95 latency for baseline.
- [ ] Compute p95 latency for guarded_pipeline.
- [ ] Compute estimated cost per task for baseline.
- [ ] Compute estimated cost per task for guarded_pipeline.
- [ ] Compute structured-output validity rate for baseline.
- [ ] Compute structured-output validity rate for guarded_pipeline.
- [ ] Compute retry frequency for baseline.
- [ ] Compute retry frequency for guarded_pipeline.
- [ ] Compute pass-rate delta in percentage points (guarded - baseline).
- [ ] Compute median latency delta percent.
- [ ] Mark verdict as `supported` if pass-rate delta >= 10 points, reliability improves, and median latency degradation <= 30%.
- [ ] Mark verdict as `partially supported` if pass rate improves but latency or cost is materially worse.
- [ ] Mark verdict as `rejected` if guarded does not improve practical outcomes.
- [ ] Mark verdict as `inconclusive` if evidence quality is insufficient or run quality is unstable.
- [ ] Write final report to `outputs/runs/<run-id>/report.md`.
- [ ] Ensure report includes model, budgets, and suite version.
- [ ] Ensure report includes aggregate A/B metrics.
- [ ] Ensure report includes per-task deltas.
- [ ] Ensure report includes recommendation: continue, pivot, or stop.

## Phase 6 - Definition Of Done Gate

- [ ] Confirm `agent run` completes a single task and prints result plus run id.
- [ ] Confirm benchmark suite runs in baseline mode.
- [ ] Confirm benchmark suite runs in guarded_pipeline mode.
- [ ] Confirm per-task traces are persisted for benchmark runs.
- [ ] Confirm aggregate summaries are persisted for benchmark runs.
- [ ] Confirm machine-readable scorecard data exists in summary outputs.
- [ ] Confirm one markdown report states supported/rejected/inconclusive.
- [ ] Confirm the full flow runs locally within practical machine limits.
- [ ] Confirm all four non-negotiable MVP outcomes are satisfied.
