# Persona Agent Platform Risk Register (Single Production Exit)

## Risk Scoring Model
- **Severity:** Low, Medium, High, Critical
- **Probability:** Low, Medium, High
- **Response SLA:** maximum time to mitigation action after trigger detection
- **Release gate alignment:** trigger thresholds must match `docs/implementation/2026-04-13-persona-agent-platform-release-gate-spec.md`.

## Active Risks
| ID | Risk | Severity | Probability | Trigger | Mitigation | Contingency | Owner | Response SLA |
|---|---|---|---|---|---|---|---|---|
| R1 | Planner generates unsafe or invalid trajectories | Critical | Medium | policy/temporal gate violations trend above baseline for 2 runs | tighten planner constraints, expand failure-memory retrieval, add reject patterns | fail-closed for affected workflows until mitigated; block promotion | Safety Owner | 4h |
| R2 | Cross-backend output drift between `Ollama` and `vLLM` | High | Medium | gate parity <99% or critical safety divergence in release corpus | lock model-version pairs, calibrate routing policies, add backend-specific eval checks | route all critical flows to parity-approved backend | Inference DRI | 24h |
| R3 | Memory contamination across tenants | Critical | Low | tenant boundary check fails in integration test or logs | enforce tenant-scoped keys and query filters, add access assertions | halt writes and isolate impacted tenant data | Data/Memory DRI | 1h |
| R4 | Observability blind spots block incident diagnosis | High | Medium | missing trace coverage for key run stages | telemetry checklist gate in CI, dashboard completeness review | block release until minimum observability set restored | Observability DRI | 8h |
| R5 | Gate fatigue leads to weak release discipline | High | Medium | repeated waiver requests on same subsystem | require waiver expiry, senior owner sign-off, root-cause corrective action | freeze subsystem release until action closure | Engineering Manager | 24h |
| R6 | Performance regressions under production-like load | High | Medium | availability <99% for two consecutive 15-minute windows, or sustained p95 latency breach through defined windows | enable progressive rollout guardrails and adaptive routing thresholds | auto-rollback and incident protocol | SRE/Operations Owner | 1h |
| R7 | Third-party tool misuse or privilege escalation | Critical | Low | unauthorized tool call detected | strict allowlist, least-privilege scopes, audit checks | revoke token scope and block affected workflow | Safety Owner | 1h |
| R8 | Eval pipeline nondeterminism or flaky **promptfoo** / CI masking real failures | High | Medium | same workflow fails after **three** deterministic retries in one run, or flakes without root-cause ticket | pin suite revisions, isolate seeds, fix harness timeouts, split flaky tests | block promotion for affected workflows until harness fix merges; **no** waiver for silent retry loops | Quality Owner + Observability DRI | 24h |

## Risk Review Cadence
- Weekly risk board update in Friday gate review.
- Immediate incident-triggered review for any critical risk activation.
- Monthly trend review on open/closed risk ratio and mitigation effectiveness.

## Closure Criteria
- Trigger condition absent across two consecutive review cycles.
- Preventive checks added where applicable.
- Owner confirms residual risk falls within accepted threshold.
- For critical risks tied to release gates, closure requires one incident-free soak window per release-gate spec.
