# SDE action plan — how the system delivers a full-stack app

This is the **operational blueprint** for how one SDE instance replaces a solo developer (you) in building a **production-quality full-stack application**. Agents are **junior engineers**; company processes (reviews, gates, leases, learning) ensure mistakes are caught early and lessons compound across the run.

Every mechanism described here operates **under CTO gates** ([execution.md](../coding-agent/execution.md) HS01–HS06). No section below may weaken those gates for speed or learning volume.

---

## 1. Product goal

**Input:** A product-level prompt — for example *"Build a SaaS invoicing app: Next.js frontend, Express API, Postgres, Stripe billing, auth, CI, deploy script."*

**Output:** A working codebase in the target repository with:
- all planned features implemented and reviewed,
- tests passing (`verification_bundle.json`),
- documentation (product brief, architecture, API, deploy runbook),
- every change traceable to a plan step and a review record,
- honest terminal state (`completed_review_pass` or `blocked_human` with reasons).

**Definition of "done":** The SDE does not stop until the `definition_of_done` checklist ([completion.md](../coding-agent/completion.md)) is fully green **or** a hard block is surfaced (budget exhaustion, human decision required, safety veto). Silent stalls are a hard-stop violation (HS15).

---

## 2. How the system works — end to end

Below is the concrete flow from prompt to shipped product. Each numbered stage maps to a version spec; CTO gates run **continuously**, not only at the end.

### Stage 1 — Intake and decomposition (V2 planning)

```
User prompt
  → Discovery: constraints, stack, non-goals, repo scan
  → Research: competitive scan, patterns, risks
  → Question burst: unknowns surfaced, resolved or deferred
  → Doc pack: product brief, architecture, test plan written to target repo
  → Doc review gate: pass or fail-closed (HS08)
  → Plan lock: project_plan.json with phases and atomic step_ids
```

**How it works concretely:**
1. The orchestrator receives the prompt and spawns a **Planner agent** (junior role: produces artifacts, cannot self-approve).
2. Planner writes `discovery.json`, `research_digest.md`, `question_workbook.jsonl`, doc files.
3. A **Reviewer agent** (separate LLM call with reviewer persona) evaluates the doc pack against checklists. Result → `doc_review.json`.
4. If review fails: Planner gets findings, revises, resubmits — bounded retries (max configured in run profile, default 3). If still failing → `blocked_human`.
5. On pass: `project_plan.json` is locked. Each `step_id` has `depends_on`, `phase`, `implementation_allowed`, and `rollback_hint`.

**Learning within this stage (V2):** Every discovery insight, rejected alternative, and question resolution emits a line to `learning_events.jsonl`. Minimum 8 events by plan lock (LearningFirstProfile). This is the "motivated self-learning" — the system **must** articulate what it learned, not just what it produced.

**CTO gates active:** HS01–HS12 checked continuously. Token budgets enforced per stage (HS06). No silent context truncation (HS03).

### Stage 2 — Parallel workstream spawning (V7 organization)

```
project_plan.json
  → Orchestrator decomposes plan into workstreams
  → Each workstream gets an agent lane with a lease
  → Lanes run in parallel with non-overlapping file ownership
```

**How it works concretely:**
1. Orchestrator reads `project_plan.json` and groups `step_id`s into **workstreams** by dependency graph: steps with no cross-dependencies can run in parallel lanes.
   - Example: `frontend/` steps, `api/` steps, `db/migrations` steps, `infra/` steps, `docs/` steps.
2. For each lane, orchestrator spawns an **Implementor agent** (junior role) with:
   - a **lease** on its file scope (e.g. `frontend/**`). No other agent may write to leased paths.
   - a **heartbeat** interval. If an agent stalls past heartbeat timeout, the lease expires and work is reassigned or blocked.
   - a **step queue** — the ordered `step_id`s for that lane.
3. Shared interfaces (API contracts between frontend and backend, DB schema used by API) are defined in the plan as **contract steps** that must complete before dependent lanes begin.
4. The number of parallel lanes is bounded by host resources (configurable `max_concurrent_agents`); excess lanes queue with priority by dependency depth.

**Lease conflict resolution:** If step N in lane A depends on step M in lane B, lane A blocks on M's completion. The orchestrator tracks this via `depends_on` and does not issue the step until the dependency's `step_review` passes.

### Stage 3 — Atomic build + review loop (V3 completion)

```
For each step_id in each lane:
  Implementor agent writes code/tests/docs for that step
  → Reviewer agent evaluates the diff
  → If pass: progress.json advances
  → If fail: Implementor gets findings, retries (bounded)
  → If still failing: lane blocks with remediation_required
```

**How it works concretely:**
1. Implementor receives `step_id` scope from `project_plan.json`, the current repo state, and any `learning_events` relevant to this step.
2. Implementor writes files to the leased scope. All writes go through the orchestrator so trace events are emitted.
3. **Reviewer agent** (separate persona, separate LLM call) produces `step_reviews/<step_id>.json`:
   - `passed: true/false`
   - `findings[]` — specific issues with file/line references
   - `evidence_refs[]` — what was checked
4. If `passed: false`: Implementor gets findings as input for a retry. Max retries per step configured (default 2). Each retry is a new trace event.
5. If all retries exhausted: step status → `remediation_required`. Orchestrator tries to continue other non-dependent steps. If the blocked step is on the critical path, the run surfaces `blocked_human` with the specific failure.
6. If `passed: true`: `progress.json.last_completed_step_id` advances. Next step issued.

**No big-bang merges:** Every step is reviewed before the next begins in that lane. The system never accumulates unreviewed work.

### Stage 4 — Verification (V3 completion)

```
After all steps complete (or on cadence):
  Run tests, linter, typecheck against target repo
  → verification_bundle.json with commands, exit codes, logs
  → If any critical command fails: loop back to Stage 3
```

**How it works concretely:**
1. Orchestrator assembles the verification commands from `project_plan.json` metadata (test runner, linter, typecheck, build).
2. Commands execute in the target repo. stdout/stderr captured to `verification_logs/`.
3. `verification_bundle.json` records each command's exit code and `passed` aggregate.
4. If `passed: false` and the plan has remaining budget:
   - Orchestrator identifies which step likely caused the failure (from error output + file mapping).
   - That step re-enters Stage 3 with the verification failure as input to the Implementor.
   - Re-review required after fix.
5. If `passed: true`: proceed to Definition of Done.

### Stage 5 — Definition of Done (V3 completion)

```
definition_of_done checklist:
  ☐ All plan steps reviewed and passed
  ☐ verification_bundle passed
  ☐ Doc pack manifest satisfied
  ☐ Critical-path smoke test passed (if declared)
  ☐ Security smoke (dependency audit) passed (if declared)
  → All checked: status = completed_review_pass
  → Any unchecked: status = completed_review_fail or blocked_human
```

Terminal honesty (HS15): the system **never** claims `completed_review_pass` while any required check is red or any hard-stop is violated.

### Stage 6 — Learning capture (V2 planning + V6 evolution)

**Within the run (V2):**
- Every significant decision, failure, retry, and reviewer finding emits to `learning_events.jsonl`.
- After verification: optional `learning_synthesis.md` consolidates what worked, what didn't, what to do differently.
- Playbook deltas (structured hints) may append to `.agent/sde/playbook_delta.jsonl`.

**Across runs (V6, when implemented):**
- Reflection bundles extract root causes from failures (HS25: causal closure).
- Practice loop: verified skill gaps generate targeted practice tasks (HS27).
- Canary: policy or prompt changes are shadow-tested before promotion (HS28).
- Promotion packages: stage progression requires independent evaluator signals (HS26).

**Self-learning is motivated, not optional:** The system allocates token budget to learning capture **before** optimizing for speed. But learning **never** bypasses HS01–HS06.

### Stage 7 — Event trail and replay (V4 events)

Every state change across Stages 1–6 emits an event to `traces.jsonl` / `orchestration.jsonl` / the platform event store (when V4 is active). This enables:
- **"Why did it do X?"** — trace any output back through step_id → plan → review → decision.
- **Replay** — reconstruct the run from events; fail closed on manifest mismatch (HS18).
- **Kill switch** — emergency stop is a first-class event with actor and reason (HS19).

### Stage 8 — Memory (V5, when implemented)

Across multiple runs, the system builds institutional memory:
- **Episodic:** "Last time we built a Next.js app, the auth middleware pattern caused issues" — retrieved before similar steps.
- **Semantic:** Generalized domain knowledge with provenance.
- **Skill:** What the agent is certified to do, with decay and recertification.
- **Quarantine:** Contradictory memories surface to review, not silently merge (HS22).

---

## 3. Agent roles — junior humans with company process

| Role | Who | What they can do | What they cannot do |
|------|-----|------------------|---------------------|
| **Planner** | LLM with planner persona | Write discovery, research, questions, docs, plan | Approve own docs (needs Reviewer) |
| **Implementor** | LLM with coder persona | Write code/tests/docs within leased scope | Write outside lease; skip review; advance progress |
| **Reviewer** | LLM with reviewer persona (separate call) | Approve/reject step reviews, doc reviews | Write implementation code; override safety veto |
| **Verifier** | Deterministic tool execution | Run tests, lint, typecheck; report pass/fail | Make judgment calls; skip hard-stops |
| **Orchestrator** | Python runtime (not LLM) | Schedule steps, manage leases, enforce gates, route failures | Override gate failures; fake pass status |

**Key constraint:** No agent self-approves. The Implementor cannot review its own work. The Planner cannot approve its own docs. This is the "company process" — separation of duties enforced by the orchestrator runtime, not by trust.

---

## 4. CTO gates — how they maintain quality without blocking speed

Gates are **continuous**, not a final checkpoint:

| When | What runs | Blocks on failure |
|------|-----------|-------------------|
| Every LLM call | Token budget check (HS06), context overflow check (HS03) | Call rejected; retry with smaller context |
| Every file write | Lease validation (HS29 when V7 active) | Write rejected |
| Every step completion | Per-step review required (HS13) | Step does not advance |
| Every stage boundary | Hard-stop sweep (HS01–HS06 minimum) | Stage does not advance |
| On verification | Tests/lint must pass for DoD (HS14) | Loop back to implementation |
| On run completion | Full balanced gate score (reliability ≥ 85, delivery ≥ 85, governance ≥ 85, composite ≥ 90) | Status cannot be `completed_review_pass` |

**Speed comes from parallelism, not from skipping gates.** Multiple lanes run simultaneously; each lane individually respects all gates. Total wall-clock time drops because work is concurrent, not because reviews are cut.

---

## 5. Global precedence (resolves all spec ordering conflicts)

This order is **binding** across all extension specs and docs:

1. **Safety and integrity (V1 / execution)** — HS01–HS06, token/context evidence, refusal paths.
2. **Production evidence (V3 completion)** — verification bundle, DoD, per-step review.
3. **Lineage and replay (V4 events)** — append-only, fail-closed replay.
4. **Governed memory (V5)** — provenance, quarantine.
5. **Policy-gated learning (V6)** — reflection, canary, promotion.
6. **Organization and IAM (V7)** — leases, roles, federation.
7. **Self-learning capture (V2 planning)** — maximized inside the envelope above.
8. **Wall-clock latency** — improved only after gates and learning minima are met.

---

## 6. Version ladder — one combined product

The V1–V7 labels are **staged capabilities**, not separate products. Together they answer: *how does one SDE instance deliver a full-stack app with company-grade process?*

| Version | Spec | Hard-stops | What it adds to the delivery flow |
|---------|------|------------|-----------------------------------|
| **V1** | [execution.md](../coding-agent/execution.md) | HS01–HS06 | **Trust base.** Auditable runs, token integrity, balanced gates. Without this nothing else is trustworthy. |
| **V2** | [planning.md](../coding-agent/planning.md) | HS07–HS12 | **Company planning.** Stages 1 + learning capture. The system plans before coding and records what it learns. |
| **V3** | [completion.md](../coding-agent/completion.md) | HS13–HS16 | **Build + prove.** Stages 3–5. Atomic step loop, verification, DoD. Features reach "done" with evidence. |
| **V4** | [events.md](../coding-agent/events.md) | HS17–HS20 | **Audit trail.** Stage 7. Every decision is replayable. |
| **V5** | [memory.md](../coding-agent/memory.md) | HS21–HS24 | **Institutional memory.** Stage 8. Cross-run knowledge with provenance. |
| **V6** | [evolution.md](../coding-agent/evolution.md) | HS25–HS28 | **Learning loop.** Stage 6 (cross-run). Reflection, practice, canary, promotion. |
| **V7** | [organization.md](../coding-agent/organization.md) | HS29–HS32 | **Many agents.** Stage 2. Parallel lanes, leases, IAM, coordination safety. |

**Implementation order:** V1 → V3 (need build loop before planning is useful at scale) → V2 → V4 → V7 (parallel agents) → V5 → V6. But **all** are required for the complete product story.

---

## 7. Phased implementation

### Phase 0 — Baseline (now)
- `sde run`, `sde benchmark`, `sde report` working with guarded pipeline.
- **Exit:** green tests, reference run validates.

### Phase 1 — V1 complete
- All execution artifacts, HS01–HS06, balanced gates implemented and tested.
- **Exit:** execution spec checklist + benchmarks green with stored run ids.

### Phase 2 — V3 completion loop
- Atomic steps, per-step review, verification bundle, DoD, run-to-completion.
- **Exit:** a multi-step task completes with all step reviews, verification green.

### Phase 3 — V2 planning
- Discovery → doc review → plan lock → learning_events pipeline.
- **Exit:** a full-stack-shaped program planned and documented before implementation.

### Phase 4 — V4 events
- Event envelopes, replay manifests, fail-closed replay.
- **Exit:** HS17–HS20 green on golden manifests.

### Phase 5 — V7 organization (parallel agents)
- Leases, heartbeats, IAM matrix, multi-lane orchestration.
- **Exit:** two+ lanes running concurrently with non-overlapping leases and independent reviews.

### Phase 6 — V5 memory
- Episodic/semantic/skill stores, quarantine, quality metrics.
- **Exit:** HS21–HS24 green, cross-run retrieval with provenance.

### Phase 7 — V6 evolution
- Reflection bundles, practice loop, canary, promotion packages.
- **Exit:** HS25–HS28 green under declared profiles.

---

## 8. Capability yardsticks (beyond hard-stop checklists)

Hard-stops are hygiene. These measure whether SDE actually **replaces you in coding:**

| Yardstick | What it proves | How to measure |
|-----------|---------------|----------------|
| **Held-out product tasks** | Can it build things it wasn't tuned for? | Reserve tasks from benchmarks; pass rate on unseen prompts |
| **Full-stack E2E** | Does the output actually work? | One run produces UI + API + DB + tests + deploy; smoke test passes |
| **Regression stability** | Does fixing X break Y? | CI suite; `CriticalRegressionCount == 0` |
| **Rollback drill** | Can it recover from failures? | Simulate gate failure; system rolls back and surfaces reason |
| **Time-to-green** | Is it fast enough to be useful? | Wall-clock from prompt to `completed_review_pass` on reference tasks |
| **Learning transfer** | Does run N+1 avoid run N's mistakes? | Compare `learning_events` from run N with decisions in run N+1 |

---

## 9. Honest scope boundary

- **This repo delivers:** the orchestrator, agent personas, gates, and process that make the §2 flow work.
- **Not in this repo:** specific infrastructure bindings (Postgres, OTel, cloud deploy) unless pinned in `local-prod` profile.
- **Tier 2.1** (all V1–V7 implemented with evidence) = the complete product story.
- **Tier 2.2** (every named master-doc service deployed) = separate ops program.

---

## 10. Changelog

- **2026-04-18 (v2):** Complete rewrite: concrete end-to-end flow (§2), agent roles (§3), continuous gate model (§4), implementation order adjusted (V3 before V2), capability yardsticks (§8).
- **2026-04-18 (v1):** Initial action plan.
