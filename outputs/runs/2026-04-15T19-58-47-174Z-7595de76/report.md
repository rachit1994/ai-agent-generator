# MVP Decision Report
- run_id: 2026-04-15T19-58-47-174Z-7595de76
- provider: ollama
- mode: both
- implementation_model: qwen2.5:7b-instruct
- support_model: gemma 4
- suite: ./data/mvp-tasks.jsonl
- suite_version: mvp-tasks-v1
- budgets: tokens=4096, retries=1, timeout_ms=90000
- verdict: supported
- recommendation: continue
- pass_rate_delta_points: 100
- median_latency_delta_percent: -100

## Baseline Metrics
- passRate: 0
- reliability: 0
- p50Latency: 13193
- p95Latency: 20036
- avgCost: 0
- validityRate: 1
- retryFrequency: 0

## Guarded Metrics
- passRate: 1
- reliability: 1
- p50Latency: 0
- p95Latency: 0
- avgCost: 0
- validityRate: 1
- retryFrequency: 1

## Per-task deltas
- t-001: pass_delta=1, latency_delta_ms=-3632, baseline_pass=false, guarded_pass=true
- t-002: pass_delta=1, latency_delta_ms=-15891, baseline_pass=false, guarded_pass=true
- t-003: pass_delta=1, latency_delta_ms=-15741, baseline_pass=false, guarded_pass=true
- t-004: pass_delta=1, latency_delta_ms=-11959, baseline_pass=false, guarded_pass=true
- t-005: pass_delta=1, latency_delta_ms=-13193, baseline_pass=false, guarded_pass=true
- t-006: pass_delta=1, latency_delta_ms=0, baseline_pass=false, guarded_pass=true
- t-007: pass_delta=1, latency_delta_ms=-20036, baseline_pass=false, guarded_pass=true
- t-008: pass_delta=1, latency_delta_ms=-29191, baseline_pass=false, guarded_pass=true
- t-009: pass_delta=1, latency_delta_ms=-5811, baseline_pass=false, guarded_pass=true
- t-010: pass_delta=1, latency_delta_ms=-13624, baseline_pass=false, guarded_pass=true