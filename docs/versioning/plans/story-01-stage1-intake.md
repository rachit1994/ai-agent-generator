# OSV-STORY-01 — Stage 1 (V2) machine-runnable intake

| Field | Value |
|-------|-------|
| **Version ID** | `OSV-STORY-01` |
| **Tier** | 2.1 |
| **Backlog** | [`company-os-full-delivery-checklist.md`](../../architecture/company-os-full-delivery-checklist.md) §1 (first bullet) |
| **Completion definition** | [`company-os-path-to-100-percent.md`](../../architecture/company-os-path-to-100-percent.md) §3 (**M2 / S1a**) and §4 backlog **B1–B5** |

---

## 1. Goal

Automate discovery → research → question burst → doc pack in **target repo** → separate doc reviewer → `doc_review.json` → bounded revise → **plan lock** with phases, `step_id`, `depends_on`, `rollback_hint`, and contract steps.

---

## 2. Prerequisites

_None beyond Tier 2.1 spine and prior versions in this folder._

---

## 3. Scope

**In scope:** Orchestrated intake pipeline, artifacts on disk in target repo, fail-closed gates on malformed reviewer output.

**Out of scope (for this version):** Implementation execution (Stage 3); parallel lanes (Stage 2 full V7); **model-assisted doc regeneration or LLM-driven revise** (deterministic local regen only for OSV-STORY-01 — see [ADR 0002](../../adrs/0002-s1a-model-assisted-revise-deferred.md)); **service-backed reviewer attestation** beyond on-disk artifacts and CLI strict gates (see [ADR 0001](../../adrs/0001-s1a-reviewer-attestation-policy.md)).

---

## 4. Deliverables

- [x] `discovery.json` (or equivalent) schema-valid — `scaffold_project_intake` + `project_validate` / lock-readiness; tests `test_project_intake_scaffold.py`, `test_project_validate.py`
- [x] `research_digest.md` + question artifacts — written by scaffold; lock-readiness requires non-empty digest + `question_workbook.jsonl`
- [x] Doc pack paths declared and written — **S1a scope:** intake stubs + plan-side contract (`project_plan.json` with `rollback_hint` + `contract_step`); full product doc-pack manifest beyond intake is **S1b / program** (see [path-to-100 §3.2](../../architecture/company-os-path-to-100-percent.md))
- [x] `doc_review.json` with pass/fail + findings — schema + `apply_intake_doc_review_result`; tests `test_project_intake_revise.py`, `test_project_validate.py`
- [x] Lockable `project_plan.json` with contract steps — `project_schema` + `write_project_plan_lock` / readiness; tests `test_project_plan_lock.py`, `test_stage1_golden_flow.py`

---

## 5. Completion confirmation (this version is *shipped*)

Confirm each item before marking the version complete.

- [x] Golden-repo demo: cold start → plan lock without manual file edits — **`./scripts/stage1-cold-start-demo.sh`** (writes plan via heredoc; otherwise CLI-only); runbook [§Golden cold start](../../runbooks/stage1-intake-failures.md); test `test_stage1_cold_start_demo.py`
- [x] Reviewer identity separate from planner in config + audit log — **S1a:** on-disk `planner_identity.json` / `reviewer_identity.json` + lock-readiness checks + `session_events` / `project status`; **service credentials:** out of scope ([ADR 0001](../../adrs/0001-s1a-reviewer-attestation-policy.md))
- [x] Revise loop respects max retries; surfaces `blocked_human` when exhausted — `test_project_intake_revise.py`, `test_stage1_golden_flow.py`

---

## 6. Working verification (this version is *proven*)

Evidence must exist in CI, `local-prod`, or a signed reference run — not only local developer machines.

- [x] Automated test: invalid `doc_review.json` rejected — `test_project_validate.py`
- [x] CI job: intake golden path < N minutes wall clock (budget declared) — `.github/workflows/ci.yml` job **`stage1-preflight`**; cap **`STAGE1_SUITE_MAX_SECONDS`** + `./scripts/run-stage1-suite.sh` (whole-suite budget; per-scenario cap optional per [path-to-100 §3.1](../../architecture/company-os-path-to-100-percent.md))
- [x] Trace: every artifact hash referenced from `session_events` or platform event stub — **S1a:** `intake/lineage_manifest.json` + `intake_lineage_manifest_*` on driver `session_events.jsonl` and `project status` → `session_events` ([path-to-100 §3.1](../../architecture/company-os-path-to-100-percent.md) item **(A)**); **platform durable sink:** M0/M1 item **(B)**

---

## 7. Observability & operations

`doc_review` latency + retry counts dashboarded or logged structurally.

---

## 8. Documentation & ownership

`docs/runbooks/` intake failure modes; `docs/adrs/` for S1a policy (**0001**, **0002**) and future schema ADRs.

---

## 9. Version sign-off

Use **[`company-os-path-to-100-percent.md`](../../architecture/company-os-path-to-100-percent.md) §3.1 (S1a)** as the bar for “100% of this version in repo.” **§4 backlog B1–B5** resolved there (implementation + ADRs).

- [x] Sections **5** and **6** engineering criteria met **in-repo** (evidence above + CI `stage1-preflight`); attach **your tracker** links / run IDs when promoting beyond this repository.
- [ ] No known **P0/P1** defects open against this version’s acceptance criteria — *program tracker*
- [ ] **Owner** name and **date** recorded in your project system (not duplicated here).

## Progress note (implementation snapshot)

Automated coverage now present:

- `invalid doc_review rejected`:
  - `src/orchestrator/tests/unit/test_project_validate.py`
- bounded revise loop (`retry_allowed` -> `blocked_human`):
  - `src/orchestrator/tests/unit/test_project_intake_revise.py`
- plan-lock readiness + artifact:
  - `src/orchestrator/tests/unit/test_project_plan_lock.py`
- golden success/failure Stage 1 flows:
  - `src/orchestrator/tests/unit/test_stage1_golden_flow.py`
- runbook consistency check:
  - `src/orchestrator/tests/unit/test_stage1_runbook_consistency.py`
- runtime plan-lock on `project run` / `continuous` + strict reviewer forwarding (`require_non_stub_reviewer` / CLI flags / `SDE_REQUIRE_NON_STUB_REVIEWER` when lock enforcement is on):
  - `src/orchestrator/api/project_driver.py`, `continuous_run.py`, `runtime/cli/main.py`; tests in `test_project_meta.py`, `test_continuous_run.py`
- operator doc for flags and env semantics:
  - `docs/sde/project-driver.md` (Stage 1 plan lock section), `docs/runbooks/stage1-intake-failures.md`
- CI preflight job:
  - `.github/workflows/ci.yml` (`stage1-preflight`); whole-suite wall clock capped via `STAGE1_SUITE_MAX_SECONDS` + `./scripts/run-stage1-suite.sh`
- `session_events.jsonl` correlates `intake/lineage_manifest.json` when present (`intake_lineage_manifest_*` on driver start, tick, terminal — `lineage_manifest_session_event_snapshot` in `project_plan_lock.py`; tests in `test_project_plan_lock.py`, `test_project_meta.py`); `describe_project_session` merges the same snapshot into status `session_events` (`test_project_status.py`)
- B4 structured export: `write_project_stage1_observability_export` / CLI `project export-stage1-observability` → `intake/stage1_observability_export.json` (`test_project_stage1_observability_export.py`, runbook §Structured observability export)
- B5 cold-start narrative: `./scripts/stage1-cold-start-demo.sh` (runbook §Golden cold start; `test_stage1_cold_start_demo.py` runs the script in the Stage 1 suite)
- B1 / B2 (S1a): closed via ADRs [0001](../../adrs/0001-s1a-reviewer-attestation-policy.md) and [0002](../../adrs/0002-s1a-model-assisted-revise-deferred.md) (strict reviewer CLI/env remains the production lever; model revise deferred to a future story)

Still pending for full checklist closure in this plan:

- separate reviewer identity/credentials proof and audit signal
- tighter per-scenario wall-clock assertions inside golden tests (optional; whole-suite cap above already gates CI)
- full artifact hash lineage binding into durable/platform event path
- production/local-prod observability for `doc_review` latency + retries

---
*Generated by `docs/versioning/_generate_plans.py` — safe to edit this file in place after generation. To refresh **`docs/versioning/INDEX.md`** only (without overwriting any `plans/*.md`), run: `python3 docs/versioning/_generate_plans.py --index-only`.*
