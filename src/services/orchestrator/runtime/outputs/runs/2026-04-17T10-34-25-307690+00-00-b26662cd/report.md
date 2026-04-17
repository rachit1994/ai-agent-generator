# MVP Decision Report
- run_id: 2026-04-17T10-34-25-307690+00-00-b26662cd
- provider: ollama
- mode: both
- implementation_model: qwen2.5:7b-instruct
- support_model: gemma4:latest
- suite: ../../../../data/mvp-tasks.jsonl
- suite_version: mvp-tasks
- budgets: tokens=4096, retries=1, planner_timeout_ms=5000, verifier_timeout_ms=5000, executor_timeout_ms=8000
- verdict: supported
- recommendation: continue
- pass_rate_delta_points: 80.0
- reliability_delta_points: 80.0
- median_latency_delta_percent: -50.0

## Baseline Metrics
- passRate: 0.2
- reliability: 0.2
- p50Latency: 16004
- p95Latency: 16005
- avgCost: 0.0
- validityRate: 1.0
- retryFrequency: 0.8

## Guarded Metrics
- passRate: 1.0
- reliability: 1.0
- p50Latency: 8002
- p95Latency: 18026
- avgCost: 0.0
- validityRate: 1.0
- retryFrequency: 0.0

## Per-task deltas
- t-001: pass_delta=0, latency_delta_ms=3054, baseline_pass=True, guarded_pass=True
- t-002: pass_delta=1, latency_delta_ms=-8005, baseline_pass=False, guarded_pass=True
- t-003: pass_delta=1, latency_delta_ms=2005, baseline_pass=False, guarded_pass=True
- t-004: pass_delta=1, latency_delta_ms=2023, baseline_pass=False, guarded_pass=True
- t-005: pass_delta=1, latency_delta_ms=-8003, baseline_pass=False, guarded_pass=True
- t-006: pass_delta=0, latency_delta_ms=0, baseline_pass=True, guarded_pass=True
- t-007: pass_delta=1, latency_delta_ms=2022, baseline_pass=False, guarded_pass=True
- t-008: pass_delta=1, latency_delta_ms=-8003, baseline_pass=False, guarded_pass=True
- t-009: pass_delta=1, latency_delta_ms=-8001, baseline_pass=False, guarded_pass=True
- t-010: pass_delta=1, latency_delta_ms=2011, baseline_pass=False, guarded_pass=True

## Root-cause distribution
- baseline: {'none': 1, 'contract_parse_error': 8, 'refusal_expected': 1}
- guarded_pipeline: {'none': 9, 'refusal_expected': 1}

## Stage latency breakdown (ms)
- baseline: {'executor': 68852, 'finalize': 132873, 'repair': 64017}
- guarded_pipeline: {'planner_doc': 20022, 'planner_prompt': 20026, 'executor': 71916, 'verifier': 0, 'finalize': 111976}

## Incremental ROI
- conservative: 150.0
- base_case: 160.0
- aggressive: 170.0

## Strict gate decision
- decision: continue_and_scale
- checks: {'passRateDelta': True, 'reliabilityDelta': True, 'latencyOverhead': True, 'incrementalRoiBaseCase': True}