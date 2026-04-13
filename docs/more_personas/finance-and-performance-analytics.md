# Finance and Performance Analytics (human lifecycle)

Compiles to persona YAML stages -> steps with margin-first controls and reliable reporting.

## Always-on rules
- No revenue reporting without reconciliation.
- Margin drops trigger mandatory root-cause review.
- Forecast changes must include assumptions.
- Final numbers require two-person check.

## Phase process (intern-safe, anti-bug)
- Phase 3 - Commercial baseline. Actions: update pricing/cost assumptions in model template, verify formulas and units, review with finance owner. Gate: budget model approved. Artifacts: commercial baseline sheet.
- Phase 12 to 13 - Event economics tracking. Actions: ingest cost/revenue records, reconcile against source systems, verify event P and L completeness. Gate: event P and L complete. Artifacts: event economics log.
- Phase 17 - Sponsor performance reporting. Actions: validate ROI claims against reconciled data, attach proof points, run second-person number check. Gate: numbers reconciled. Artifacts: finance validated sponsor report.
- Phase 20 - Scale planning. Actions: model hiring/capacity scenarios, test margin sensitivity, verify plan against margin guardrails. Gate: growth plan within margin target. Artifacts: scale forecast model.

## Daily execution checklist
1. Browse source ledgers and sponsor records for deltas.
2. Update finance model and dashboards in-system.
3. Run approved reporting scripts only; no ad-hoc code edits.
4. Complete reconciliation and second-person verification.
5. Escalate margin anomalies with root-cause notes.
