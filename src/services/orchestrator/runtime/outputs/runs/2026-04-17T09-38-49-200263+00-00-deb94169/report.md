# MVP Decision Report
- run_id: 2026-04-17T09-38-49-200263+00-00-deb94169
- provider: ollama
- mode: both
- implementation_model: qwen2.5:7b-instruct
- support_model: gemma4:latest
- suite: ../../../../data/mvp-tasks.jsonl
- suite_version: mvp-tasks
- budgets: tokens=4096, retries=1, planner_timeout_ms=5000, verifier_timeout_ms=5000, executor_timeout_ms=8000
- verdict: rejected
- recommendation: stop
- pass_rate_delta_points: -20.0
- reliability_delta_points: -20.0
- median_latency_delta_percent: 90.99152845722467

## Baseline Metrics
- passRate: 0.5
- reliability: 0.5
- p50Latency: 8381
- p95Latency: 16006
- avgCost: 0.0
- validityRate: 1.0
- retryFrequency: 0.6

## Guarded Metrics
- passRate: 0.3
- reliability: 0.3
- p50Latency: 16007
- p95Latency: 26045
- avgCost: 0.0
- validityRate: 1.0
- retryFrequency: 0.7

## Per-task deltas
- t-001: pass_delta=0, latency_delta_ms=1200, baseline_pass=True, guarded_pass=True
- t-002: pass_delta=1, latency_delta_ms=-4429, baseline_pass=False, guarded_pass=True
- t-003: pass_delta=0, latency_delta_ms=10035, baseline_pass=False, guarded_pass=False
- t-004: pass_delta=-1, latency_delta_ms=18240, baseline_pass=True, guarded_pass=False
- t-005: pass_delta=0, latency_delta_ms=-1, baseline_pass=False, guarded_pass=False
- t-006: pass_delta=0, latency_delta_ms=0, baseline_pass=False, guarded_pass=False
- t-007: pass_delta=-1, latency_delta_ms=19373, baseline_pass=True, guarded_pass=False
- t-008: pass_delta=0, latency_delta_ms=1, baseline_pass=False, guarded_pass=False
- t-009: pass_delta=0, latency_delta_ms=5179, baseline_pass=True, guarded_pass=True
- t-010: pass_delta=-1, latency_delta_ms=10969, baseline_pass=True, guarded_pass=False

## Root-cause distribution
- baseline: {'none': 5, 'contract_parse_error': 4, 'refusal_expected': 1}
- guarded_pipeline: {'none': 3, 'quality_check_fail': 6, 'refusal_expected': 1}

## Stage latency breakdown (ms)
- baseline: {'executor': 66296, 'repair': 42424, 'finalize': 108721}
- guarded_pipeline: {'planner_doc': 20052, 'planner_prompt': 20057, 'executor': 67524, 'verifier': 10020, 'finalize': 169288, 'executor_fix': 51581, 'verifier_fix': 0}

## Incremental ROI
- conservative: -140.99152845722466
- base_case: -130.99152845722466
- aggressive: -120.99152845722466

## Strict gate decision
- decision: stop
- checks: {'passRateDelta': False, 'reliabilityDelta': False, 'latencyOverhead': False, 'incrementalRoiBaseCase': False}