# Achieving the master architecture goal (completion definition)

This document ties **[AI Professional Evolution — Master Architecture](AI-Professional-Evolution-Master-Architecture.md)** to the **versioned extension specs** under `docs/coding-agent/` ([execution](../coding-agent/execution.md), [planning](../coding-agent/planning.md), [completion](../coding-agent/completion.md), [events](../coding-agent/events.md), [memory](../coding-agent/memory.md), [evolution](../coding-agent/evolution.md), [organization](../coding-agent/organization.md)). It answers: *when all “versions” are built in this repo, have we completely achieved the architecture’s goal?*

**Operational plan:** [action-plan.md](../onboarding/action-plan.md) — product north star (full-stack, company-like process, parallel junior agents, quality + speed), **global precedence** (V1 safety before self-learning and speed), phased delivery, and **capability yardsticks** beyond hard-stop checklists.

---

## 1. The goal (from the master document)

### 1.0 Product goal (this repository’s coding-agent slice)

**Intent:** Enable **one SDE-driven program** to execute a **product-sized** objective (for example a **full-stack application**: UI, API, persistence, tests, CI, operational docs) using **company-like** discipline—**parallel workstreams**, **reviews**, **verification**, **governed learning**, and **gates that support reliable pushes to production**—with **agents modeled as junior engineers** (mistakes expected; process and evidence minimize blast radius). **Self-learning is motivated and required** where specs say so (for example planning’s `learning_events.jsonl`), but **never** bypasses **V1** execution safety ([execution.md](../coding-agent/execution.md) HS01–HS06). See [action-plan.md](../onboarding/action-plan.md) §§1–3.

**Executive intent:** Build agents that **evolve like professional engineers** over time—not one-off task demos—with **production-grade, long-horizon, auditable** operation, **event-sourced lineage** from execution through learning to promotion, **policy-gated autonomy**, and **local-first** contracts ([§1 Executive Summary](AI-Professional-Evolution-Master-Architecture.md), [§2 System Vision](AI-Professional-Evolution-Master-Architecture.md)).

**Non-negotiables from the blueprint:** safety over autonomy, **no hidden learning**, deterministic evaluation for risky changes, **machine-checkable** authority and transitions, explicit arbitration of safety / quality / velocity / autonomy ([§2 Constraints](AI-Professional-Evolution-Master-Architecture.md)).

**Binary production gates (must pass for production claims):** §14 lists `CriticalRegressionCount == 0`, `UnsafeActionRate <= 0.02`, `ReplayCriticalDriftCount == 0`, `RollbackDrillPass == true`, `ResourceBudgetBreaches == 0`.

---

## 2. Two senses of “complete”

### 2.1 Extension ladder complete (this repository’s specs)

**Definition:** Every extension spec under `docs/coding-agent/` has been **implemented**, **verified**, and its own **“Success is not assumed”** (or equivalent acceptance) **checklist and benchmarks** are satisfied with **retained evidence** (run ids, artifacts, CI logs).

| Extension (version label) | Spec | Hard-stop range | Role in the master goal |
|---------------------------|------|-------------------|-------------------------|
| V1 | [execution.md](../coding-agent/execution.md) | HS01–HS06 | **Trust base:** auditable runs, balanced gates, token/context integrity—**foundation for “no hidden truncation” and replayable execution evidence**. **Dominates** all later extensions ([action-plan.md](../onboarding/action-plan.md) §2). |
| V2 | [planning.md](../coding-agent/planning.md) | HS07–HS12 | **Company planning + motivated learning:** discovery through plan lock, `learning_events.jsonl`—**within** the V1 safety envelope. |
| V3 | [completion.md](../coding-agent/completion.md) | HS13–HS16 | **Build + prove:** atomic steps, verification bundle, DoD—**full-stack delivery** toward production-leaning evidence. |
| V4 | [events.md](../coding-agent/events.md) | HS17–HS20 | **Event-sourced lineage** and replay fail-closed—core to “execution → learning → promotion” traceability. |
| V5 | [memory.md](../coding-agent/memory.md) | HS21–HS24 | **Institutional memory** with provenance and quarantine—implements “memory is not unstructured cache.” |
| V6 | [evolution.md](../coding-agent/evolution.md) | HS25–HS28 | **Reflection, promotion packages, canary, practice**—implements policy-gated learning and lifecycle without unconstrained self-modification. |
| V7 | [organization.md](../coding-agent/organization.md) | HS29–HS32 | **Many juniors + process:** multi-agent, IAM, leases, federation—**parallel agents** with coordination safety. |

**When this tier is done:** You have a **contract-complete, evidence-first spine** that implements the **behaviors and gates** the architecture requires for the **coding-agent / SDE slice** and the **platform behaviors** those specs encode. That is **necessary** for honest “we ship the blueprint’s control plane story” claims for this codebase. **Together, V1–V7 implement one combined product story** (full-stack, company-like, production-gated); the labels are **staged delivery**, not separate products ([action-plan.md](../onboarding/action-plan.md) §3).

**Capability note:** Satisfying HS01–HS32 is **necessary** hygiene; **capability yardsticks** (held-out tasks, regression, E2E smoke, rollback drill) are tracked in [action-plan.md](../onboarding/action-plan.md) §4 and master **§14**.

### 2.2 Full operating system as literally described in every section

**Definition:** All services, storage choices, observability products, KPI dashboards, readiness program scoring, and optional cloud-adjacent components **exactly as named** in later sections of the master document (e.g. Postgres event store, OpenTelemetry, dedicated worker pools, §28 100-point program) are **deployed, operated, and continuously evidenced**.

**Honest scope statement:** The master document describes an **organization-scale OS** (many services in §15–§19, §27–§28). The **`docs/coding-agent/*` specs deliberately abstract** some of those into **logical artifacts** (`replay_manifest.json`, `event_store/` paths, etc.) without mandating a single vendor or database in every environment. **Completing every extension spec does not by itself instantiate every named service** (e.g. a specific Postgres topology) unless your **local-prod profile** pins those choices and proves them in §14/§28 gates.

**Therefore:**

- **“All versions (extensions) built”** ⇒ **Tier 2.1 complete** ⇒ you have met the **architectural goal for controllable, auditable evolution** *as encoded in this repo’s contracts*.
- **“Entire master document materially deployed”** ⇒ **Tier 2.2** ⇒ requires **additional workstreams** beyond merging the markdown specs: infrastructure bind, operations runbooks, readiness scoring, and evidence from §28.

---

## 3. Coverage matrix (master themes → specs → concrete HOW)

Each spec now includes a **"How it works in practice"** section with concrete flows. The matrix below links master themes to both specs and HOW sections.

| Master theme | Sections | Primary specs | How section in spec | Evidence type |
|--------------|----------|---------------|---------------------|----------------|
| Long-horizon execution + review | §3, §10, §11 | execution, completion | execution §"How the runtime drives a full-stack task"; completion §"How the build loop works" | `traces.jsonl`, `review.json`, verification bundle |
| Self-learning / reflection / practice | §3, §9 | planning, evolution | planning §"How planning and learning work"; evolution §"How self-improvement and progression work" | `learning_events.jsonl`, `reflection_bundle.json`, practice artifacts |
| Event sourcing + replay | §12, §14 | events | events §"How the event trail works" | `replay_manifest.json`, HS18 |
| Memory + contradiction | §8, §18 | memory | memory §"How memory supports full-stack delivery" | provenance, quarantine, HS22 |
| Lifecycle + promotion | §6, §13 | evolution | evolution §"Promotion mechanics" | promotion packages, HS25–HS28 |
| Multi-agent + IAM | §5, §15–§16 | organization | organization §"How multi-agent spawning works" | leases, permission matrix, HS29–HS32 |
| Hard release gates | §14 | execution + events + completion | action-plan §4 "CTO gates" | binary gate metrics |
| Roadmap Phases 0–4 | §17 | events → memory → evolution → organization | action-plan §7 "Phased implementation" | phase exit evidence per §17 |

---

## 4. What you must still do after specs are “green”

To **fully align** with §**28** (Production Readiness Program) and §**15** (concrete production architecture names):

1. **Bind logical specs to chosen infra** (e.g. event store technology, vector store, OTel export)—document in `local-prod` profile and prove replay/manifest conformance.
2. **Run §14 gates continuously** with stored artifacts; no production claim without `RollbackDrillPass` and zero critical regressions.
3. **Close P0/P1** from master §19.D in your tracker; unresolved P0/P1 caps readiness per §28.
4. **Operate governance cadence** (§28.5)—weekly evidence completeness and Go/Hold/No-Go log.

Until then, the correct public posture is: **“Extension ladder complete; platform operational completeness per §28 in progress.”**

---

## 5. Links

- Master blueprint: [AI-Professional-Evolution-Master-Architecture.md](AI-Professional-Evolution-Master-Architecture.md)
- Spec index and V1–V3 redirects: [README.md](../README.md)
- Research alignment (self-improvement techniques): [research/self-improvement-research-alignment.md](../research/self-improvement-research-alignment.md)

---

## Changelog

- **2026-04-18:** Product goal (§1.0), V1 dominance note, combined V1–V7 narrative, capability yardsticks pointer, link to [action-plan.md](../onboarding/action-plan.md).
- **2026-04-17:** Initial completion definition and coverage matrix for coding-agent extensions vs master architecture scope.
