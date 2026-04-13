# Data, AI, and CRM Intelligence (human lifecycle)

Compiles to persona YAML stages -> steps with strict data quality gates and reproducible insights.

## Always-on rules
- CRM is source of truth; external sheets are read-only scratchpads.
- No model/scoring output without input schema and null checks.
- Scheduled dedupe/hygiene jobs are mandatory and logged.
- Any anomaly needs ticket, owner, and written root-cause path.

## Phase process (intern-safe, anti-bug)
- Phase 0 - Signal intake. Actions: browse approved market/sponsor sources, capture raw signals with source URL, verify relevance tags. Gate: signals validated. Artifacts: topic intake log.
- Phase 1 - Identity resolution. Actions: run dedupe playbook, normalize key fields, review high-risk merges manually, verify duplicate threshold. Gate: duplicate rate under threshold. Artifacts: dedupe report.
- Phase 2 - Lifecycle analytics. Actions: refresh dashboard pipeline, compare with prior day baseline, verify metric parity checks. Gate: dashboard integrity pass. Artifacts: lifecycle dashboard.
- Phase 13 - Lead scoring. Actions: run approved scoring job/script, inspect top and bottom deciles, verify handoff criteria. Gate: scoring QA pass. Artifacts: scored lead export.
- Phase 15 - Graph update. Actions: execute graph refresh workflow, sample confidence edges, verify accuracy threshold. Gate: edge accuracy threshold met. Artifacts: graph update log.
- Phase 19 - Feedback intelligence. Actions: ingest feedback notes, map to taxonomy, update topic priorities, verify cycle-time target. Gate: cycle-time target met. Artifacts: feedback insights report.

## Daily execution checklist
1. Browse sources, store links, and tag confidence.
2. Update CRM and analytics systems in the same work block.
3. Run only approved automation/scripts; no unreviewed code changes.
4. Perform QA checks, document pass/fail, request verifier sign-off.
5. Escalate anomalies immediately with evidence snapshot.
