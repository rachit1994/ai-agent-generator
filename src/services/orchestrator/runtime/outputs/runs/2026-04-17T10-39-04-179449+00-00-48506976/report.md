# MVP Decision Report
- run_id: 2026-04-17T10-39-04-179449+00-00-48506976
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
- median_latency_delta_percent: -49.97813183380194

## Baseline Metrics
- passRate: 0.2
- reliability: 0.2
- p50Latency: 16005
- p95Latency: 16016
- avgCost: 0.0
- validityRate: 1.0
- retryFrequency: 0.8

## Guarded Metrics
- passRate: 1.0
- reliability: 1.0
- p50Latency: 8006
- p95Latency: 18030
- avgCost: 0.0
- validityRate: 1.0
- retryFrequency: 0.0

## Per-task deltas
- rw-001: pass_delta=0, latency_delta_ms=10660, baseline_pass=True, guarded_pass=True
- rw-002: pass_delta=1, latency_delta_ms=2016, baseline_pass=False, guarded_pass=True
- rw-003: pass_delta=1, latency_delta_ms=2002, baseline_pass=False, guarded_pass=True
- rw-004: pass_delta=1, latency_delta_ms=1984, baseline_pass=False, guarded_pass=True
- rw-005: pass_delta=1, latency_delta_ms=-8002, baseline_pass=False, guarded_pass=True
- rw-006: pass_delta=0, latency_delta_ms=1, baseline_pass=True, guarded_pass=True
- rw-007: pass_delta=1, latency_delta_ms=-8010, baseline_pass=False, guarded_pass=True
- rw-008: pass_delta=1, latency_delta_ms=-8002, baseline_pass=False, guarded_pass=True
- rw-009: pass_delta=1, latency_delta_ms=-8002, baseline_pass=False, guarded_pass=True
- rw-010: pass_delta=1, latency_delta_ms=2025, baseline_pass=False, guarded_pass=True

## Root-cause distribution
- baseline: {'none': 1, 'contract_parse_error': 8, 'refusal_expected': 1}
- guarded_pipeline: {'none': 9, 'refusal_expected': 1}

## Stage latency breakdown (ms)
- baseline: {'executor': 71392, 'finalize': 135445, 'repair': 64050}
- guarded_pipeline: {'planner_doc': 25038, 'planner_prompt': 25032, 'executor': 72027, 'verifier': 1, 'finalize': 122117}

## Incremental ROI
- conservative: 150.0
- base_case: 160.0
- aggressive: 170.0

## Strict gate decision
- decision: continue_and_scale
- checks: {'passRateDelta': True, 'reliabilityDelta': True, 'latencyOverhead': True, 'incrementalRoiBaseCase': True}