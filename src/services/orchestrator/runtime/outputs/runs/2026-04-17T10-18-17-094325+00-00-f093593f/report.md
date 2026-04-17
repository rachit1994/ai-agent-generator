# MVP Decision Report
- run_id: 2026-04-17T10-18-17-094325+00-00-f093593f
- provider: ollama
- mode: both
- implementation_model: qwen2.5:7b-instruct
- support_model: gemma4:latest
- suite: ../../../../data/real-workflow-tasks.jsonl
- suite_version: real-workflow-tasks
- budgets: tokens=4096, retries=1, planner_timeout_ms=5000, verifier_timeout_ms=5000, executor_timeout_ms=8000
- verdict: rejected
- recommendation: stop
- pass_rate_delta_points: -9.999999999999998
- reliability_delta_points: -9.999999999999998
- median_latency_delta_percent: 0.024993751562109475

## Baseline Metrics
- passRate: 0.3
- reliability: 0.3
- p50Latency: 16004
- p95Latency: 16007
- avgCost: 0.0
- validityRate: 1.0
- retryFrequency: 0.8

## Guarded Metrics
- passRate: 0.2
- reliability: 0.2
- p50Latency: 16008
- p95Latency: 26024
- avgCost: 0.0
- validityRate: 1.0
- retryFrequency: 0.9

## Per-task deltas
- rw-001: pass_delta=0, latency_delta_ms=16834, baseline_pass=True, guarded_pass=True
- rw-002: pass_delta=0, latency_delta_ms=10011, baseline_pass=False, guarded_pass=False
- rw-003: pass_delta=0, latency_delta_ms=10005, baseline_pass=False, guarded_pass=False
- rw-004: pass_delta=-1, latency_delta_ms=11002, baseline_pass=True, guarded_pass=False
- rw-005: pass_delta=0, latency_delta_ms=2, baseline_pass=False, guarded_pass=False
- rw-006: pass_delta=0, latency_delta_ms=0, baseline_pass=True, guarded_pass=True
- rw-007: pass_delta=0, latency_delta_ms=1, baseline_pass=False, guarded_pass=False
- rw-008: pass_delta=0, latency_delta_ms=2, baseline_pass=False, guarded_pass=False
- rw-009: pass_delta=0, latency_delta_ms=0, baseline_pass=False, guarded_pass=False
- rw-010: pass_delta=0, latency_delta_ms=10020, baseline_pass=False, guarded_pass=False

## Root-cause distribution
- baseline: {'none': 2, 'contract_parse_error': 7, 'refusal_expected': 1}
- guarded_pipeline: {'none': 1, 'quality_check_fail': 8, 'refusal_expected': 1}

## Stage latency breakdown (ms)
- baseline: {'executor': 71446, 'finalize': 134487, 'repair': 63038}
- guarded_pipeline: {'planner_doc': 25044, 'planner_prompt': 25041, 'executor': 72024, 'verifier': 0, 'executor_fix': 70231, 'verifier_fix': 0, 'finalize': 192364}

## Incremental ROI
- conservative: -30.024993751562107
- base_case: -20.024993751562107
- aggressive: -10.024993751562107

## Strict gate decision
- decision: stop
- checks: {'passRateDelta': False, 'reliabilityDelta': False, 'latencyOverhead': True, 'incrementalRoiBaseCase': False}