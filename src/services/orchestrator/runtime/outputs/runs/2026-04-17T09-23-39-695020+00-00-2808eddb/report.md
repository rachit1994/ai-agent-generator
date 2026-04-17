# MVP Decision Report
- run_id: 2026-04-17T09-23-39-695020+00-00-2808eddb
- provider: ollama
- mode: both
- implementation_model: qwen2.5:7b-instruct
- support_model: gemma4:latest
- suite: ../../../../data/real-workflow-tasks.jsonl
- suite_version: real-workflow-tasks
- budgets: tokens=4096, retries=1, planner_timeout_ms=5000, verifier_timeout_ms=5000, executor_timeout_ms=8000
- verdict: supported
- recommendation: continue
- pass_rate_delta_points: 20.0
- reliability_delta_points: 15.0
- median_latency_delta_percent: -0.006247657128576784

## Baseline Metrics
- passRate: 0.1
- reliability: 0.15
- p50Latency: 16006
- p95Latency: 16011
- avgCost: 0.0
- validityRate: 1.0
- retryFrequency: 0.8

## Guarded Metrics
- passRate: 0.3
- reliability: 0.3
- p50Latency: 16005
- p95Latency: 26053
- avgCost: 0.0
- validityRate: 1.0
- retryFrequency: 0.7

## Per-task deltas
- rw-001: pass_delta=-1, latency_delta_ms=16339, baseline_pass=True, guarded_pass=False
- rw-002: pass_delta=0, latency_delta_ms=10037, baseline_pass=False, guarded_pass=False
- rw-003: pass_delta=0, latency_delta_ms=10034, baseline_pass=False, guarded_pass=False
- rw-004: pass_delta=0, latency_delta_ms=10159, baseline_pass=False, guarded_pass=False
- rw-005: pass_delta=1, latency_delta_ms=-3696, baseline_pass=False, guarded_pass=True
- rw-006: pass_delta=0, latency_delta_ms=0, baseline_pass=False, guarded_pass=False
- rw-007: pass_delta=1, latency_delta_ms=-4562, baseline_pass=False, guarded_pass=True
- rw-008: pass_delta=1, latency_delta_ms=-3382, baseline_pass=False, guarded_pass=True
- rw-009: pass_delta=0, latency_delta_ms=-4, baseline_pass=False, guarded_pass=False
- rw-010: pass_delta=0, latency_delta_ms=10047, baseline_pass=False, guarded_pass=False

## Root-cause distribution
- baseline: {'none': 1, 'contract_parse_error': 7, 'quality_check_fail': 1, 'refusal_expected': 1}
- guarded_pipeline: {'quality_check_fail': 6, 'none': 3, 'refusal_expected': 1}

## Stage latency breakdown (ms)
- baseline: {'executor': 71729, 'finalize': 135676, 'repair': 63945}
- guarded_pipeline: {'planner_doc': 25075, 'planner_prompt': 25106, 'executor': 70936, 'verifier': 10029, 'executor_fix': 49448, 'verifier_fix': 0, 'finalize': 180648}

## Incremental ROI
- conservative: 25.0
- base_case: 35.0
- aggressive: 45.0

## Strict gate decision
- decision: continue_and_scale
- checks: {'passRateDelta': True, 'reliabilityDelta': True, 'latencyOverhead': True, 'incrementalRoiBaseCase': True}