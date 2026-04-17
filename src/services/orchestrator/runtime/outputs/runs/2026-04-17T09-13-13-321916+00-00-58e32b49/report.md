# MVP Decision Report
- run_id: 2026-04-17T09-13-13-321916+00-00-58e32b49
- provider: ollama
- mode: both
- implementation_model: qwen2.5:7b-instruct
- support_model: gemma4:latest
- suite: ../../../../data/mvp-tasks.jsonl
- suite_version: mvp-tasks
- budgets: tokens=4096, retries=1, planner_timeout_ms=5000, verifier_timeout_ms=5000, executor_timeout_ms=8000
- verdict: rejected
- recommendation: stop
- pass_rate_delta_points: 0.0
- reliability_delta_points: -4.999999999999999
- median_latency_delta_percent: 4.36256928594718

## Baseline Metrics
- passRate: 0.3
- reliability: 0.35
- p50Latency: 15335
- p95Latency: 16006
- avgCost: 0.0
- validityRate: 1.0
- retryFrequency: 0.8

## Guarded Metrics
- passRate: 0.3
- reliability: 0.3
- p50Latency: 16004
- p95Latency: 26046
- avgCost: 0.0
- validityRate: 1.0
- retryFrequency: 0.6

## Per-task deltas
- t-001: pass_delta=0, latency_delta_ms=-4041, baseline_pass=True, guarded_pass=True
- t-002: pass_delta=1, latency_delta_ms=-2766, baseline_pass=False, guarded_pass=True
- t-003: pass_delta=0, latency_delta_ms=10038, baseline_pass=False, guarded_pass=False
- t-004: pass_delta=0, latency_delta_ms=10031, baseline_pass=False, guarded_pass=False
- t-005: pass_delta=0, latency_delta_ms=3, baseline_pass=False, guarded_pass=False
- t-006: pass_delta=0, latency_delta_ms=0, baseline_pass=False, guarded_pass=False
- t-007: pass_delta=-1, latency_delta_ms=18935, baseline_pass=True, guarded_pass=False
- t-008: pass_delta=0, latency_delta_ms=-3, baseline_pass=False, guarded_pass=False
- t-009: pass_delta=0, latency_delta_ms=-2535, baseline_pass=True, guarded_pass=True
- t-010: pass_delta=0, latency_delta_ms=10040, baseline_pass=False, guarded_pass=False

## Root-cause distribution
- baseline: {'none': 3, 'contract_parse_error': 6, 'refusal_expected': 1}
- guarded_pipeline: {'none': 3, 'quality_check_fail': 6, 'refusal_expected': 1}

## Stage latency breakdown (ms)
- baseline: {'executor': 71158, 'repair': 60213, 'finalize': 131372}
- guarded_pipeline: {'planner_doc': 20043, 'planner_prompt': 20059, 'executor': 67881, 'verifier': 15028, 'finalize': 171074, 'executor_fix': 48015, 'verifier_fix': 0}

## Incremental ROI
- conservative: -19.36256928594718
- base_case: -9.36256928594718
- aggressive: 0.6374307140528206

## Strict gate decision
- decision: stop
- checks: {'passRateDelta': False, 'reliabilityDelta': False, 'latencyOverhead': True, 'incrementalRoiBaseCase': False}