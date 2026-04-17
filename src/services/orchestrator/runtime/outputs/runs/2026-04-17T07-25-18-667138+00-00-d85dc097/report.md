# MVP Decision Report
- run_id: 2026-04-17T07-25-18-667138+00-00-d85dc097
- provider: ollama
- mode: both
- implementation_model: qwen2.5:7b-instruct
- support_model: gemma4:latest
- suite: ../../../../data/real-workflow-tasks.jsonl
- suite_version: mvp-tasks-v1
- budgets: tokens=4096, retries=1, planner_timeout_ms=5000, verifier_timeout_ms=5000, executor_timeout_ms=8000
- verdict: rejected
- recommendation: stop
- pass_rate_delta_points: 0.0
- median_latency_delta_percent: 62.54126440361259

## Baseline Metrics
- passRate: 0.0
- reliability: 0.0
- p50Latency: 16055
- p95Latency: 16082
- avgCost: 0.0
- validityRate: 1.0
- retryFrequency: 0.9

## Guarded Metrics
- passRate: 0.0
- reliability: 0.0
- p50Latency: 26096
- p95Latency: 26159
- avgCost: 0.0
- validityRate: 1.0
- retryFrequency: 0.9

## Per-task deltas
- rw-001: pass_delta=0, latency_delta_ms=9980, baseline_pass=False, guarded_pass=False
- rw-002: pass_delta=0, latency_delta_ms=9948, baseline_pass=False, guarded_pass=False
- rw-003: pass_delta=0, latency_delta_ms=10006, baseline_pass=False, guarded_pass=False
- rw-004: pass_delta=0, latency_delta_ms=10050, baseline_pass=False, guarded_pass=False
- rw-005: pass_delta=0, latency_delta_ms=10117, baseline_pass=False, guarded_pass=False
- rw-006: pass_delta=0, latency_delta_ms=0, baseline_pass=False, guarded_pass=False
- rw-007: pass_delta=0, latency_delta_ms=10200, baseline_pass=False, guarded_pass=False
- rw-008: pass_delta=0, latency_delta_ms=10004, baseline_pass=False, guarded_pass=False
- rw-009: pass_delta=0, latency_delta_ms=10041, baseline_pass=False, guarded_pass=False
- rw-010: pass_delta=0, latency_delta_ms=10040, baseline_pass=False, guarded_pass=False