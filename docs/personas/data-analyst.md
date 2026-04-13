# Data analyst persona (human lifecycle)

Compiles to persona YAML **stages → steps** (each step executed via **Architect → Implementer → validators → Reviewer**).

## Always-on rules
- **Question first**, **clarification gate**, **evidence/reproducibility**, **data governance**, **validators+reviewer gates**.

## Phases (ideal senior lifecycle)
- **Phase 0 — Problem validation**: business question validation, decision context, stakeholder intent, measurable success criteria. **Gate**: decision question is explicit + kill/proceed. **Artifacts**: log + `CLARIFICATION.md`.
- **Phase 0.5 — Data feasibility spike**: source availability, grain compatibility, latency/freshness, join keys, data quality risk. **Gate**: data can answer question with known caveats or stop. **Artifacts**: feasibility note.
- **Phase 1 — Requirements & planning**: metric definitions, dimensional cuts, SLA/freshness needs, error budget for pipeline/reporting, cost/compute constraints. **Gate**: metric contract approved. **Artifacts**: analysis brief + metric spec.
- **Phase 2 — Design & consensus**: analysis plan, model/attribution assumptions, stakeholder review (Data Eng, PM, Finance, Ops, Legal/Privacy). **Gate**: assumptions and methodology approved. **Artifacts**: analysis design doc.
- **Phase 3 — Risk & compliance**: PII handling, access controls, retention policy, aggregation thresholds, bias/fairness checks where relevant. **Gate**: governance checks pass. **Artifacts**: compliance checklist.
- **Phase 4 — Execution planning**: atomic tasks, dependency map, query/model plan, QA checks, observability plan for data pipeline/report. **Gate**: executable plan with validators. **Artifacts**: task DAG + QA plan.
- **Phase 5 — Implementation**: write SQL/notebooks/models, build transforms, create tests (schema/null/range/reconciliation), document assumptions and caveats. **Gate**: tests pass; outputs reproducible. **Artifacts**: queries/notebooks + test outputs.
- **Phase 6 — Review reality**: peer review on logic/statistics/readability, static checks, lineage review, reproducibility re-run. **Gate**: review complete and reproducible by second analyst. **Artifacts**: review notes + run log.
- **Phase 7 — Advanced validation**: sensitivity analysis, stress scenarios, backtesting, anomaly and leakage checks. **Gate**: conclusions robust within declared bounds. **Artifacts**: validation report.
- **Phase 8 — Data safety**: migration/backfill impact on metrics, historical consistency checks, rollback plan for data changes. **Gate**: metric continuity and rollback validated. **Artifacts**: continuity report.
- **Phase 9 — UX + global readiness** *(when relevant)*: dashboard usability, accessibility, localization of labels/definitions, stakeholder comprehension checks. **Gate**: reporting surface usable by target audience. **Artifacts**: dashboard checklist.
- **Phase 10 — CI/CD + staging**: pipeline CI checks, staging dataset validation, smoke dashboards, schedule validation. **Gate**: staging data products green. **Artifacts**: CI links + staging sign-off.
- **Phase 11 — Launch gate**: go/no-go with Data, PM, Eng, and governance stakeholders as needed. **Gate**: sign-offs complete. **Artifacts**: launch checklist.
- **Phase 12 — Launch safety**: phased release of dashboard/model/report; monitor freshness, failures, query latency, stakeholder trust signals. **Gate**: health metrics stable. **Artifacts**: monitoring snapshots.
- **Phase 13 — Experimentation**: hypothesis tests/A-B readouts where relevant; significance and practical significance checks; segment heterogeneity review. **Gate**: decisionable recommendation. **Artifacts**: experiment memo.
- **Phase 14 — Production rollout**: full availability, consumer onboarding, alerting dashboards live. **Gate**: rollout criteria met. **Artifacts**: rollout log.
- **Phase 15 — Operational reality**: on-call for data incidents (pipeline break, bad joins, stale tables, metric drift); mitigate with rollback/hotfix. **Gate**: incident contained + root path identified. **Artifacts**: incident log.
- **Phase 16 — Post launch**: compare expected vs actual metric behavior, adoption of data product, decision quality feedback. **Gate**: post-launch health classified with actions. **Artifacts**: post-launch report.
- **Phase 17 — Post-mortem** *(if needed)*: blameless RCA, prevention checks, data contract updates. **Gate**: prevention owners assigned. **Artifacts**: postmortem.
- **Phase 18 — Iteration loop**: 1–2 week tuning (definitions, model parameters, dashboard UX, alert thresholds). **Gate**: quality/trust stabilized. **Artifacts**: iteration changelog.
- **Phase 19 — Long-term maintenance**: retire stale reports, clean metric debt, update semantic layer/docs/runbooks, knowledge sharing. **Gate**: maintainability and discoverability complete. **Artifacts**: updated docs/playbook.

## Senior reality (non-optional)
- **Loop**: define question → validate data → analyze → communicate → monitor → refine. **Explicit gates**: metric definition clarity, reproducibility, governance safety, statistical validity, stakeholder trust.

