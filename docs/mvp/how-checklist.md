# MVP Atomic Checklist

Follow this checklist in order. Do not start a later phase until all checkboxes in the current phase are complete.

## Phase 0 - Preconditions

- [x] Confirm machine constraints are documented for this run (OS, CPU, RAM, disk).
- [x] Install Ollama locally.
- [x] Start Ollama server.
- [x] Pull local implementation model `qwen2.5:7b-instruct`.
- [x] Pull local support-agent model `gemma 4`.
- [x] Run a local health check with one Ollama generation.
- [x] Set model provider to `ollama` for default benchmark runs.
- [x] Set model policy: use `qwen2.5:7b-instruct` for implementation agents and `gemma 4` for non-implementation agents.
- [x] Set a maximum token budget for one task execution.
- [x] Set a maximum retry budget for one task execution.
- [x] Set a timeout budget for one task execution.
- [x] Create `data/` if it does not exist.
- [x] Create `outputs/runs/` if it does not exist.
- [x] Confirm out-of-scope work is excluded (UI, cloud deploy, production architecture refactor).
- [x] Record fallback trigger rules for API model switch in run config.
  - Verification: config includes validity threshold, latency trigger, and rerun rule.

## Phase 1 - CLI Skeleton And Single Task Run

- [x] Create CLI entrypoint module under `src/services/orchestrator/runtime/agent_mvp/cli/`.
- [x] Add `sde run` command parsing.
- [x] Add `sde benchmark` command parsing.
- [x] Add `sde report` command parsing.
- [x] Create run-id generation utility.
- [x] Create per-run output directory at `outputs/runs/<run-id>/`.
- [x] Add model adapter invocation path.
- [x] Wire `sde run --task "<text>" --mode baseline|guarded_pipeline` to runner input.
- [x] Execute `sde run --task "hello" --mode baseline`.
  - Verification: CLI prints a result and a `run_id`.

## Phase 2 - Baseline Mode

- [x] Implement baseline one-shot task execution path.
- [x] Record `run_id` in trace output.
- [x] Record `task_id` in trace output.
- [x] Record `mode` in trace output.
- [x] Record `model` in trace output.
- [x] Record `started_at` in trace output.
- [x] Record `ended_at` in trace output.
- [x] Record `latency_ms` in trace output.
- [x] Record `token_input` in trace output.
- [x] Record `token_output` in trace output.
- [x] Record `estimated_cost_usd` in trace output.
- [x] Record `retry_count` in trace output.
- [x] Record `errors[]` in trace output.
- [x] Record `score` object in trace output.
- [x] Write per-step trace events to `outputs/runs/<run-id>/traces.jsonl`.
- [x] Write aggregate summary to `outputs/runs/<run-id>/summary.json`.
- [x] Run 3 sample tasks in baseline mode.
  - Verification: each sample run writes both `traces.jsonl` and `summary.json`.

## Phase 3 - Guarded Pipeline Mode

- [x] Enforce strict sequential stages (no skipping).
- [x] Planner is called twice for every guarded run:
  - [x] `planner_doc`: produces a planning document (written to `planner_doc.md`).
  - [x] `planner_prompt`: produces an executor-ready prompt with prompt-engineering guidelines (written to `executor_prompt.txt`).
- [x] `executor`: generates output using the planner prompt (and planner doc context).
- [x] `verifier`: verifies executor output against planner outputs and task requirements.
- [x] `executor_fix` (optional, max one retry): re-asks executor with a fixed prompt to address security, performance, and edge cases.
- [x] `verifier_fix` (optional): verifies the fixed output.
- [x] `finalize`: emits final structured metadata.
- [x] Enforce retry budget cap for guarded mode.
- [x] Enforce timeout budget cap for guarded mode.
- [x] Emit stage-level trace entries for all stages.
- [x] Emit final structured metadata for guarded mode output.
- [x] Run the same 3 sample tasks in guarded mode.
  - Verification: all runs complete and produce `traces.jsonl` plus `summary.json`.

## Phase 4 - Benchmark Harness

- [x] Create task suite file at `data/mvp-tasks.jsonl`.
- [x] Add `task_id` for each task row.
- [x] Add `prompt` for each task row.
- [x] Add `expected_checks` for each task row.
- [x] Add `difficulty` for each task row.
- [x] Ensure suite size is between 10 and 30 tasks.
- [x] Ensure suite includes at least one simple task.
- [x] Ensure suite includes at least one medium task.
- [x] Ensure suite includes at least one failure-prone task.
- [x] Execute `sde benchmark --suite ./data/mvp-tasks.jsonl` in baseline mode.
- [x] Execute `sde benchmark --suite ./data/mvp-tasks.jsonl` in guarded_pipeline mode.
- [x] Generate run summary JSON artifacts for both modes.
- [x] Generate per-run markdown report artifact for both modes.

## Phase 5 - Metrics And Decision Report

- [x] Compute task pass rate for baseline.
- [x] Compute task pass rate for guarded_pipeline.
- [x] Compute reliability score for baseline.
- [x] Compute reliability score for guarded_pipeline.
- [x] Compute p50 latency for baseline.
- [x] Compute p50 latency for guarded_pipeline.
- [x] Compute p95 latency for baseline.
- [x] Compute p95 latency for guarded_pipeline.
- [x] Compute estimated cost per task for baseline.
- [x] Compute estimated cost per task for guarded_pipeline.
- [x] Compute structured-output validity rate for baseline.
- [x] Compute structured-output validity rate for guarded_pipeline.
- [x] Compute retry frequency for baseline.
- [x] Compute retry frequency for guarded_pipeline.
- [x] Compute pass-rate delta in percentage points (guarded - baseline).
- [x] Compute median latency delta percent.
- [x] Mark verdict as `supported` if pass-rate delta >= 10 points, reliability improves, and median latency degradation <= 30%.
- [x] Mark verdict as `partially supported` if pass rate improves but latency or cost is materially worse.
- [x] Mark verdict as `rejected` if guarded does not improve practical outcomes.
- [x] Mark verdict as `inconclusive` if evidence quality is insufficient or run quality is unstable.
- [x] Write final report to `outputs/runs/<run-id>/report.md`.
- [x] Ensure report includes model, budgets, and suite version.
- [x] Ensure report includes aggregate A/B metrics.
- [x] Ensure report includes per-task deltas.
- [x] Ensure report includes recommendation: continue, pivot, or stop.

## Phase 6 - Definition Of Done Gate

- [x] Confirm `sde run` completes a single task and prints result plus run id.
- [x] Confirm benchmark suite runs in baseline mode.
- [x] Confirm benchmark suite runs in guarded_pipeline mode.
- [x] Confirm per-task traces are persisted for benchmark runs.
- [x] Confirm aggregate summaries are persisted for benchmark runs.
- [x] Confirm machine-readable scorecard data exists in summary outputs.
- [x] Confirm one markdown report states supported/rejected/inconclusive.
- [x] Confirm the full flow runs locally within practical machine limits.
- [x] Confirm all four non-negotiable MVP outcomes are satisfied.
