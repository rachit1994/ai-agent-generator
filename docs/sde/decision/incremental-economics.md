# Incremental Economics

**In plain words:** a **tiny income statement** for “orchestrated runs vs raw model calls” — did we gain more **value** than we spent in **cost**? Uses numbers from real summaries; read **Framing** before the tables.

## Framing
Incremental economics compares the orchestrated path against direct model usage:

`incremental_value = value_guarded - value_baseline`

`incremental_cost = cost_guarded - cost_baseline`

`incremental_roi = (incremental_value - incremental_cost) / max(incremental_cost, 1e-9)`

## Observed Inputs From Current Runs
- Synthetic run A base ROI: `-9.36`
- Synthetic run B base ROI: `+29.99`
- Real-workflow run A base ROI: `+35.00`
- Real-workflow run B base ROI: `-25.05`
- Latency overhead is generally within threshold after fast-path changes, but value deltas are highly unstable.

## Scenario Outcomes
- Conservative case: negative expected ROI due to run-to-run volatility.
- Base case: inconclusive (sign flips between strongly positive and strongly negative outcomes).
- Aggressive case: positive only when favorable reliability deltas appear; currently not repeatable.

## Economics Conclusion
Incremental ROI is no longer uniformly negative, but it is not stable enough for scale decisions. Keep investment in constrained stabilization mode until repeated runs show consistently positive base-case ROI with strict-gate reproducibility.
