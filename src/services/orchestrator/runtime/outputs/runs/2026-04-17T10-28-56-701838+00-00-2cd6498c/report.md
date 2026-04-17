# MVP Decision Report
- run_id: 2026-04-17T10-28-56-701838+00-00-2cd6498c
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
- median_latency_delta_percent: -49.97813183380194

## Baseline Metrics
- passRate: 0.2
- reliability: 0.2
- p50Latency: 16005
- p95Latency: 16009
- avgCost: 0.0
- validityRate: 1.0
- retryFrequency: 0.8

## Guarded Metrics
- passRate: 1.0
- reliability: 1.0
- p50Latency: 8006
- p95Latency: 18021
- avgCost: 0.0
- validityRate: 1.0
- retryFrequency: 0.0

## Per-task deltas
- t-001: pass_delta=0, latency_delta_ms=3248, baseline_pass=True, guarded_pass=True
- t-002: pass_delta=1, latency_delta_ms=-8014, baseline_pass=False, guarded_pass=True
- t-003: pass_delta=1, latency_delta_ms=2013, baseline_pass=False, guarded_pass=True
- t-004: pass_delta=1, latency_delta_ms=2000, baseline_pass=False, guarded_pass=True
- t-005: pass_delta=1, latency_delta_ms=-8004, baseline_pass=False, guarded_pass=True
- t-006: pass_delta=0, latency_delta_ms=1, baseline_pass=True, guarded_pass=True
- t-007: pass_delta=1, latency_delta_ms=2005, baseline_pass=False, guarded_pass=True
- t-008: pass_delta=1, latency_delta_ms=-8006, baseline_pass=False, guarded_pass=True
- t-009: pass_delta=1, latency_delta_ms=-8002, baseline_pass=False, guarded_pass=True
- t-010: pass_delta=1, latency_delta_ms=2020, baseline_pass=False, guarded_pass=True

## Root-cause distribution
- baseline: {'none': 1, 'contract_parse_error': 8, 'refusal_expected': 1}
- guarded_pipeline: {'none': 9, 'refusal_expected': 1}

## Stage latency breakdown (ms)
- baseline: {'executor': 68807, 'finalize': 132835, 'repair': 64026}
- guarded_pipeline: {'planner_doc': 20015, 'planner_prompt': 20027, 'executor': 72045, 'verifier': 0, 'finalize': 112096}

## Incremental ROI
- conservative: 150.0
- base_case: 160.0
- aggressive: 170.0

## Strict gate decision
- decision: continue_and_scale
- checks: {'passRateDelta': True, 'reliabilityDelta': True, 'latencyOverhead': True, 'incrementalRoiBaseCase': True}