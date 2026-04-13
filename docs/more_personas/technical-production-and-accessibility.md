# Technical Production and Accessibility (human lifecycle)

Compiles to persona YAML stages -> steps with failure-prevention and accessibility guarantees.

## Always-on rules
- No live session without dry run on production-like setup.
- Accessibility checks are mandatory, never optional.
- Incident response follows written playbook only.
- Root cause note required for every incident.

## Phase process (intern-safe, anti-bug)
- Phase 10 - Tech setup. Actions: run platform/recording/caption/fallback checklist, execute dry run script, verify checklist evidence. Gate: dry run pass. Artifacts: tech checklist.
- Phase 11 - Final system check. Actions: confirm host permissions and support channels, run T-60 signoff routine, verify all statuses green. Gate: T-60 technical signoff. Artifacts: technical signoff log.
- Phase 12 - Live execution. Actions: monitor health dashboard, triage issues by incident tree, apply playbook actions only, verify failure-rate threshold. Gate: failure rate remains below threshold. Artifacts: incident log.
- Phase 14 - Technical QA. Actions: review incident patterns and caption quality, create remediation tasks with owners/ETAs, verify closure plan. Gate: remediation tasks assigned. Artifacts: technical QA report.

## Daily execution checklist
1. Browse monitoring boards and upcoming session queue.
2. Update technical run logs and support systems in real time.
3. Run only approved scripts/automation; no unreviewed code edits during live ops.
4. Complete gate checks and second-person sign-off before go-live.
5. Escalate critical incidents immediately and capture prevention notes.
