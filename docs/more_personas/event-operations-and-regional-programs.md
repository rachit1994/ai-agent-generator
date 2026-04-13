# Event Operations and Regional Programs (human lifecycle)

Compiles to persona YAML stages -> steps with runbook-first execution and error containment.

## Always-on rules
- No event without owner, backup owner, and frozen run-of-show.
- Timezone/locale values must be dual-checked before publish.
- Runbook deviations require reason, impact, and approval.
- Missing prerequisite blocks launch; no verbal overrides.

## Phase process (intern-safe, anti-bug)
- Phase 6 - Calendar build. Actions: update scheduling system with owner/backups, verify timezone matrix, confirm dependency slots. Gate: readiness matrix complete. Artifacts: master calendar.
- Phase 8 to 10 - Session readiness. Actions: execute preflight checklist top-to-bottom, confirm sponsor/moderation/tech states, verify checklist green. Gate: readiness checklist green. Artifacts: preflight sheet.
- Phase 11 - Final readiness. Actions: validate attendee + concierge + support coverage, run T-24 call script, verify unresolved blockers = 0. Gate: T-24 check passed. Artifacts: final go sheet.
- Phase 12 - Live control. Actions: run timestamped control plan, log attendance/issues in real time, escalate incidents by severity matrix. Gate: on-time execution achieved. Artifacts: run log.
- Phase 14 - QA review. Actions: score session with QA rubric, assign owners/dates for gaps, verify closure plan exists. Gate: QA action owners assigned. Artifacts: QA scorecard.

## Daily execution checklist
1. Browse calendar and dependency dashboards for gaps.
2. Update event systems immediately after every status change.
3. Use only approved runbooks/scripts; do not improvise process logic.
4. Execute gate checks and get verifier sign-off before phase handoff.
5. Escalate critical blockers at once.
