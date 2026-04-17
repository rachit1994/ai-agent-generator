# Coding-Agent V3 Specification

## Goal

Extend V2 so SDE can **execute through completion** of a large full-stack codebase: **atomic steps** with **per-step review**, **run-to-completion** semantics (monotonic progress, resume, bounded budgets), **multi-thousand-file scale** via batching and manifests, and **production verification** evidence—all while inheriting V1 runtime contracts, V1+V2 strict balanced CTO gates, hard-stops HS01–HS12, and adding **HS13–HS16**.

**Priority order (non-negotiable):** **quality** and **completion** (meeting `definition_of_done` and passing CTO hard-stops) **outrank** wall-clock speed. Batching and parallelism exist to make completion **feasible**, not to skip reviews or verification.

## External research alignment (verification and solver–verifier loops)

- **Learning to Solve and Verify** / Sol-Ver-style pipelines ([arXiv:2502.14948](https://arxiv.org/abs/2502.14948)): treat **tests and linters** in `verification_bundle.json` as the **verifier channel** for code evolution; co-generate or harden tests alongside implementation when the plan allows.
- **ReST^EM** ([arXiv:2312.06585](https://arxiv.org/abs/2312.06585)): binary **correctness** filters (e.g. test pass) define which trajectories may enter any future **self-training** dataset—never train on failing traces without explicit “negative example” policy.
- **Mind the Gap** ([OpenReview ICLR 2025](https://openreview.net/pdf?id=mtJSMcF3ek)): before claiming completion, measure **verifier vs generator** strength on **holdout** tasks; if the gap is large, keep **human or tool verifier** in the loop for that slice.
- **DSVD** ([arXiv:2503.03149](https://arxiv.org/abs/2503.03149)): optional decoding-time **self-verify** for high-risk single-shot outputs before they touch `outputs/` or the main branch.

Bibliography and cross-links: [docs/research/self-improvement-research-alignment.md](../research/self-improvement-research-alignment.md).

## V3 Scope

In scope:
- **Implementor contract:** orchestrator issues **one atomic `step_id` at a time**; implementor produces artifacts; **per-step review** before advancing `step_id`.
- **Per-step review artifacts:** `step_reviews/<step_id>.json` under run dir and mirror rules under `.agent/sde/step_reviews/` (or run-only if policy forbids dot-dir writes—must be fixed in `project_plan.json`).
- **Work manifest:** bounded batches of paths (`work_batch.json`) for large repos; idempotent re-runs.
- **Resume / checkpoint:** crash-safe continuation using `progress.json` + `last_completed_step_id` + manifest hashes.
- **Production verification bundle:** tests, lint, typecheck (as applicable to stack) with captured stdout/stderr or report paths referenced from `review.json` / `verification_bundle.json`.
- **`definition_of_done`:** explicit checklist object; terminal states are honest (no fake pass).
- **Hard-stops HS13–HS16** (below).

Out of scope for V3:
- Cross-machine distributed scheduler (same as V1).
- Autonomous release promotion without human approval.
- Unbounded agent self-modification of policies (learning promotion remains gated per V2).

## Relationship to V1 and V2

V3 **requires** V2 artifacts to be valid **before** the first atomic implementation step for a greenfield “one go” program:

- `doc_review.json` with `passed: true`.
- `project_plan.json` with `plan_version` and atomic `steps[]`.
- `question_workbook.jsonl` policy satisfied (HS07 clear).

V3 **inherits** [docs/coding-agent/execution.md](../coding-agent/execution.md) per-run layout and [docs/coding-agent/planning.md](../coding-agent/planning.md) program paths.

For V3-class runs, `summary.json` → `balanced_gates.hard_stops` **must** list **HS01–HS16** each with `id`, `passed`, optional `evidence_ref`.

## Primary End-User Journey (Phases V3 Owns)

| Order | Phase | Outcome |
|-------|--------|---------|
| 8 | **Atomic implementation loop** | For each `step_id` in dependency order: implement → **step review** → mark progress or remediate. |
| 9 | **Batch integration** | Writes grouped in `work_batch.json` chunks; manifest updated; reruns skip completed hashes. |
| 10 | **Production verification** | After planned steps or on cadence: run test/lint/typecheck; store **verification_bundle.json**. |
| 11 | **Definition of Done** | `definition_of_done` checklist in `review.json` (or linked path) all satisfied **or** terminal `blocked_human` / `exhausted_budget`. |

## Path Conventions

### Run directory (`outputs/runs/<run-id>/`)

| Path | Purpose |
|------|---------|
| `program/work_batch.json` | Current batch: `batch_id`, `paths[]`, `max_paths`, `content_sha256` per path or aggregate hash. |
| `program/progress.json` | `last_completed_step_id`, `pending_step_id`, `plan_version`, `updated_at`. |
| `step_reviews/<step_id>.json` | Per-step review: `schema_version`, `step_id`, `passed`, `findings[]`, `evidence_refs[]`, `reviewed_at`. |
| `verification_bundle.json` | Commands run, exit codes, log paths, `passed` aggregate. |

### Target repository

| Path | Purpose |
|------|---------|
| `.agent/sde/progress.json` | Mirror of run progress for multi-session UX (optional but recommended). |
| `.agent/sde/step_reviews/<step_id>.json` | Optional mirror of per-step reviews. |

## End-User Features (Minimum 3)

### Feature 1 — Atomic step runner with mandatory per-step review

- **Outcome:** User gets traceable increments; no “big bang” merge without a review record per step.
- **Artifacts:** `step_reviews/<step_id>.json`; `traces.jsonl` entries `step_start`, `step_review_pass` / `step_review_fail`.
- **Evidence:** Delivery + Governance; HS13 if advancing `step_id` without adjacent passing step review for prior required step.

### Feature 2 — Production verification bundle

- **Outcome:** Before claiming completion, tests/lint/typecheck evidence exists (stack-dependent).
- **Artifacts:** `verification_bundle.json`; stderr/stdout logs under `outputs/runs/<run-id>/verification_logs/`.
- **Evidence:** Delivery; HS14 if `definition_of_done` requires verification but bundle missing or `passed: false`.

### Feature 3 — Run-to-completion with honest terminal states

- **Outcome:** Agent continues through phases until DoD satisfied or documented stop (budget, human block)—never silent stall as “pass”.
- **Artifacts:** `progress.json`; `review.json` with `status` in `completed_review_pass` \| `completed_review_fail` \| `incomplete` and optional `terminal_reason` (`dod_met` \| `blocked_human` \| `exhausted_budget` \| `remediation_required`).
- **Evidence:** Reliability + Governance; HS15 on contradictory terminal state vs traces.

### Feature 4 (bonus) — Large-repo batching and resume

- **Outcome:** Thousands of files are handled in bounded batches with idempotent resume.
- **Artifacts:** `work_batch.json` series; `orchestration.jsonl` `batch_committed` events; `progress.json` updated per batch.
- **Evidence:** Reliability; HS16 on manifest/hash mismatch after claimed batch complete.

## Implementor Contract

1. **Planner/orchestrator** selects the next `step_id` such that all `depends_on` are completed per `project_plan.json`.
2. **Implementor** executes only that step’s scope; writes code/docs/tests per plan.
3. **Reviewer** (role may be model or human) produces `step_reviews/<step_id>.json` with explicit `passed`.
4. If `passed: false`, orchestrator **does not** advance; it schedules remediation **for the same `step_id`** or opens a `plan_amendment` per V2 HS09.
5. Only after `passed: true` may `progress.json` advance `last_completed_step_id`.

## Strict Balanced Gate Model (V3)

Same category minimums as V1 (85/85/85, composite ≥ 90) for validation-ready unless org profile tightens (e.g. Governance ≥ 90 for regulated workloads)—if tightened, document in `project_plan.json` metadata.

## Hard-Stop Gates (V3 Extensions)

| ID | Condition | Detection |
|----|-----------|-----------|
| HS13 | **Step advanced** without **passing per-step review** for required predecessor | `progress.json` / traces show `step_complete` for step N when `step_reviews/<pred>.json` missing or `passed != true` where `depends_on` requires it |
| HS14 | **Definition of Done** requires verification but **verification_bundle** absent or failed | `definition_of_done.checks` includes `verification` true but `verification_bundle.json` missing or `passed: false` |
| HS15 | **Terminal state lie** | `review.json` `status` is `completed_review_pass` while traces show open `step_review_fail` or failing hard-stop |
| HS16 | **Work batch integrity** failure | Paths listed in `work_batch.json` committed state disagree with filesystem hash or `step_reviews` reference missing files |

## `definition_of_done` (in `review.json` or sibling)

Recommended embedded object `definition_of_done`:

| Field | Type | Description |
|-------|------|-------------|
| `schema_version` | string | e.g. `1.0` |
| `checks` | array | `{ "id", "description", "required", "passed", "evidence_ref" }` |
| `all_required_passed` | boolean | Derived consistency check |

Example required checks for full-stack default profile (adjust per `project_plan.json`):

- `docs_complete` — doc pack manifest satisfied (V2).
- `verification` — `verification_bundle.json` passed.
- `critical_path_tests` — e2e or smoke subset specified in plan.
- `security_smoke` — dependency audit or SAST slot if declared in plan.

## Production Verification Bundle

`verification_bundle.json` fields:

| Field | Type | Description |
|-------|------|-------------|
| `schema_version` | string | Contract version |
| `run_id` | string | Matches run directory |
| `commands` | array | `{ "cmd", "cwd", "exit_code", "log_path" }` |
| `passed` | boolean | All required commands exit 0 (or plan-specific success criteria) |
| `captured_at` | string | ISO-8601 |

## Execution Profiles (V3)

1. **AtomicStepProfile** — Small plan (≤ 5 steps); every step has `step_reviews/<step_id>.json`; negative test: skip review → HS13.
2. **LargeRepoBatchProfile** — Synthetic or fixture with > N files; multiple `work_batch.json`; resume mid-run; HS16 checks.
3. **CompletionProfile** — Full DoD with verification; must end `completed_review_pass` or honest `blocked_human` / `exhausted_budget` with reasons.

## Validation Matrix (Gates to Evidence)

| Gate theme | Primary evidence | Supporting evidence |
|------------|------------------|---------------------|
| Reliability | `progress.json`, batch events, resume traces | `orchestration.jsonl` |
| Delivery | `step_reviews/`, `verification_bundle.json`, `definition_of_done` | `review.json` |
| Governance | HS13–HS16 in `balanced_gates.hard_stops`, no HS15 | `traces.jsonl` |
| Replay/auditability | Monotonic `step_id` completion order | `step_reviews/`, `traces.jsonl` |

## Acceptance Criteria

V3 is accepted when:

1. V1 and V2 prerequisites and HS01–HS12 satisfied for V3-class “one go” runs.
2. HS13–HS16 emitted and passing for validation-ready claims.
3. **AtomicStepProfile**, **LargeRepoBatchProfile**, and **CompletionProfile** demonstrable with artifact-backed evidence.
4. Terminal honesty: no `completed_review_pass` without DoD checks and verification policy satisfied.
5. **End-user features (minimum 3)** in this doc remain satisfied in proof runs.

## Definition of Done for This V3 Doc

- Implementor contract and per-step review paths are unambiguous.
- HS13–HS16, `definition_of_done`, and `verification_bundle.json` are fully specified.
- Completion vs speed priority is explicit; V3 stays aligned with V2’s **non-bypassable** gates while V2 additionally treats **structured self-learning** as the primary upstream product priority.
- Linked from [README.md](../../README.md) and [docs/README.md](../README.md).
