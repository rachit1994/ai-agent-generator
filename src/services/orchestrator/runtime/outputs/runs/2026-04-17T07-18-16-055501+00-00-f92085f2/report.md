# MVP Decision Report
- run_id: 2026-04-17T07-18-16-055501+00-00-f92085f2
- provider: ollama
- mode: both
- implementation_model: qwen2.5:7b-instruct
- support_model: gemma4:latest
- suite: ../../../../data/mvp-tasks.jsonl
- suite_version: mvp-tasks-v1
- budgets: tokens=4096, retries=1, planner_timeout_ms=5000, verifier_timeout_ms=5000, executor_timeout_ms=8000
- verdict: rejected
- recommendation: stop
- pass_rate_delta_points: 0.0
- median_latency_delta_percent: 62.54831068445331

## Baseline Metrics
- passRate: 0.0
- reliability: 0.0
- p50Latency: 16042
- p95Latency: 16125
- avgCost: 0.0
- validityRate: 1.0
- retryFrequency: 0.9

## Guarded Metrics
- passRate: 0.0
- reliability: 0.0
- p50Latency: 26076
- p95Latency: 26219
- avgCost: 0.0
- validityRate: 1.0
- retryFrequency: 0.9

## Per-task deltas
- t-001: pass_delta=0, latency_delta_ms=10184, baseline_pass=False, guarded_pass=False
- t-002: pass_delta=0, latency_delta_ms=10000, baseline_pass=False, guarded_pass=False
- t-003: pass_delta=0, latency_delta_ms=10002, baseline_pass=False, guarded_pass=False
- t-004: pass_delta=0, latency_delta_ms=10080, baseline_pass=False, guarded_pass=False
- t-005: pass_delta=0, latency_delta_ms=10002, baseline_pass=False, guarded_pass=False
- t-006: pass_delta=0, latency_delta_ms=0, baseline_pass=False, guarded_pass=False
- t-007: pass_delta=0, latency_delta_ms=9984, baseline_pass=False, guarded_pass=False
- t-008: pass_delta=0, latency_delta_ms=9977, baseline_pass=False, guarded_pass=False
- t-009: pass_delta=0, latency_delta_ms=10027, baseline_pass=False, guarded_pass=False
- t-010: pass_delta=0, latency_delta_ms=10039, baseline_pass=False, guarded_pass=False