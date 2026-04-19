# Company OS — full delivery checklist (25% → 100%)

**In plain words:** this is **only** a list of what must exist for the **whole company operating system** (master architecture + end-to-end product story) to be **honestly at 100%**. It does **not** describe how to build each item. The current **`src/`** tree mainly ships the **local SDE spine** (~25% of this list, depending how you count partials); finishing everything here is what moves the program toward **100%**.

**Sources of truth:** [`AI-Professional-Evolution-Master-Architecture.md`](AI-Professional-Evolution-Master-Architecture.md), [`operating-system-folder-structure.md`](operating-system-folder-structure.md), [`onboarding/action-plan.md`](../onboarding/action-plan.md) §2–8, [`architecture-goal-completion.md`](architecture-goal-completion.md) (Tier 2.1 vs Tier 2.2).

**Per-feature version plans:** each checklist line is tracked as a version with completion + verification sections in [`../versioning/`](../versioning/) ([`README`](../versioning/README.md), [`INDEX`](../versioning/INDEX.md), [`plans/`](../versioning/plans/)).

**Path to 100% (milestones vs `src/`):** [`company-os-path-to-100-percent.md`](company-os-path-to-100-percent.md) — defines **M0–M3**, counts open checklist items, and lists the **actionable backlog** to honestly claim **OSV-STORY-01** complete in this repository without implying every §3–15 service exists.

---

## How to read “100%”

| Tier | Meaning | Done when |
|------|---------|-----------|
| **2.1 — Product story** | V1–V7 **behaviors** from the action plan: full intake → parallel build → verify → DoD → learning → durable events/memory, with **separation of duties** and **no self-approval**, on real repos—not only artifacts under `outputs/`. | Every **Stage 1–8** item in §2 below is implemented **without** the “shipped slice / roadmap” caveats in [`action-plan.md`](../onboarding/action-plan.md), and **§8 yardsticks** have automated or scripted measurement on reference programs. |
| **2.2 — Master OS** | Every **named deployable** in the master-aligned layout: versioned **contracts**, **services**, **agent** packages, **deterministic worker** + **sandbox**, **libraries**, **infra**, **tools**, and **test** pillars as **running** components under the **`local-prod`** profile, with **non-bypass ownership** enforced at boundaries—not only stubs or local JSON. | Every **§3–11** checkbox below is satisfied; services pass **extraction contract** drills and **contract conformance** before deploy. |

**100% for “whole company OS” in this document** means **both Tier 2.1 and Tier 2.2** unless your program explicitly caps scope at 2.1 (then treat §3–11 as out of scope and re-baseline the percentage).

---

## 1. End-to-end delivery story (action plan — Tier 2.1)

- [ ] **Stage 1 (V2 planning) — machine-runnable intake:** automated discovery → research → question burst → doc pack written to **target repo** → **separate** doc review agent → `doc_review.json` → bounded revise loop → **plan lock** (`project_plan.json` with phases, `step_id`, `depends_on`, `rollback_hint`, contract steps).
- [ ] **LearningFirstProfile (V2):** enforced minimum learning events (e.g. plan-lock floor) in **`learning_events.jsonl`**, not advisory-only.
- [ ] **Stage 2 (V7) — true parallel lanes:** dependency-grouped workstreams, **concurrent** lanes, **per-lane** queues, bounded **`max_concurrent_agents`**, **not** only sequential driver + optional worktrees.
- [ ] **Leases + heartbeats:** lease grant/renew/expiry, **heartbeat** timeout → reassignment or `blocked_human` with reason; **no writes outside lease** enforced by orchestrator on **all** file mutations (not prompt-only).
- [ ] **Contract-step gating:** shared API/DB/schema **contract steps** block dependent lanes until review + verification evidence exists.
- [ ] **Stage 3 — separation of duties:** **Implementor** cannot approve work; **Reviewer** is always a **separate** model call / role with distinct credentials/context; **Planner** cannot self-approve docs.
- [ ] **Stage 3 — orchestrated writes:** all implementation writes go through **orchestrator APIs** that enforce lease + trace + gate order (no direct “model wrote files” shortcuts).
- [ ] **Per-step review loop:** `step_reviews/<step_id>.json` with findings, evidence refs, bounded retries, `remediation_required` / `blocked_human` on critical path per action-plan semantics.
- [ ] **Stage 4 — verification from plan:** commands assembled from **plan metadata**; `verification_logs/`; **`verification_bundle.json`** drives pass/fail and **failure attribution** loop back to Stage 3 with re-review after fix.
- [ ] **Stage 5 — DoD automation:** `definition_of_done` items (reviews, verification bundle, doc pack manifest, smoke, security smoke when declared) are **checked by code**, not only human-readable stubs; terminal status cannot lie (HS15-class honesty end-to-end).
- [ ] **Stage 6 — cross-run learning (V6):** reflection with **causal closure**, practice loop from skill gaps, **canary** shadow runs, **promotion** packages with **independent evaluator** signals—**durable** and **policy-gated**, not JSON-only demos.
- [ ] **Stage 7 — durable event platform:** append-only **event store** with envelopes, integrity, **fail-closed replay**, kill switch as first-class **platform** events (beyond per-run `traces.jsonl` / local mirrors).
- [ ] **Stage 8 — durable memory (V5):** episodic + semantic + skill stores with **retrieval/write policies**, **quarantine** workflow, decay/recertification, **provenance** on every retrieve used in decisions.
- [ ] **Continuous CTO gates:** token/context/refusal/retry budgets on **every** LLM call; hard-stop sweeps at **stage boundaries**; composite balanced gates block **`completed_review_pass`** when subscores fail (action-plan §4 table fully automated).

---

## 2. Version ladder completeness (V1–V7 — evidence, not labels)

- [ ] **V1:** HS01–HS06 + balanced gates + token/refusal/static evidence **on all run classes** (single task, benchmark aggregate where applicable, project session, parallel lanes).
- [ ] **V2:** HS07–HS12 tied to **real** planning artifacts and doc-review outcomes (not scaffold-only).
- [ ] **V3:** HS13–HS16 tied to **real** step reviews, verification bundle, DoD progression.
- [ ] **V4:** HS17–HS20 on **durable** lineage (platform event store + replay manifest policy).
- [ ] **V5:** HS21–HS24 on **durable** memory services (not only run-dir harness files).
- [ ] **V6:** HS25–HS28 on **operational** reflection / practice / canary / promotion paths.
- [ ] **V7:** HS29–HS32 on **live** multi-agent coordination (IAM, federation, coordination safety at scale).

---

## 3. Contracts (versioned, linted, owned)

- [ ] **`src/contracts/`** tree populated: event, policy, lifecycle, capability, authz, service RPC schemas **as published contracts** (not ad-hoc Python dicts only).
- [ ] **Objective arbitration** and **policy bundle** schemas versioned and **activated** through a single owner path (see §4 `policy-management`).
- [ ] **Role / stage / risk matrix** and **approval tokens** (`identity-authz`) enforced on high-risk actions.
- [ ] **Contract lint + CI gate** (`tools/contract-lint`): fail-closed on breaking changes without version bump and migration story.
- [ ] **Schema upcaster** tool for supported upgrade paths (`tools/schema-upcaster`).

---

## 4. Deployable services (master-aligned — Tier 2.2)

Each item: **`api/` + `runtime/` + `tests/` + `README.md`**, independently deployable, **contract conformance** green, **README extraction steps** verified.

- [ ] **objective-policy-engine**
- [ ] **lifecycle-governance** (sole owner of promotion/autonomy mutations)
- [ ] **identity-authz** (sole issuer/validator of scoped approval tokens)
- [ ] **policy-management** (sole activator of policy bundles)
- [ ] **event-store** (durable append-only; scaling/replay SLOs defined)
- [ ] **projection-query** (query models over events)
- [ ] **memory-lifecycle** (sole memory mutator)
- [ ] **capability-graph** (certification state, capability nodes)
- [ ] **reflection-rca**
- [ ] **learning-update**
- [ ] **canary-rollout**
- [ ] **evaluation** (offline/online/regression/promotion evaluation pipelines per master doc)
- [ ] **safety-controller** (sole final veto on high-risk actions)
- [ ] **model-router**
- [ ] **quota-scheduler**
- [ ] **observability-gateway** (metrics/logs/traces export **bound** in `local-prod`)
- [ ] **incident-ops**
- [ ] **chaos-simulator**

---

## 5. Orchestrator & coordination (beyond current CLI package)

- [ ] **Service RPC** contract (`common_rpc.v1.json`) used for **inter-service** calls.
- [ ] **Hierarchy + deadlock** handling (`hierarchy.v1.json`, `deadlock.v1.json`) operational under multi-lane load.
- [ ] **Orchestrator** as **platform** scheduler: routes work across services/agents with **global precedence** from action-plan §5 enforced in code paths.

---

## 6. Deterministic worker & sandbox (production execution)

- [ ] **Deterministic worker** image/build pipeline (reproducible worker artifact).
- [ ] **Isolated sandbox** execution for code/tests (container or equivalent) with **policy-injected** limits.
- [ ] **Worker policies** enforced (resource, network, filesystem, egress).
- [ ] **Remote / optional runtimes** productized where architecture requires (not “local Mac only” as the only honest path).

---

## 7. Agent packages (distinct roles, certifiable)

- [ ] **junior-agent**, **midlevel-agent**, **senior-agent**, **architect-agent**
- [ ] **reviewer-agent** (cannot share implementor credentials or bypass gates)
- [ ] **evaluator-agent**
- [ ] **learning-agent**, **practice-agent**
- [ ] **manager-agent**, **specialist-agent**, **career-strategy-agent**
- [ ] **Career / progression / recertification / stagnation** flows from master doc wired to **capability-graph** + **lifecycle-governance** with measurable signals.

---

## 8. Libraries (SDKs consumers actually use)

- [ ] **event-sdk**
- [ ] **contract-validator** (runtime + CI)
- [ ] **lineage-sdk**
- [ ] **policy-eval-sdk**
- [ ] **memory-sdk**

---

## 9. Data plane

- [ ] **seed-curriculum** (managed content + versioning)
- [ ] **benchmark-suites** (beyond ad-hoc `jsonl`; suite versioning in product sense)
- [ ] **replay-manifests** catalog tied to **durable** event store

---

## 10. Infra & `local-prod`

- [ ] **`local-prod` profile** fully specified: storage bindings, secrets, backups, **monitoring** dashboards, SLOs/alerts **as code** or checked-in config.
- [ ] **backup-restore** runbooks **exercised** (drill evidence).
- [ ] **Storage choices** from master doc (§15-class) **pinned and operated**, not deferred.

---

## 11. Product surfaces omitted today

- [ ] **UI / dashboard** for runs, lanes, memory quarantine, promotions, incidents (if architecture treats them as in-product).
- [ ] **Operator runbooks** under `docs/runbooks/` kept in sync with shipped failure modes.

---

## 12. Testing pillars (repo-wide, not only unit)

- [ ] **Integration** tests per service boundaries
- [ ] **E2E** full-stack reference programs (UI + API + DB + tests + deploy smoke per action-plan §8)
- [ ] **Replay** tests on golden manifests against **durable** store
- [ ] **Chaos** tests (fault injection for scheduler, store, worker)
- [ ] **Security** tests (authz bypass attempts, token replay, lease escape)
- [ ] **Promotion** tests (lifecycle transitions refuse invalid states)

---

## 13. Governance artifacts (living documents)

- [ ] **ADRs** for major contract/service decisions
- [ ] **Threat models** updated per trust boundary shipped
- [ ] **Incident forensics** tool (`tools/incident-forensics`) operational against real telemetry

---

## 14. Readiness & metrics (master doc scoring / KPIs)

- [ ] **Readiness program** / KPI dashboards described in master architecture **implemented** and fed by **observability-gateway** (not placeholder).
- [ ] **Capability growth, error reduction, transfer, stability** metrics (master doc §25–29 class) **computed on a schedule** with historical retention.

---

## 15. Extraction & multi-tenant posture

- [ ] Every service passes **microservice extraction contract** (copy folder + contracts + SDKs only; register peers; conformance green).
- [ ] **Multi-tenant / org** boundaries defined where applicable (IAM, quotas, data isolation)—even if first customer is internal.

---

## Completion rule

When **every** checkbox in **§1–2** (Tier 2.1) **and** **§3–15** (Tier 2.2) is checked with **evidence** (tests, runbooks, deployed `local-prod`, dashboards), the **whole company OS** is at **100%** for the scope defined above. If the program **intentionally** caps at Tier 2.1, mark **§3–11** (and dependent §12–15 items) **out of scope** in your tracking system and rename the target (for example **“100% product story”**).

---

## Changelog

- **2026-04-19:** Linked **[`company-os-path-to-100-percent.md`](company-os-path-to-100-percent.md)** — milestone definitions vs **`src/`** and OSV-STORY-01 closure backlog.
- **2026-04-18:** Initial checklist (backlog-only; aligns action-plan stages with master-aligned layout and completion tiers).
