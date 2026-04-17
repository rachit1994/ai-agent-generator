# MVP Decision Report
- run_id: 2026-04-17T09-54-00-147652+00-00-d498eac3
- provider: ollama
- mode: both
- implementation_model: qwen2.5:7b-instruct
- support_model: gemma4:latest
- suite: ../../../../data/real-workflow-tasks.jsonl
- suite_version: real-workflow-tasks
- budgets: tokens=4096, retries=1, planner_timeout_ms=5000, verifier_timeout_ms=5000, executor_timeout_ms=8000
- verdict: rejected
- recommendation: stop
- pass_rate_delta_points: 0.0
- reliability_delta_points: 0.0
- median_latency_delta_percent: 0.07498125468632841

## Baseline Metrics
- passRate: 0.2
- reliability: 0.2
- p50Latency: 16004
- p95Latency: 16021
- avgCost: 0.0
- validityRate: 1.0
- retryFrequency: 0.7

## Guarded Metrics
- passRate: 0.2
- reliability: 0.2
- p50Latency: 16016
- p95Latency: 26044
- avgCost: 0.0
- validityRate: 1.0
- retryFrequency: 0.7

## Per-task deltas
- rw-001: pass_delta=-1, latency_delta_ms=14809, baseline_pass=True, guarded_pass=False
- rw-002: pass_delta=0, latency_delta_ms=10023, baseline_pass=False, guarded_pass=False
- rw-003: pass_delta=0, latency_delta_ms=10034, baseline_pass=False, guarded_pass=False
- rw-004: pass_delta=-1, latency_delta_ms=19327, baseline_pass=True, guarded_pass=False
- rw-005: pass_delta=1, latency_delta_ms=-3796, baseline_pass=False, guarded_pass=True
- rw-006: pass_delta=0, latency_delta_ms=1, baseline_pass=False, guarded_pass=False
- rw-007: pass_delta=0, latency_delta_ms=-11, baseline_pass=False, guarded_pass=False
- rw-008: pass_delta=1, latency_delta_ms=-3155, baseline_pass=False, guarded_pass=True
- rw-009: pass_delta=0, latency_delta_ms=-1, baseline_pass=False, guarded_pass=False
- rw-010: pass_delta=0, latency_delta_ms=10040, baseline_pass=False, guarded_pass=False

## Root-cause distribution
- baseline: {'none': 2, 'contract_parse_error': 7, 'refusal_expected': 1}
- guarded_pipeline: {'quality_check_fail': 7, 'none': 2, 'refusal_expected': 1}

## Stage latency breakdown (ms)
- baseline: {'executor': 70033, 'finalize': 126079, 'repair': 56041}
- guarded_pipeline: {'planner_doc': 25062, 'planner_prompt': 25071, 'executor': 71072, 'verifier': 10027, 'executor_fix': 52059, 'verifier_fix': 0, 'finalize': 183350}

## Incremental ROI
- conservative: -10.074981254686328
- base_case: -0.07498125468632841
- aggressive: 9.925018745313672

## Strict gate decision
- decision: stop
- checks: {'passRateDelta': False, 'reliabilityDelta': False, 'latencyOverhead': True, 'incrementalRoiBaseCase': False}