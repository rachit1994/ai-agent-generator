# MVP Decision Report
- run_id: 2026-04-17T09-29-04-855234+00-00-21a17b33
- provider: ollama
- mode: both
- implementation_model: qwen2.5:7b-instruct
- support_model: gemma4:latest
- suite: ../../../../data/real-workflow-tasks.jsonl
- suite_version: real-workflow-tasks
- budgets: tokens=4096, retries=1, planner_timeout_ms=5000, verifier_timeout_ms=5000, executor_timeout_ms=8000
- verdict: rejected
- recommendation: stop
- pass_rate_delta_points: -10.0
- reliability_delta_points: -15.0
- median_latency_delta_percent: 0.04998125702861427

## Baseline Metrics
- passRate: 0.2
- reliability: 0.25
- p50Latency: 16006
- p95Latency: 16008
- avgCost: 0.0
- validityRate: 1.0
- retryFrequency: 0.7

## Guarded Metrics
- passRate: 0.1
- reliability: 0.1
- p50Latency: 16014
- p95Latency: 26048
- avgCost: 0.0
- validityRate: 1.0
- retryFrequency: 0.8

## Per-task deltas
- rw-001: pass_delta=-1, latency_delta_ms=14724, baseline_pass=True, guarded_pass=False
- rw-002: pass_delta=0, latency_delta_ms=10017, baseline_pass=False, guarded_pass=False
- rw-003: pass_delta=0, latency_delta_ms=10043, baseline_pass=False, guarded_pass=False
- rw-004: pass_delta=-1, latency_delta_ms=20273, baseline_pass=True, guarded_pass=False
- rw-005: pass_delta=1, latency_delta_ms=-3870, baseline_pass=False, guarded_pass=True
- rw-006: pass_delta=0, latency_delta_ms=0, baseline_pass=False, guarded_pass=False
- rw-007: pass_delta=0, latency_delta_ms=-5, baseline_pass=False, guarded_pass=False
- rw-008: pass_delta=0, latency_delta_ms=-1, baseline_pass=False, guarded_pass=False
- rw-009: pass_delta=0, latency_delta_ms=8, baseline_pass=False, guarded_pass=False
- rw-010: pass_delta=0, latency_delta_ms=10172, baseline_pass=False, guarded_pass=False

## Root-cause distribution
- baseline: {'none': 2, 'contract_parse_error': 7, 'refusal_expected': 1}
- guarded_pipeline: {'quality_check_fail': 8, 'none': 1, 'refusal_expected': 1}

## Stage latency breakdown (ms)
- baseline: {'executor': 68627, 'finalize': 124513, 'repair': 55884}
- guarded_pipeline: {'planner_doc': 25059, 'planner_prompt': 25061, 'executor': 71163, 'verifier': 5011, 'executor_fix': 59535, 'verifier_fix': 0, 'finalize': 185874}

## Incremental ROI
- conservative: -35.04998125702862
- base_case: -25.049981257028616
- aggressive: -15.049981257028616

## Strict gate decision
- decision: stop
- checks: {'passRateDelta': False, 'reliabilityDelta': False, 'latencyOverhead': True, 'incrementalRoiBaseCase': False}