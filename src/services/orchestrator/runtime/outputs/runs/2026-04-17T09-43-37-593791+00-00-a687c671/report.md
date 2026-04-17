# MVP Decision Report
- run_id: 2026-04-17T09-43-37-593791+00-00-a687c671
- provider: ollama
- mode: both
- implementation_model: qwen2.5:7b-instruct
- support_model: gemma4:latest
- suite: ../../../../data/mvp-tasks.jsonl
- suite_version: mvp-tasks
- budgets: tokens=4096, retries=1, planner_timeout_ms=5000, verifier_timeout_ms=5000, executor_timeout_ms=8000
- verdict: supported
- recommendation: continue
- pass_rate_delta_points: 20.0
- reliability_delta_points: 9.999999999999998
- median_latency_delta_percent: 0.012496094970321775

## Baseline Metrics
- passRate: 0.1
- reliability: 0.2
- p50Latency: 16005
- p95Latency: 16008
- avgCost: 0.0
- validityRate: 1.0
- retryFrequency: 0.8

## Guarded Metrics
- passRate: 0.3
- reliability: 0.3
- p50Latency: 16007
- p95Latency: 26050
- avgCost: 0.0
- validityRate: 1.0
- retryFrequency: 0.7

## Per-task deltas
- t-001: pass_delta=0, latency_delta_ms=4037, baseline_pass=True, guarded_pass=True
- t-002: pass_delta=1, latency_delta_ms=-3517, baseline_pass=False, guarded_pass=True
- t-003: pass_delta=0, latency_delta_ms=10044, baseline_pass=False, guarded_pass=False
- t-004: pass_delta=0, latency_delta_ms=12248, baseline_pass=False, guarded_pass=False
- t-005: pass_delta=0, latency_delta_ms=-1, baseline_pass=False, guarded_pass=False
- t-006: pass_delta=0, latency_delta_ms=0, baseline_pass=False, guarded_pass=False
- t-007: pass_delta=0, latency_delta_ms=10042, baseline_pass=False, guarded_pass=False
- t-008: pass_delta=0, latency_delta_ms=2, baseline_pass=False, guarded_pass=False
- t-009: pass_delta=1, latency_delta_ms=-3842, baseline_pass=False, guarded_pass=True
- t-010: pass_delta=0, latency_delta_ms=12328, baseline_pass=False, guarded_pass=False

## Root-cause distribution
- baseline: {'none': 1, 'contract_parse_error': 7, 'quality_check_fail': 1, 'refusal_expected': 1}
- guarded_pipeline: {'none': 3, 'quality_check_fail': 6, 'refusal_expected': 1}

## Stage latency breakdown (ms)
- baseline: {'executor': 68682, 'finalize': 128227, 'repair': 59544}
- guarded_pipeline: {'planner_doc': 20048, 'planner_prompt': 20090, 'executor': 66825, 'verifier': 10043, 'finalize': 169568, 'executor_fix': 52514, 'verifier_fix': 0}

## Incremental ROI
- conservative: 19.98750390502968
- base_case: 29.98750390502968
- aggressive: 39.98750390502968

## Strict gate decision
- decision: continue_constrained
- checks: {'passRateDelta': True, 'reliabilityDelta': False, 'latencyOverhead': True, 'incrementalRoiBaseCase': True}