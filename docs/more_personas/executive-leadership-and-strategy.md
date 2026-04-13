# Executive Leadership and Strategy (human lifecycle)

Compiles to persona YAML stages -> steps with strict gates, dual checks, and artifact proof.

## Always-on rules
- No ambiguous scope starts; clarify objective, owner, deadline.
- Every decision must reference KPI impact and risk impact.
- No verbal approvals; approvals must be logged in writing.
- If a phase gate fails, stop and escalate before next step.

## Phase process (intern-safe, anti-bug)
- Phase -1 to 0 - Direction lock. Actions: browse approved market/customer inputs, draft strategy memo from template, verify objective-owner-deadline fields. Gate: strategy memo approved. Artifacts: weekly strategy brief.
- Phase 1 to 3 - Revenue intent lock. Actions: map audience/sponsor/margin assumptions, update KPI tree, verify assumptions with finance owner. Gate: KPI tree signed. Artifacts: KPI scorecard.
- Phase 4 to 6 - Operating plan lock. Actions: define qualification rules, freeze event calendar, assign named owners/backups, verify ownership matrix completeness. Gate: ownership matrix complete. Artifacts: operating plan.
- Phase 7 to 10 - Governance readiness. Actions: run legal/security/production checklists, log exceptions, verify go/no-go status. Gate: risk checklist green. Artifacts: go/no-go checklist.
- Phase 11 to 14 - Delivery control. Actions: monitor live KPI dashboard, assign incidents by SLA matrix, verify owner + ETA on each incident. Gate: all incidents assigned within SLA. Artifacts: daily control log.
- Phase 15 to 19 - Learning loop. Actions: review results and feedback, update topic/process backlog, verify next-cycle publication. Gate: next-cycle plan published. Artifacts: weekly review doc.
- Phase 20 to 21 - Scale and audit. Actions: evaluate hiring/process upgrades, update risk remediation plan, verify audit package completeness. Gate: audit readiness pass. Artifacts: quarterly audit pack.

## Daily execution checklist
1. Browse KPI/risk dashboards and flag red items.
2. Update decision log and owner matrix in-system.
3. Run approved automations only (report exports, alerts); no ad-hoc code edits.
4. Validate gates with a second reviewer before approvals.
5. Publish end-of-day status and escalate unresolved blockers.
