# A/B Protocol And Controls

## Goal
Measure whether the current orchestrated pipeline is materially better than direct model usage.

## Strict Decision Profile
- Pass-rate delta: `>= +15.0` percentage points (guarded - baseline)
- Reliability delta: `>= +15.0` percentage points
- Median latency delta: `<= +25.0%`
- Incremental ROI: `> 0` in base-case economics

All four conditions must pass for a `continue_and_scale` outcome.

## Fixed Controls
- Same task suite for A and B runs
- Same model (`qwen2.5:7b-instruct`) and provider (`ollama`)
- Same guardrail budgets and retry limits
- Same machine and runtime profile
- Same scoring logic (`summary.json` metrics)

## Runs Executed
1. Synthetic suite run A:
   - run_id: `2026-04-17T09-13-13-321916+00-00-58e32b49`
   - suite: `data/benchmark-tasks.jsonl`
2. Synthetic suite run B (reproducibility pass):
   - run_id: `2026-04-17T09-18-26-539178+00-00-449ebc7d`
   - suite: `data/benchmark-tasks.jsonl`
3. Real-workflow suite run A:
   - run_id: `2026-04-17T09-23-39-695020+00-00-2808eddb`
   - suite: `data/real-workflow-tasks.jsonl`
4. Real-workflow suite run B (reproducibility pass):
   - run_id: `2026-04-17T09-29-04-855234+00-00-21a17b33`
   - suite: `data/real-workflow-tasks.jsonl`

## Notes
- Timeouts were bounded to keep experiments operational in this environment:
  - planner: `5000ms`
  - verifier: `5000ms`
  - executor: `8000ms`
- Guarded mode includes a simple-task fast path to reduce avoidable orchestration overhead on low-complexity prompts.
