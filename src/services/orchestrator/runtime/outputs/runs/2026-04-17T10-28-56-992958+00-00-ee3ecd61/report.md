# MVP Decision Report
- run_id: 2026-04-17T10-28-56-992958+00-00-ee3ecd61
- provider: ollama
- mode: both
- implementation_model: qwen2.5:7b-instruct
- support_model: gemma4:latest
- suite: ../../../../data/mvp-tasks.jsonl
- suite_version: mvp-tasks
- budgets: tokens=4096, retries=1, planner_timeout_ms=5000, verifier_timeout_ms=5000, executor_timeout_ms=8000
- verdict: supported
- recommendation: continue
- pass_rate_delta_points: 90.0
- reliability_delta_points: 90.0
- median_latency_delta_percent: -49.990627928772255

## Baseline Metrics
- passRate: 0.1
- reliability: 0.1
- p50Latency: 16005
- p95Latency: 16012
- avgCost: 0.0
- validityRate: 1.0
- retryFrequency: 0.9

## Guarded Metrics
- passRate: 1.0
- reliability: 1.0
- p50Latency: 8004
- p95Latency: 18030
- avgCost: 0.0
- validityRate: 1.0
- retryFrequency: 0.0

## Per-task deltas
- t-001: pass_delta=1, latency_delta_ms=-8036, baseline_pass=False, guarded_pass=True
- t-002: pass_delta=1, latency_delta_ms=-8008, baseline_pass=False, guarded_pass=True
- t-003: pass_delta=1, latency_delta_ms=2022, baseline_pass=False, guarded_pass=True
- t-004: pass_delta=1, latency_delta_ms=2006, baseline_pass=False, guarded_pass=True
- t-005: pass_delta=1, latency_delta_ms=-8002, baseline_pass=False, guarded_pass=True
- t-006: pass_delta=0, latency_delta_ms=0, baseline_pass=True, guarded_pass=True
- t-007: pass_delta=1, latency_delta_ms=2000, baseline_pass=False, guarded_pass=True
- t-008: pass_delta=1, latency_delta_ms=-8002, baseline_pass=False, guarded_pass=True
- t-009: pass_delta=1, latency_delta_ms=-8002, baseline_pass=False, guarded_pass=True
- t-010: pass_delta=1, latency_delta_ms=2025, baseline_pass=False, guarded_pass=True

## Root-cause distribution
- baseline: {'contract_parse_error': 9, 'refusal_expected': 1}
- guarded_pipeline: {'none': 9, 'refusal_expected': 1}

## Stage latency breakdown (ms)
- baseline: {'executor': 72054, 'repair': 72045, 'finalize': 144101}
- guarded_pipeline: {'planner_doc': 20010, 'planner_prompt': 20036, 'executor': 72039, 'verifier': 0, 'finalize': 112104}

## Incremental ROI
- conservative: 170.0
- base_case: 180.0
- aggressive: 190.0

## Strict gate decision
- decision: continue_and_scale
- checks: {'passRateDelta': True, 'reliabilityDelta': True, 'latencyOverhead': True, 'incrementalRoiBaseCase': True}