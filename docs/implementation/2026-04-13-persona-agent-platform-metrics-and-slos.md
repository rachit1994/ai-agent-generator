# Persona Agent Platform Metrics and SLOs (Q1 Production)

## Measurement Principles
- Metrics must drive release and rollback decisions, not passive reporting.
- Every SLO has a clear owner, source dashboard, and response policy.
- Threshold breaches trigger explicit action within the defined response window.

## North Star Outcomes
- Reliable autonomous execution with safety-first behavior.
- Fast and diagnosable recovery when rejects or incidents occur.
- Continuous improvement without safety regressions.

## Service Level Objectives
| Domain | SLI | Target (SLO) | Window | Owner | Breach Action |
|---|---|---|---|---|---|
| Workflow Reliability | Step gate pass rate | >= 97% for critical workflows | rolling 7d | Quality Owner | block promotion, open corrective action |
| Consistency | Repeated-run reliability (`pass^k`) | >= 95% at k=5 for critical workflows | rolling 7d | Quality Owner | block promotion and run stability triage |
| Robustness | Semantic perturbation survival rate | >= 92% on approved perturbation set | rolling 7d | Tech Lead | open robustness bug queue and gate release |
| Fault Tolerance | Tool/API fault survival rate | >= 90% under controlled injected faults | rolling 7d | SRE/Operations Owner | freeze rollout and run fault hardening |
| Safety | Unsafe action pre-execution block success | 100% for known policy violations | rolling 7d | Safety Owner | emergency policy patch, retest and replay |
| Stability | Incident recurrence on known failures | 0 repeated unmitigated critical signatures | rolling 30d | EM + Safety Owner | freeze affected lane until prevention check added |
| Performance | End-to-end run latency p95 | <= 8s baseline persona flow | rolling 24h | Inference DRI | enable routing fallback, tune decode policy |
| Availability | Successful run completion rate | >= 99% | rolling 24h | SRE/Operations Owner | incident response, rollback if persistent |
| Observability | Trace completeness for required stages | >= 99% of runs | rolling 24h | Observability DRI | block release until telemetry restored |

## Engineering Quality KPIs
- test pass rate by gate stage,
- retry rate per workflow step,
- reviewer reject-to-accept ratio,
- schema validation failure rate,
- policy validation false-negative count,
- heuristic retrieval hit rate and effectiveness uplift,
- prompt-policy evolution win rate versus baseline.

## Release Guardrails
- Canary promotion only if all critical SLOs are green through soak window.
- Automatic rollback when availability or safety SLO breaches exceed thresholds.
- Manual override requires EM approval and documented risk acceptance.

## Reporting Cadence
- Daily dashboard scan by DRIs.
- Weekly operating review with trend deltas and corrective actions.
- Monthly executive summary with reliability, safety, and velocity posture.

## Dashboard and Evidence Requirements
- Dashboard links must include gate pass trends, latency, errors, and safety events.
- Every milestone review includes evidence snapshots attached to gate packet.
- Missing telemetry is treated as a failed gate condition.
