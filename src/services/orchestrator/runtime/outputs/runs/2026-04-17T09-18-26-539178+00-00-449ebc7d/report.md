# MVP Decision Report
- run_id: 2026-04-17T09-18-26-539178+00-00-449ebc7d
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
- median_latency_delta_percent: 0.012496875781054738

## Baseline Metrics
- passRate: 0.1
- reliability: 0.2
- p50Latency: 16004
- p95Latency: 16007
- avgCost: 0.0
- validityRate: 1.0
- retryFrequency: 0.8

## Guarded Metrics
- passRate: 0.3
- reliability: 0.3
- p50Latency: 16006
- p95Latency: 26047
- avgCost: 0.0
- validityRate: 1.0
- retryFrequency: 0.8

## Per-task deltas
- t-001: pass_delta=0, latency_delta_ms=2914, baseline_pass=True, guarded_pass=True
- t-002: pass_delta=1, latency_delta_ms=-4460, baseline_pass=False, guarded_pass=True
- t-003: pass_delta=0, latency_delta_ms=10043, baseline_pass=False, guarded_pass=False
- t-004: pass_delta=0, latency_delta_ms=13329, baseline_pass=False, guarded_pass=False
- t-005: pass_delta=0, latency_delta_ms=-1, baseline_pass=False, guarded_pass=False
- t-006: pass_delta=0, latency_delta_ms=0, baseline_pass=False, guarded_pass=False
- t-007: pass_delta=0, latency_delta_ms=10034, baseline_pass=False, guarded_pass=False
- t-008: pass_delta=0, latency_delta_ms=1, baseline_pass=False, guarded_pass=False
- t-009: pass_delta=1, latency_delta_ms=-2322, baseline_pass=False, guarded_pass=True
- t-010: pass_delta=0, latency_delta_ms=10763, baseline_pass=False, guarded_pass=False

## Root-cause distribution
- baseline: {'none': 1, 'contract_parse_error': 8, 'refusal_expected': 1}
- guarded_pipeline: {'none': 3, 'quality_check_fail': 6, 'refusal_expected': 1}

## Stage latency breakdown (ms)
- baseline: {'executor': 70711, 'finalize': 130725, 'repair': 60012}
- guarded_pipeline: {'planner_doc': 20044, 'planner_prompt': 20065, 'executor': 68619, 'verifier': 5011, 'finalize': 171026, 'executor_fix': 57247, 'verifier_fix': 0}

## Incremental ROI
- conservative: 19.987503124218946
- base_case: 29.987503124218946
- aggressive: 39.98750312421895

## Strict gate decision
- decision: continue_constrained
- checks: {'passRateDelta': True, 'reliabilityDelta': False, 'latencyOverhead': True, 'incrementalRoiBaseCase': True}