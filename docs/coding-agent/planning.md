# Coding-Agent V2 Specification

## Goal

Extend V1 so SDE can drive a **production-leaning full-stack application** in the **target repository** with **evidence-backed planning upstream of code**: discovery, external research and differentiation, references to features in other projects, a **pre-implementation question policy**, **in-repo documentation**, a **documentation review gate**, and a **locked phased plan**—while inheriting V1 runtime contracts, strict balanced CTO gates, and hard-stops HS01–HS06.

**Priority order (V2 product posture):**

Global ordering is defined in [action-plan.md](../onboarding/action-plan.md) §2. Within V2, priorities are:

1. **Absolute safety floor (V1 / non-bypassable)** — [execution.md](execution.md) **HS01–HS06** and token/context integrity **always** win. “Self-learning first” means **first among planning activities inside the safe envelope**—not above execution safety. Learning must **never** override **HS03**, **HS04**, **HS06**, or any V1 gate; unsafe or ungoverned “learning” is invalid.
2. **Motivated self-learning (primary planning priority)** — Every major phase must **produce durable learning artifacts** (`learning_events.jsonl` and optional `learning_synthesis.md`): capture what was tried, what failed, what was inferred from research, and what the next run should do differently. Time and token budget should **prefer allocating margin to learning capture and synthesis** over shaving latency on mechanical steps—**after** V1 gates are satisfied for the run. Optional **playbook deltas** (human-reviewable text or structured hints only) may append under `.agent/sde/` when the plan allows.
3. **Planning quality and gate completeness** — Question policy, doc pack, doc review, and plan lock remain mandatory before implementation; learning **informs** them and is **recorded** when they change (e.g. `plan_amendment` rationale linked to `learning_events.jsonl` entries).
4. **Wall-clock speed (last)** — Optional performance budgets apply only after learning minima for the active **LearningFirstProfile** (see Execution Profiles) are met; speed must not cap learning below those minima.

## V2 Scope

In scope:
- Program discovery, research digest, differentiation thesis, and optional third-party / other-project feature references (with licensing and compatibility notes).
- Question workbook policy: block substantive implementation until resolved, explicitly deferred with owner and risk, or human override (artifact-backed).
- In-repo documentation pack under the target repo (paths below) plus run-scoped mirrors for audit.
- Documentation review gate (pass or fail closed) before any **implementation phase** (code-generating work beyond scaffolding explicitly allowed in plan).
- `project_plan.json`: phases, atomic step ids, dependencies, rollback points; plan amendments traced in `traces.jsonl` / `orchestration.jsonl`.
- **Primary self-learning loop:** append-only `learning_events.jsonl` (required per phase minima below), optional `learning_synthesis.md` after research and after doc review, and optional `playbook_delta.jsonl` (structured hints or markdown chunks only—no executable content). Learning outputs **drive** question updates, doc revisions, and plan amendments; traces must link `rationale_id` to `learning_event_id` where a decision cites prior learning.
- Bounded by schema, size caps, and HS10; **never** bypasses safety or governance gates (HS01–HS06, especially HS04).
- Optional `performance_budget` fields in `summary.json` when speed targets are declared; they are **advisory for reporting** unless a profile marks them mandatory—they **cannot** weaken HS07–HS12 and **cannot** reduce learning below **LearningFirstProfile** minima.

Out of scope for V2 (deferred to V3):
- Atomic-step execution loop with per-step review artifacts (V3).
- Large-repo batching, resume across thousands of files, and production verification bundle as first-class completion (V3).
- Automatic production gate claim and autonomous release promotion (same as V1).

## Relationship to V1

V2 **inherits** all of [docs/coding-agent/execution.md](../coding-agent/execution.md):
- Per-run artifacts under `outputs/runs/<run-id>/` (`summary.json`, `traces.jsonl`, `orchestration.jsonl`, `review.json`, `token_context.json`, `outputs/`, `report.md`).
- Strict balanced gates (Reliability, Delivery, Governance, composite) and HS01–HS06.

V2 **adds** program-level artifacts, hard-stops HS07–HS12, and execution profiles documented below. For V2-class runs, `summary.json` → `balanced_gates.hard_stops` **must** list HS01–HS12 each with `id`, `passed`, and optional `evidence_ref`.

## Primary End-User Journey (Phases V2 Owns)

These phases run **before** the V3 atomic implementation loop. Gates apply throughout.

| Order | Phase | Outcome |
|-------|--------|---------|
| 1 | **Program discovery** | Constraints, stack, non-goals, repo map; optional feature references from other projects with license notes. **Emit ≥1 `learning_events.jsonl` record** (`type: episode`) summarizing initial hypotheses and unknowns. |
| 2 | **External research** | Competitive scan, patterns, pitfalls; evidence links. **Emit ≥1 learning record** (`type: episode` or `synthesis`) linking findings to discovery. |
| 3 | **Differentiation** | `differentiation.md`: why this product wins; claims cite `research_digest.md` or external refs. **Emit learning record** capturing rejected alternatives and risks. |
| 4 | **Learning synthesis (research)** | Optional but recommended: `learning_synthesis.md` consolidates episodes into actionable principles for questions and docs. |
| 5 | **Question burst** | `question_workbook.jsonl` complete per policy; no open `status: open` without deferral or override. **Learning records** when questions reveal new constraints (`type: episode`). |
| 6 | **In-repo documentation** | Doc pack files written under target repo; manifest updated. |
| 7 | **Documentation review** | `doc_review.json` records `passed: true` or fail-closed reasons. **Emit ≥1 learning record** on pass or fail (what to fix next time). |
| 8 | **Learning synthesis (docs)** | If doc review ran: append or refresh `learning_synthesis.md` with doc-quality learnings. |
| 9 | **Phased plan lock** | `project_plan.json` versioned; subsequent changes only via **plan_amendment** events in traces, each with optional `learning_event_id` link. |

## Path Conventions

### Target repository (working copy)

| Path | Purpose |
|------|---------|
| `.agent/sde/discovery.json` | Program discovery payload (constraints, goals, non-goals, external links). |
| `.agent/sde/research_digest.md` | Structured competitive / pattern research. |
| `.agent/sde/differentiation.md` | Differentiation thesis with evidence pointers. |
| `.agent/sde/question_workbook.jsonl` | One JSON object per line: `id`, `category`, `text`, `status` (`open` \| `resolved` \| `deferred` \| `overridden`), `resolution_ref`, optional `risk_notes`. |
| `.agent/sde/doc_pack_manifest.json` | List of doc paths (under `docs/` and/or `.agent/sde/docs/`), `content_sha256`, `review_status` (`pending` \| `passed` \| `failed`). |
| `.agent/sde/project_plan.json` | Phases, `steps[]` with `step_id`, `depends_on`, `phase`, `rollback_hint`, `implementation_allowed` (boolean). |
| `.agent/sde/progress.json` | High-level progress for multi-session continuity (optional until first implementation). |
| `.agent/sde/learning_events.jsonl` | **Primary** append-only learning log (see Self-learning); required minimum volume per **LearningFirstProfile**. |
| `.agent/sde/learning_synthesis.md` | Optional consolidated learnings after research and after doc review. |
| `.agent/sde/playbook_delta.jsonl` | Optional append-only deltas (text/structured hints only); promotion to “team playbook” is out of scope (human or V6+). |
| `docs/` (recommended) | Human-facing product brief, architecture, API sketches—**paths must appear** in `doc_pack_manifest.json`. |

### Run directory mirror (audit)

Under `outputs/runs/<run-id>/` the runtime **must** retain or symlink copies:

| Path | Purpose |
|------|---------|
| `program/discovery.json` | Mirror or hash-attested copy of `.agent/sde/discovery.json` at gate time. |
| `program/doc_pack_manifest.json` | Mirror at doc-review gate. |
| `program/project_plan.json` | Mirror at plan lock. |
| `program/question_workbook.jsonl` | Snapshot at question-policy gate. |
| `program/doc_review.json` | Result of documentation review gate. |
| `program/learning_events.jsonl` | Snapshot or hash attestation of `.agent/sde/learning_events.jsonl` at plan lock (required for `learning_first`). |

## End-User Features (Minimum 3)

Each feature lists **user-visible outcome**, **artifacts**, **CTO gate evidence**.

### Feature 1 — Pre-implementation question gate

- **Outcome:** The user is not surprised by wrong stack or missing auth; the agent asks structured questions and blocks coding until policy is satisfied.
- **Artifacts:** `.agent/sde/question_workbook.jsonl`; `outputs/runs/<run-id>/program/question_workbook.jsonl` snapshot; `traces.jsonl` stage `question_policy_gate`.
- **Evidence:** Delivery + Governance via `review.json` `gate_snapshot`; HS07 is violated if implementation starts before the question policy gate passes.

### Feature 2 — In-repo living doc pack + manifest

- **Outcome:** The repo the user ships contains product/architecture/test-plan docs the agent wrote, not only chat logs.
- **Artifacts:** Files under `docs/` and/or `.agent/sde/docs/`; `.agent/sde/doc_pack_manifest.json` with hashes.
- **Evidence:** Delivery via `artifact_manifest` and on-disk listing; `orchestration.jsonl` emits `doc_pack_written`.

### Feature 3 — Documentation review before code

- **Outcome:** A dedicated review pass catches inconsistency or security gaps in docs before expensive implementation.
- **Artifacts:** `.agent/sde/doc_review.json` fields: `schema_version`, `passed` (boolean), `findings[]`, `reviewed_at`, `reviewer_role`; mirror `outputs/runs/<run-id>/program/doc_review.json`.
- **Evidence:** Governance + Delivery; HS08 if `passed` is not true before first `implementation` stage in `traces.jsonl`.

### Feature 4 — Learning-first traceability (episodes + synthesis)

- **Outcome:** The system visibly **gets smarter within the V2 window**: each phase contributes structured lessons; the next question or doc revision can cite prior `event_id`s.
- **Artifacts:** `.agent/sde/learning_events.jsonl` (required minima per profile); optional `learning_synthesis.md`, `playbook_delta.jsonl`; `traces.jsonl` may include `learning_capture` stages.
- **Evidence:** Delivery + Governance; **HS10** if lines are invalid or over cap; Reliability if required learning minima are missing when `run_profile: learning_first` (see Acceptance Criteria).

### Feature 5 (bonus) — Plan lock with traced amendments

- **Outcome:** Phases and dependencies stay authoritative; scope creep is visible in the audit trail; amendments may cite **learning**.
- **Artifacts:** `.agent/sde/project_plan.json` with `plan_version`; `traces.jsonl` entries `plan_amendment` with `from_version`, `to_version`, `rationale_id`, optional `learning_event_id`.
- **Evidence:** Reliability + Replay; HS09 on silent plan drift.

## Strict Balanced Gate Model (V2)

Same thresholds as V1 unless a stricter org profile overrides:

- Reliability ≥ 85, Delivery ≥ 85, Governance ≥ 85, composite ≥ 90.
- All hard-stops HS01–HS12 must pass for V2 validation-ready posture.

## Hard-Stop Gates (V2 Extensions)

Any single violation blocks V2 readiness. HS01–HS06 definitions match [docs/coding-agent/execution.md](../coding-agent/execution.md).

| ID | Condition | Detection |
|----|-----------|-----------|
| HS07 | Substantive **implementation** before question policy complete | `traces.jsonl` shows `implementation` or code-write stages while `question_workbook.jsonl` has `open` items without adjacent `deferral_accepted` or `human_override` trace, or missing `question_policy_gate` pass |
| HS08 | Implementation before **documentation review** pass | `doc_review.json` absent or `passed != true` before first implementation trace |
| HS09 | **Plan amendment** without trace | `project_plan.json` `plan_version` increments without matching `plan_amendment` event in `traces.jsonl` / `orchestration.jsonl` |
| HS10 | **Learning** write invalid or over budget | `learning_events.jsonl` line fails schema OR run exceeds configured max bytes/lines for file OR **required learning minima** for `run_profile: learning_first` not met (see LearningFirstProfile) |
| HS11 | Missing **discovery** or **project_plan** when entering implementation prep | Required files absent at gate boundary recorded in `review.json` |
| HS12 | **Doc pack manifest** mismatch | Listed path missing on disk OR `content_sha256` mismatch vs file contents at review time |

## Functional Requirements (V2)

1. **Discovery:** Populate `discovery.json` with stack constraints, deploy intent, data classification, and explicit non-goals.
2. **Research:** `research_digest.md` must cite at least three external or corpus sources OR state "no external sources used" with rationale.
3. **Differentiation:** `differentiation.md` must link claims to research sections or discovery fields.
4. **Question policy:** Minimum categories covered: stack, auth/session, data model, API surface, UX critical path, observability, deployment target, SLOs. Completeness machine-checkable from workbook metadata.
5. **Doc pack:** Minimum recommended files (adjust to product): `docs/product-brief.md`, `docs/architecture.md`, `docs/test-plan.md`; all listed in manifest with hashes.
6. **Doc review:** Automated + optional human sign-off; failures produce `required_fixes` in `review.json`.
7. **Plan lock:** `project_plan.json` lists phases; each phase lists atomic `step_id` entries (execution deferred to V3) with `implementation_allowed` flags.
8. **Self-learning (priority planning workstream, inside V1 envelope):** Structured events are **mandatory** under LearningFirstProfile minima; synthesis and playbook deltas are optional. No automatic **policy** promotion without human or gated workflow (V6+); learning **content** may feed questions and docs freely within safety bounds ([action-plan.md](../onboarding/action-plan.md) §2).

## How planning and learning work in practice (concrete flow)

This section describes **how** V2 drives the planning stage before code is written, and how learning feeds back **within** a run. See [action-plan.md](../onboarding/action-plan.md) §2 Stage 1.

### The planning pipeline

```
User prompt arrives at orchestrator
  → Planner agent (junior role) produces:
      1. discovery.json — constraints, stack, non-goals
         Learning event: "hypothesis: X; unknown: Y"
      2. research_digest.md — competitive scan, patterns
         Learning event: "rejected alternative A because B"
      3. question_workbook.jsonl — unknowns surfaced
         Learning event: "question Q revealed constraint C"
      4. Doc files (product brief, architecture, test plan)
      5. doc_pack_manifest.json with content hashes

  → Reviewer agent (separate call) evaluates doc pack:
      doc_review.json: passed or failed with required_fixes
      Learning event: "review found gap X; lesson: Y"

      If failed: Planner revises, resubmits (max 3 retries)
      If still failing: blocked_human

  → On pass: project_plan.json locked
      Phases, step_ids, depends_on, rollback_hints
      Learning event: "plan structure decision: Z because W"
```

### How learning feeds back within the same run

```
learning_events.jsonl accumulates throughout planning.
When the build loop (V3) begins:

  For each step, the Implementor receives:
    - step scope from project_plan.json
    - relevant learning_events (filtered by phase/topic)

  Example: step is "implement auth middleware"
    Learning event from planning: "rejected session-based auth
    because stateless JWT aligns better with API-first architecture"
    → Implementor receives this context → avoids the rejected path

  After each step review:
    Learning event: "step N review finding: missed edge case X"
    → Available to subsequent steps in the same lane
```

**Motivated learning:** The system **must** spend tokens on learning capture. This is not optional overhead — it is the mechanism by which run N+1 avoids run N's mistakes. But it operates **inside** V1 token budgets (HS06), never above them.

## Self-Learning (Bounded; first among planning activities when safe)

- Append-only `learning_events.jsonl`; each line: `event_id`, `type` (`episode` \| `synthesis` \| `playbook_hint`), `refs` (trace line or path), `created_at`, optional `phase`, no executable payload.
- **LearningFirstProfile minima (default for V2-class runs when `run_profile` is unset or `learning_first`):** at least **8** valid lines in `learning_events.jsonl` by plan lock, with **≥1** line after discovery, **≥1** after research/differentiation, **≥1** after question policy gate, **≥1** after doc review (pass or fail). Fewer lines **fails HS10** when profile is `learning_first`.
- Max size per run configurable; default **512 KiB** total append for `learning_events.jsonl` per run window (reflects motivated learning within token budgets—**subordinate** to V1 HS03/HS06); `playbook_delta.jsonl` shares the same cap unless split in config.
- Learning **never** bypasses HS04 or token/context integrity (HS03, HS06).

## External research alignment (self-learning and refinement)

Structured learning in this spec aligns with **in-context iterative refinement** and **principle-guided critique** from the literature, without implying unconstrained weight updates.

- **Self-Refine** ([arXiv:2303.17651](https://arxiv.org/abs/2303.17651)): treat `learning_synthesis.md`, doc iterations, and question workbook updates as **feedback → revise** loops; persist both draft and critique in `learning_events.jsonl`.
- **Constitutional AI / RLAIF** ([arXiv:2212.08073](https://arxiv.org/abs/2212.08073), [Anthropic PDF](https://www-cdn.anthropic.com/7512771452629584566b6303311496c262da1006/Anthropic_ConstitutionalAI_v2.pdf)): encode product and CTO rules as **explicit checklists** used during doc review and synthesis—not ad hoc model preferences.
- **EVOLVE** ([arXiv:2502.05605](https://arxiv.org/abs/2502.05605)): if future work adds **adapter or SFT** tied to planning quality, co-design **training** with the same **evaluation** used at inference (see [research doc](../research/self-improvement-research-alignment.md) §2.1–§2.2).

Full bibliography, technique notes, and spec mapping: [docs/research/self-improvement-research-alignment.md](../research/self-improvement-research-alignment.md).

## Optional Performance Budget (V2)

If present in `summary.json`:

```json
"performance_budget": {
  "declared_profile": "none | advisory | strict",
  "wall_clock_ms_ceiling": null,
  "notes": "strict must not override hard-stops"
}
```

- `advisory`: reporting only.
- `strict`: may fail run if ceiling exceeded **after** all mandatory gates and **LearningFirstProfile** learning minima are satisfied; must not skip HS07–HS12 or reduce learning below profile minima.

## Execution Profiles (V2)

1. **LearningFirstProfile (default)** — Same artifact gates as full V2; **enforces** learning minima in Self-learning section and optional `learning_synthesis.md` after research and doc review when `run_class` includes `full_v2`.
2. **DiscoveryProfile** — Run ends after discovery + research + differentiation artifacts present; no implementation traces; still requires **≥3** learning lines (discovery, research, differentiation).
3. **QuestionGateProfile** — Ends after question policy satisfied; includes negative test: implementation attempt must be rejected in trace; learning line after question gate required.
4. **DocReviewGateProfile** — Full doc pack + failing doc review blocks; passing doc review unlocks (V3 continues); learning line after doc review required.

## Validation Matrix (Gates to Evidence)

| Gate theme | Primary evidence | Supporting evidence |
|------------|------------------|---------------------|
| Reliability | `traces.jsonl`, `orchestration.jsonl` | `summary.json` |
| Delivery | `doc_pack_manifest.json`, `doc_review.json`, `review.json` | `outputs/` program mirror |
| Governance | `question_workbook.jsonl`, `review.json` `gate_snapshot` | `token_context.json` |
| Replay/auditability | `plan_amendment` events, monotonic `plan_version` | `orchestration.jsonl` |
| Question / doc hard-stops | HS07, HS08, HS12 in `balanced_gates.hard_stops` | `program/` mirror |
| Self-learning | `learning_events.jsonl`, optional `learning_synthesis.md` | HS10, `traces.jsonl` `learning_capture` |

## Acceptance Criteria

V2 is accepted when:

1. All V1 per-run artifacts and HS01–HS06 remain satisfied for V2-class runs.
2. HS07–HS12 are emitted in `balanced_gates.hard_stops` and pass for validation-ready claims.
3. At least one **DocReviewGateProfile** run demonstrates fail-closed behavior when `doc_review.json` would fail.
4. `question_workbook.jsonl` policy is machine-checkable and enforced in traces.
5. **End-user features (minimum 3)** section above remains satisfied with live artifact paths in CI or local proof runs.
6. At least one **LearningFirstProfile** run demonstrates **HS10** when learning minima are intentionally not met.

## Definition of Done for This V2 Doc

- V2 phases are unambiguous relative to V1 and V3.
- Artifacts, hard-stops HS07–HS12, and validation matrix are testable strings, not placeholders.
- Priority order states **self-learning first**, then the non-bypassable safety floor, then planning quality, then speed; performance budget rules reflect this.
- Linked from [README.md](../../README.md) and [docs/README.md](../README.md).
