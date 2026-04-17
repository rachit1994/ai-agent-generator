# MVP Decision Report
- run_id: 2026-04-17T10-24-30-766863+00-00-4d14b4d2
- provider: ollama
- mode: both
- implementation_model: qwen2.5:7b-instruct
- support_model: gemma4:latest
- suite: ../../../../data/real-workflow-tasks.jsonl
- suite_version: real-workflow-tasks
- budgets: tokens=4096, retries=1, planner_timeout_ms=5000, verifier_timeout_ms=5000, executor_timeout_ms=8000
- verdict: supported
- recommendation: continue
- pass_rate_delta_points: 80.0
- reliability_delta_points: 80.0
- median_latency_delta_percent: -49.99375156210947

## Baseline Metrics
- passRate: 0.2
- reliability: 0.2
- p50Latency: 16004
- p95Latency: 16006
- avgCost: 0.0
- validityRate: 1.0
- retryFrequency: 0.8

## Guarded Metrics
- passRate: 1.0
- reliability: 1.0
- p50Latency: 8003
- p95Latency: 18033
- avgCost: 0.0
- validityRate: 1.0
- retryFrequency: 0.0

## Per-task deltas
- rw-001: pass_delta=0, latency_delta_ms=10435, baseline_pass=True, guarded_pass=True
- rw-002: pass_delta=1, latency_delta_ms=2028, baseline_pass=False, guarded_pass=True
- rw-003: pass_delta=1, latency_delta_ms=2021, baseline_pass=False, guarded_pass=True
- rw-004: pass_delta=1, latency_delta_ms=2048, baseline_pass=False, guarded_pass=True
- rw-005: pass_delta=1, latency_delta_ms=-9698, baseline_pass=False, guarded_pass=True
- rw-006: pass_delta=0, latency_delta_ms=0, baseline_pass=True, guarded_pass=True
- rw-007: pass_delta=1, latency_delta_ms=-8002, baseline_pass=False, guarded_pass=True
- rw-008: pass_delta=1, latency_delta_ms=-8002, baseline_pass=False, guarded_pass=True
- rw-009: pass_delta=1, latency_delta_ms=-8002, baseline_pass=False, guarded_pass=True
- rw-010: pass_delta=1, latency_delta_ms=-861, baseline_pass=False, guarded_pass=True

## Root-cause distribution
- baseline: {'none': 1, 'contract_parse_error': 8, 'refusal_expected': 1}
- guarded_pipeline: {'none': 9, 'refusal_expected': 1}

## Stage latency breakdown (ms)
- baseline: {'executor': 71599, 'finalize': 135620, 'repair': 64015}
- guarded_pipeline: {'planner_doc': 25013, 'planner_prompt': 22198, 'executor': 70342, 'verifier': 0, 'finalize': 117587}

## Incremental ROI
- conservative: 150.0
- base_case: 160.0
- aggressive: 170.0

## Strict gate decision
- decision: continue_and_scale
- checks: {'passRateDelta': True, 'reliabilityDelta': True, 'latencyOverhead': True, 'incrementalRoiBaseCase': True}