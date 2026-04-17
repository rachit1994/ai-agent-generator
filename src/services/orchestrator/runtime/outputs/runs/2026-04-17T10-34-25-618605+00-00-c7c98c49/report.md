# MVP Decision Report
- run_id: 2026-04-17T10-34-25-618605+00-00-c7c98c49
- provider: ollama
- mode: both
- implementation_model: qwen2.5:7b-instruct
- support_model: gemma4:latest
- suite: ../../../../data/real-workflow-tasks.jsonl
- suite_version: real-workflow-tasks
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
- p95Latency: 16008
- avgCost: 0.0
- validityRate: 1.0
- retryFrequency: 0.9

## Guarded Metrics
- passRate: 1.0
- reliability: 1.0
- p50Latency: 8004
- p95Latency: 18020
- avgCost: 0.0
- validityRate: 1.0
- retryFrequency: 0.0

## Per-task deltas
- rw-001: pass_delta=1, latency_delta_ms=2003, baseline_pass=False, guarded_pass=True
- rw-002: pass_delta=1, latency_delta_ms=-382, baseline_pass=False, guarded_pass=True
- rw-003: pass_delta=1, latency_delta_ms=2004, baseline_pass=False, guarded_pass=True
- rw-004: pass_delta=1, latency_delta_ms=2002, baseline_pass=False, guarded_pass=True
- rw-005: pass_delta=1, latency_delta_ms=-8001, baseline_pass=False, guarded_pass=True
- rw-006: pass_delta=0, latency_delta_ms=0, baseline_pass=True, guarded_pass=True
- rw-007: pass_delta=1, latency_delta_ms=-8004, baseline_pass=False, guarded_pass=True
- rw-008: pass_delta=1, latency_delta_ms=-8001, baseline_pass=False, guarded_pass=True
- rw-009: pass_delta=1, latency_delta_ms=-8003, baseline_pass=False, guarded_pass=True
- rw-010: pass_delta=1, latency_delta_ms=2033, baseline_pass=False, guarded_pass=True

## Root-cause distribution
- baseline: {'contract_parse_error': 9, 'refusal_expected': 1}
- guarded_pipeline: {'none': 9, 'refusal_expected': 1}

## Stage latency breakdown (ms)
- baseline: {'executor': 72034, 'repair': 72019, 'finalize': 144058}
- guarded_pipeline: {'planner_doc': 25028, 'planner_prompt': 22637, 'executor': 72027, 'verifier': 0, 'finalize': 119709}

## Incremental ROI
- conservative: 170.0
- base_case: 180.0
- aggressive: 190.0

## Strict gate decision
- decision: continue_and_scale
- checks: {'passRateDelta': True, 'reliabilityDelta': True, 'latencyOverhead': True, 'incrementalRoiBaseCase': True}