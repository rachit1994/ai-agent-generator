# MVP Decision Report
- run_id: 2026-04-17T09-48-45-899965+00-00-c59f5db2
- provider: ollama
- mode: both
- implementation_model: qwen2.5:7b-instruct
- support_model: gemma4:latest
- suite: ../../../../data/real-workflow-tasks.jsonl
- suite_version: real-workflow-tasks
- budgets: tokens=4096, retries=1, planner_timeout_ms=5000, verifier_timeout_ms=5000, executor_timeout_ms=8000
- verdict: rejected
- recommendation: stop
- pass_rate_delta_points: -20.0
- reliability_delta_points: -20.0
- median_latency_delta_percent: 0.012495314257153568

## Baseline Metrics
- passRate: 0.3
- reliability: 0.3
- p50Latency: 16006
- p95Latency: 16008
- avgCost: 0.0
- validityRate: 1.0
- retryFrequency: 0.6

## Guarded Metrics
- passRate: 0.1
- reliability: 0.1
- p50Latency: 16008
- p95Latency: 26053
- avgCost: 0.0
- validityRate: 1.0
- retryFrequency: 0.9

## Per-task deltas
- rw-001: pass_delta=-1, latency_delta_ms=14796, baseline_pass=True, guarded_pass=False
- rw-002: pass_delta=0, latency_delta_ms=10038, baseline_pass=False, guarded_pass=False
- rw-003: pass_delta=0, latency_delta_ms=10043, baseline_pass=False, guarded_pass=False
- rw-004: pass_delta=-1, latency_delta_ms=20295, baseline_pass=True, guarded_pass=False
- rw-005: pass_delta=1, latency_delta_ms=-4747, baseline_pass=False, guarded_pass=True
- rw-006: pass_delta=0, latency_delta_ms=1, baseline_pass=False, guarded_pass=False
- rw-007: pass_delta=0, latency_delta_ms=0, baseline_pass=False, guarded_pass=False
- rw-008: pass_delta=0, latency_delta_ms=-1, baseline_pass=False, guarded_pass=False
- rw-009: pass_delta=0, latency_delta_ms=2, baseline_pass=False, guarded_pass=False
- rw-010: pass_delta=-1, latency_delta_ms=18342, baseline_pass=True, guarded_pass=False

## Root-cause distribution
- baseline: {'none': 3, 'contract_parse_error': 6, 'refusal_expected': 1}
- guarded_pipeline: {'quality_check_fail': 8, 'none': 1, 'refusal_expected': 1}

## Stage latency breakdown (ms)
- baseline: {'executor': 69075, 'finalize': 117096, 'repair': 48020}
- guarded_pipeline: {'planner_doc': 25066, 'planner_prompt': 25093, 'executor': 72046, 'verifier': 0, 'executor_fix': 63613, 'verifier_fix': 0, 'finalize': 185865}

## Incremental ROI
- conservative: -50.01249531425715
- base_case: -40.01249531425715
- aggressive: -30.01249531425715

## Strict gate decision
- decision: stop
- checks: {'passRateDelta': False, 'reliabilityDelta': False, 'latencyOverhead': True, 'incrementalRoiBaseCase': False}