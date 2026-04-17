# MVP Decision Report
- run_id: 2026-04-17T10-24-31-166348+00-00-99de0066
- provider: ollama
- mode: both
- implementation_model: qwen2.5:7b-instruct
- support_model: gemma4:latest
- suite: ../../../../data/real-workflow-tasks.jsonl
- suite_version: real-workflow-tasks
- budgets: tokens=4096, retries=1, planner_timeout_ms=5000, verifier_timeout_ms=5000, executor_timeout_ms=8000
- verdict: supported
- recommendation: continue
- pass_rate_delta_points: 70.0
- reliability_delta_points: 70.0
- median_latency_delta_percent: -49.99375156210947

## Baseline Metrics
- passRate: 0.3
- reliability: 0.3
- p50Latency: 16004
- p95Latency: 16004
- avgCost: 0.0
- validityRate: 1.0
- retryFrequency: 0.9

## Guarded Metrics
- passRate: 1.0
- reliability: 1.0
- p50Latency: 8003
- p95Latency: 18011
- avgCost: 0.0
- validityRate: 1.0
- retryFrequency: 0.0

## Per-task deltas
- rw-001: pass_delta=0, latency_delta_ms=3556, baseline_pass=True, guarded_pass=True
- rw-002: pass_delta=1, latency_delta_ms=64, baseline_pass=False, guarded_pass=True
- rw-003: pass_delta=1, latency_delta_ms=1991, baseline_pass=False, guarded_pass=True
- rw-004: pass_delta=0, latency_delta_ms=2530, baseline_pass=True, guarded_pass=True
- rw-005: pass_delta=1, latency_delta_ms=-8002, baseline_pass=False, guarded_pass=True
- rw-006: pass_delta=0, latency_delta_ms=0, baseline_pass=True, guarded_pass=True
- rw-007: pass_delta=1, latency_delta_ms=-8002, baseline_pass=False, guarded_pass=True
- rw-008: pass_delta=1, latency_delta_ms=-8001, baseline_pass=False, guarded_pass=True
- rw-009: pass_delta=1, latency_delta_ms=-8002, baseline_pass=False, guarded_pass=True
- rw-010: pass_delta=1, latency_delta_ms=2007, baseline_pass=False, guarded_pass=True

## Root-cause distribution
- baseline: {'none': 2, 'contract_parse_error': 7, 'refusal_expected': 1}
- guarded_pipeline: {'none': 9, 'refusal_expected': 1}

## Stage latency breakdown (ms)
- baseline: {'executor': 72031, 'repair': 67683, 'finalize': 139715}
- guarded_pipeline: {'planner_doc': 20814, 'planner_prompt': 25017, 'executor': 72017, 'verifier': 0, 'finalize': 117856}

## Incremental ROI
- conservative: 130.0
- base_case: 140.0
- aggressive: 150.0

## Strict gate decision
- decision: continue_and_scale
- checks: {'passRateDelta': True, 'reliabilityDelta': True, 'latencyOverhead': True, 'incrementalRoiBaseCase': True}