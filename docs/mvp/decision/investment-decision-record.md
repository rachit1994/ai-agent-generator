# Investment Decision Record

## Decision
- outcome: `continue_constrained`
- date: `2026-04-17`
- decision_type: `CTO_A/B_investment_gate`

## Evidence Used
- Protocol and controls: `docs/mvp/decision/ab-protocol-and-controls.md`
- Scorecard: `docs/mvp/decision/ab-decision-scorecard.md`
- Economics: `docs/mvp/decision/incremental-economics.md`
- Synthetic run A summary: `src/services/orchestrator/runtime/outputs/runs/2026-04-17T09-13-13-321916+00-00-58e32b49/summary.json`
- Synthetic run B summary: `src/services/orchestrator/runtime/outputs/runs/2026-04-17T09-18-26-539178+00-00-449ebc7d/summary.json`
- Real-workflow run A summary: `src/services/orchestrator/runtime/outputs/runs/2026-04-17T09-23-39-695020+00-00-2808eddb/summary.json`
- Real-workflow run B summary: `src/services/orchestrator/runtime/outputs/runs/2026-04-17T09-29-04-855234+00-00-21a17b33/summary.json`

## Rationale
- Some runs pass strict technical/economic gates, but repeated runs are not consistent.
- Reproducibility requirement is not satisfied across both suites.
- Technical signal improved versus prior baseline, but confidence is not high enough for scale.

## Re-entry Conditions
Re-open investment only after all are true in fresh A/B runs:
1. `pass_rate_delta_points >= +15.0`
2. `reliability_delta_points >= +15.0`
3. `median_latency_delta_percent <= +25.0`
4. Base-case incremental ROI > 0
5. Two consecutive reproducible passes on both synthetic and real-workflow suites
