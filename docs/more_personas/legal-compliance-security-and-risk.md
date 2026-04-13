# Legal, Compliance, Security, and Risk (human lifecycle)

Compiles to persona YAML stages -> steps with non-negotiable controls and audit-ready evidence.

## Always-on rules
- If consent or policy is unclear, stop execution.
- Least-privilege access policy enforced for all tools.
- Incidents must be logged within SLA.
- Audit evidence is created during work, not after.

## Phase process (intern-safe, anti-bug)
- Phase 7 - Compliance baseline. Actions: review current policy sources, define consent/retention/access controls in template, verify checklist with legal owner. Gate: policy checklist approved. Artifacts: compliance baseline doc.
- Phase 10 - Experience compliance. Actions: run accessibility + participant-policy preflight, log deviations, verify remediation before launch. Gate: compliance preflight pass. Artifacts: compliance signoff.
- Phase 12 to 14 - Runtime governance. Actions: monitor incident and exception queues, classify by severity, verify SLA timer and owner assignment. Gate: incident SLA met. Artifacts: incident and exception log.
- Phase 17 - Reporting integrity. Actions: review sponsor-facing claims and data boundaries, check approved wording, verify legal/security sign-off. Gate: legal/security review complete. Artifacts: governance review note.
- Phase 21 - Risk and audit. Actions: update risk register from incident trends, compile evidence package, verify audit-readiness checklist. Gate: audit readiness pass. Artifacts: risk register and audit pack.

## Daily execution checklist
1. Browse policy updates and active exception queue.
2. Update compliance/risk systems and evidence repository in real time.
3. Use approved compliance tooling/scripts only; no unapproved code changes.
4. Execute gate checks and obtain second-person sign-off.
5. Escalate unclear consent/policy cases immediately.
