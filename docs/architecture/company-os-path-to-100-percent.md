# Company OS — path to 100% (definitions, `src/` reality, actionable backlog)

**In plain words:** the [full delivery checklist](company-os-full-delivery-checklist.md) describes **~83** top-level unchecked outcomes today (Tier **2.1** story + **2.2** platform). This repository’s **`src/`** tree mainly implements the **local SDE spine** and a **partial** Tier **2.1** Stage 1 (“machine-runnable intake”) slice. **You cannot reach “100% of the whole checklist” inside this repo alone** without building deployable services, contracts, worker/sandbox, UI, and the rest of §3–15. This document **names what “100%” can mean**, **how much is left vs `src/`**, and **what to implement next** so that completing the listed work **honestly closes** the chosen milestone (without hand-waving).

**Companion docs:** [gap analysis vs `src/`](company-os-gap-analysis-src-vs-checklist.md) (code truth), [remaining work](company-os-remaining-work.md) (backlog narrative), [goal completion](architecture-goal-completion.md) (tier semantics), version plan [OSV-STORY-01](../versioning/plans/story-01-stage1-intake.md).

---

## 1. Pick your “100%” (milestones)

| Milestone | What “done” means | Achievable in this repo (`coding-agent`) alone? | Primary evidence |
|-----------|-------------------|--------------------------------------------------|------------------|
| **M0 — Whole checklist** | Every §1–2 **and** §3–15 checkbox in the [full checklist](company-os-full-delivery-checklist.md) with deployable services, `local-prod`, tests, runbooks | **No** — requires new trees (`src/contracts/`, `src/services/`, `tools/`, `infra/`, …) and many runtime products listed in §4 | Checklist + [gap analysis §3–15](company-os-gap-analysis-src-vs-checklist.md) (`missing`) |
| **M1 — Tier 2.1 product story (Stages 1–8)** | [Checklist §1](company-os-full-delivery-checklist.md) *and* action-plan Stages **2–8** as **real** multi-agent, durable events/memory, learning loop — not only local harness | **Mostly no** — same blockers as M0 for Stages **6–8** (durable platform) and large parts of **2–5** (service-backed enforcement) | [Remaining work §A–B](company-os-remaining-work.md) |
| **M2 — OSV-STORY-01 “Stage 1 slice” 100%** | Version [OSV-STORY-01](../versioning/plans/story-01-stage1-intake.md) **§5–6 + §9 sign-off** satisfied with **automated** tests + CI + documented operator path; Stage 1 **gates** and **artifacts** match the plan’s acceptance (below) | **Yes** (with bounded scope; see §3 **S1a vs S1b**) | `scripts/run-stage1-suite.sh`, [runbook](../runbooks/stage1-intake-failures.md), [project driver](../sde/project-driver.md) |
| **M3 — Tier 2.1 checklist §1 first bullet only (literal)** | “Automated discovery → … → **separate doc review agent** → …” end-to-end **without** human-authored intermediate files beyond policy | **Not today** — needs autonomous agent loop + credentialed reviewer runtime (outside current `orchestrator` scope) | [Gap analysis Stage 1 remaining](company-os-gap-analysis-src-vs-checklist.md) |

**Rule:** If you say “we are at 100%,” **name the milestone** (M0–M3). For this codebase, the only milestone that a single team can close **with evidence in `src/` + CI + docs** without spinning new services is **M2** (optionally tightened toward **M3** as a later program).

---

## 2. Full checklist vs `src/` (magnitude)

- **Checklist file:** [company-os-full-delivery-checklist.md](company-os-full-delivery-checklist.md) — **83** lines still use `- [ ]` (unchecked) as of the last edit pass that counted them.
- **`src/` today:** [gap analysis](company-os-gap-analysis-src-vs-checklist.md) — strong **orchestrator + pipeline + gates**; **no** `src/contracts/`, **no** `src/services/`, **no** `tools/contract-lint`, **no** deployable Tier **2.2** services.
- **Implication:** **M0** is **~0%** complete on §3–15. **M1** is **partial** on §1–2 only where local/session code exists. **M2** is the **right “100% project” target** for intake/plan-lock work **anchored in this repository**.

---

## 3. OSV-STORY-01 — definition of **100%** (M2) and split **S1a / S1b**

### 3.1 S1a — “100% of OSV-STORY-01 in repo” (recommended closure target)

When **all** of the following are true, treat **OSV-STORY-01** as **100% complete for the `coding-agent` repo** (sign off M2 / S1a):

1. **Deliverables (plan §4)** — each has **automated** proof (pytest and/or CI), not only manual demo:
   - `discovery.json` schema-valid with **`goal_excerpt`** semantics enforced ([`test_project_validate` / intake tests](../../src/orchestrator/tests/unit/)).
   - `research_digest.md` + question artifacts present and validated at **plan-lock readiness** ([`project_plan_lock.py`](../../src/orchestrator/api/project_plan_lock.py), tests).
   - Doc pack / intake merge anchor rules enforced ([`project_intake_util.py`](../../src/orchestrator/api/project_intake_util.py), status + validate).
   - `doc_review.json` pass/fail + findings schema fail-closed ([`project_validate.py`](../../src/orchestrator/api/project_validate.py)).
   - `project_plan.json` lockable: contract metadata (`rollback_hint`, `contract_step`, etc.) enforced where the schema promises ([`project_schema.py`](../../src/orchestrator/api/project_schema.py), plan-lock readiness).

2. **Completion confirmation (plan §5)**  
   - **Golden path:** **done** — runbook §Golden cold start + [`scripts/stage1-cold-start-demo.sh`](../../scripts/stage1-cold-start-demo.sh) (CLI: scaffold → plan → `intake-revise` → `plan-lock` → `validate --require-plan-lock` → export); [`test_stage1_golden_flow.py`](../../src/orchestrator/tests/unit/test_stage1_golden_flow.py) covers success/failure classes; [`test_stage1_cold_start_demo.py`](../../src/orchestrator/tests/unit/test_stage1_cold_start_demo.py) runs the shell demo in CI. Optional `run --enforce-plan-lock` remains a separate operator choice.
   - **Reviewer ≠ planner:** enforced **at artifact + lock-readiness** level (today: `planner_identity.json` / `reviewer_identity.json` + doc_review match + non-stub policy when enabled). **100% S1a** still allows **local** attestation types when strict flags are off; **strict** path must be **test-covered** for CI that opts in.
   - **Revise loop:** `blocked_human` after retry cap — covered by [`test_project_intake_revise.py`](../../src/orchestrator/tests/unit/test_project_intake_revise.py).

3. **Working verification (plan §6)**  
   - Invalid `doc_review` rejected — **test exists** (keep green).
   - **CI wall clock:** `STAGE1_SUITE_MAX_SECONDS` + `./scripts/run-stage1-suite.sh` in [`.github/workflows/ci.yml`](../../.github/workflows/ci.yml) — **done**; optional **per-scenario** budgets remain a **polish** item (not a blocker for S1a if you document the choice).
   - **Trace / hashes:** **(A) implemented (session + status):** `session_events.jsonl` driver lines and `project status` → `session_events` carry the same `intake_lineage_manifest_*` fields when `intake/lineage_manifest.json` is readable on disk (manifest file sha256 + counts); `status_at_a_glance` surfaces presence/unreadable. See `lineage_manifest_session_event_snapshot` in `project_plan_lock.py` (merged in `project_driver.py` and `project_status.py`). **(B)** platform-wide binding into a **durable** event store remains **M0/M1** (separate services).

4. **Version sign-off (plan §9)** — tracker links: CI job name, commit SHA, test module list.

### 3.2 S1b — “100% of checklist §1 Stage 1 *wording* (literal north star)”

The checklist bullet for Stage 1 also implies **autonomous** discovery/research/question burst and a **separate doc review agent** (LLM/runtime), not only deterministic regeneration. That is **not** fully replaceable by `orchestrator` today ([remaining work](company-os-remaining-work.md): model-driven revise, service-backed reviewer attestation, observability service, durable lineage). Treat **S1b** as **program work** beyond M2 unless you **narrow the checklist** with an ADR.

**If the program adopts S1b as mandatory:** add new version plans (e.g. reviewer service, intake agent service) and **new repositories or `src/services/*`**; M2 alone is insufficient.

---

## 4. OSV-STORY-01 **B1–B5** backlog (M2 / S1a — **closed in-repo**)

Rows below are **closed** for **S1a** in this repository (acceptance satisfied; tests green). Keep them as the audit trail for what “M2 / S1a 100%” meant operationally; refresh [gap analysis](company-os-gap-analysis-src-vs-checklist.md) if Stage 1 behavior changes.

| # | Work item | Why it blocks “100%” today | Done when (acceptance) |
|---|-----------|----------------------------|-------------------------|
| **B1** | **Reviewer attestation (non-local-stub) for production policy** | **S1a closed (ADR path):** [ADR 0001](../adrs/0001-s1a-reviewer-attestation-policy.md) — `local_stub` allowed when strict flags off; **`--require-non-stub-reviewer`** / **`SDE_REQUIRE_NON_STUB_REVIEWER`** for production-style CLI; external verifier adapter **deferred** to a future story. |
| **B2** | **Model-assisted revise / regeneration** | **S1a closed (ADR path):** [ADR 0002](../adrs/0002-s1a-model-assisted-revise-deferred.md) — deterministic regen only for OSV-STORY-01; **[`story-01`](../versioning/plans/story-01-stage1-intake.md) §3** out-of-scope text updated. Model revise **deferred** to a future OSV story. |
| **B3** | **Session → audit trail for lineage (§6 trace)** | **Done (session + status):** same `intake_lineage_manifest_*` fields on driver `session_events.jsonl` lines **and** on `project status` → `session_events` (plus `status_at_a_glance` presence / unreadable + red flag when corrupt). **Still M0:** export to a durable platform event sink. |
| **B4** | **Observability for doc_review / revise** | **S1a minimum done:** `sde project export-stage1-observability` → `intake/stage1_observability_export.json` (`revise_metrics` + `status_at_a_glance`; schema `1.0` / `project_stage1_observability`; tests in `test_project_stage1_observability_export.py`; runbook §Structured observability export). Session JSONL + `project status` remain the live sources. **Still M0:** hosted metrics service / dashboards. |
| **B5** | **Golden “cold start” narrative** | Plan §5 asks demo | **Done:** `./scripts/stage1-cold-start-demo.sh` + runbook §Golden cold start; `./scripts/run-stage1-suite.sh` includes `test_stage1_cold_start_demo.py` (runs the script) alongside `test_stage1_golden_flow.py`. |

**B1–B5** are resolved for **S1a** in this repo (B1/B2 via [ADR 0001](../adrs/0001-s1a-reviewer-attestation-policy.md) and [ADR 0002](../adrs/0002-s1a-model-assisted-revise-deferred.md); B3–B5 via implementation). **Re-run** `./scripts/run-stage1-suite.sh` after material changes; refresh [gap analysis](company-os-gap-analysis-src-vs-checklist.md) when Stage 1 behavior shifts; use your tracker for **OSV-STORY-01** §5–6 sign-off links.

---

## 5. After M2 — what is left for **M1 / M0** (still “project” in Company OS sense)

Not exhaustive; use [remaining work](company-os-remaining-work.md) and [checklist §2](company-os-full-delivery-checklist.md):

- **Stage 2 true lanes:** durable queues, federated coordination — not only `project_parallel` / worktrees.
- **Stages 3–5 at platform:** separation of duties **service**, orchestrated writes **boundary**, verification/DoD **across services**.
- **Stages 6–8:** durable **event store**, **memory lifecycle**, learning/promotion **services**.
- **§3–15:** contracts, **17** named services, worker/sandbox, SDKs, infra, UI, integration/E2E/chaos/security pillars — each maps to a **version plan** under [`docs/versioning/plans/`](../versioning/) or new program charters.

Completing **that** set is what moves you toward **M1** then **M0**.

---

## 6. Changelog

- **2026-04-19:** Initial document — disambiguates M0–M3, counts checklist openness, defines **S1a/S1b**, and lists **B1–B5** backlog to close **OSV-STORY-01** in-repo without claiming full Company OS.
- **2026-04-19 (later):** Implemented **B3 session trace (A)** — ``lineage_manifest_session_event_snapshot`` merged into ``session_events`` for driver start / tick / terminal (`project_driver.py` + tests).
- **2026-04-19 (status embed):** Same snapshot merged into ``describe_project_session`` → ``session_events`` and glance (`project_status.py` + tests).
- **2026-04-19 (B4 export):** ``export-stage1-observability`` CLI + ``write_project_stage1_observability_export`` / schema validator (`project_stage1_observability_export.py`).
- **2026-04-19 (B5 cold start):** ``scripts/stage1-cold-start-demo.sh`` + runbook narrative + suite test `test_stage1_cold_start_demo.py`.
- **2026-04-19 (B1/B2 ADRs):** [ADR 0001](../adrs/0001-s1a-reviewer-attestation-policy.md), [ADR 0002](../adrs/0002-s1a-model-assisted-revise-deferred.md); OSV-STORY-01 §3 out-of-scope updated.
- **2026-04-19 (release):** **`sde` 0.11.0** in `pyproject.toml` / `uv.lock` (S1a M2 shipped in **0.9.5**; subsequent **minor** bumps follow `.githooks/pre-push`); versioning log row consolidated; OSV-STORY-01 plan §4–§6 checkboxes updated for in-repo S1a evidence (§9 tracker lines still program-owned).
