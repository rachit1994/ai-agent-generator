# A/B Decision Scorecard

## Thresholds (Strict CTO Gate)
- `pass_rate_delta_points >= 15.0`
- `reliability_delta_points >= 15.0`
- `median_latency_delta_percent <= 25.0`
- `incremental_roi_base_case > 0`

## Synthetic suite reproducibility (`benchmark-tasks`)
- run_id: `2026-04-17T09-13-13-321916+00-00-58e32b49`
  - pass_rate_delta_points: `0.0` -> fail
  - reliability_delta_points: `-5.0` -> fail
  - median_latency_delta_percent: `4.3626` -> pass
  - incremental_roi_base_case: `-9.3626` -> fail
  - strict decision: `stop`
- run_id: `2026-04-17T09-18-26-539178+00-00-449ebc7d`
  - pass_rate_delta_points: `20.0` -> pass
  - reliability_delta_points: `10.0` -> fail
  - median_latency_delta_percent: `0.0125` -> pass
  - incremental_roi_base_case: `29.9875` -> pass
  - strict decision: `continue_constrained`

## Real-Workflow Suite Reproducibility (`real-workflow-tasks`)
- run_id: `2026-04-17T09-23-39-695020+00-00-2808eddb`
  - pass_rate_delta_points: `20.0` -> pass
  - reliability_delta_points: `15.0` -> pass
  - median_latency_delta_percent: `-0.0062` -> pass
  - incremental_roi_base_case: `35.0` -> pass
  - strict decision: `continue_and_scale`
- run_id: `2026-04-17T09-29-04-855234+00-00-21a17b33`
  - pass_rate_delta_points: `-10.0` -> fail
  - reliability_delta_points: `-15.0` -> fail
  - median_latency_delta_percent: `0.0500` -> pass
  - incremental_roi_base_case: `-25.05` -> fail
  - strict decision: `stop`

## Decision Summary
- Technical gate: **not reproducibly passed**
- Practical transfer gate: **not reproducibly passed**
- Economics gate: **unstable across repeated runs** (see `docs/sde/decision/incremental-economics.md`)
- Final recommendation: **continue_constrained only for stabilization work; do not scale investment until reproducibility is proven**
