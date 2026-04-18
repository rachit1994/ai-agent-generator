# SDE self-assessment and implementation loop

**In plain words:** this page is for **humans or agents** who need to (1) understand whether SDE can **own a whole project**, (2) **measure how much is left**, and (3) **implement in slices** while **re-checking** remaining work after each slice. It ties together docs that already exist in this repo; it does not invent new product promises.

---

## 1. Can SDE “create the whole project” today?

**Yes, with boundaries — it is a driver, not a magic oracle.**

| Capability | Shipped in this repo? | Notes |
|------------|----------------------|--------|
| Multi-step execution from a **real** `project_plan.json` | **Yes** | `sde project run` / `sde continuous --project-plan` (see [project-driver.md](project-driver.md)). Steps have `depends_on`, `path_scope`, optional per-step **shell** `verification.commands`. |
| Bounded context per step (ContextPack) + optional repo index | **Yes** | Session `context_packs/<step_id>.json`, lineage JSONL. |
| Honest terminal state + CI-oriented `stop_report.json` | **Yes** | `driver_state.json`, session `definition_of_done.json` vs per-run `validation_ready`. |
| Workspace contract (branch, path prefixes, leases, worktrees) | **Partial / opt-in** | Documented in project-driver; parallel lanes are **sequential on one checkout** unless `--parallel-worktrees` and git + disjoint scopes apply. |
| Auto-generate a **full** product plan + doc review + separate reviewer LLM per step (action-plan Stages 1–3 as written) | **No** | [action-plan.md](../onboarding/action-plan.md) is **north star**; the **“Shipped slice (local CLI)”** callouts describe what is actually wired. You (or an outer agent) still author or refine `project_plan.json`. |
| Machine “% of entire vision done” | **Approximate only** | `sde roadmap-review` asks the **support model** (default Gemma) for structured JSON (`overall_pct`, `remaining`, …). Treat as **guided triage**, not proof. **Ground truth** for the **tool** is [core-features-and-upstream-parity.md](core-features-and-upstream-parity.md) + [implementation-contract.md](implementation-contract.md) + tests. |

**Bottom line:** SDE can **execute** a whole project **end to end** once the work is expressed as a valid plan + verification commands. It does **not** replace human or agent **product decomposition** unless you build that loop yourself on top of these primitives.

---

## 2. What to read first (minimum doc set)

Read in this order before claiming “done” or “X% left”:

1. [what.md](what.md) — CLI commands, what is in vs out of scope for the **local** SDE.
2. [project-driver.md](project-driver.md) — session layout, **gap inventory** paragraph at the top (Categories 1–5, Phases 1–21).
3. [implementation-contract.md](implementation-contract.md) — artifact checklist for a baseline run.
4. [core-features-and-upstream-parity.md](core-features-and-upstream-parity.md) — **implemented** table vs suggested gaps.
5. [../onboarding/action-plan.md](../onboarding/action-plan.md) — full-stack **story**; use **“Shipped slice”** notes to separate vision from code.

For a **project session** you are driving from disk:

6. `sde project validate` — plan + cycle + workspace preflight (see what.md / project-driver).
7. `sde project status` — JSON snapshot; use `status_at_a_glance` + `red_flags` for a quick health read (Phase 21).

---

## 3. How to measure “how much is left” (use more than one signal)

| Signal | Command / location | Strength | Weakness |
|--------|---------------------|----------|----------|
| **Roadmap % + narrative** | `sde roadmap-review` (optional `--context-file`, `--repo-root`) | Fast orientation; surfaces `remaining` text | Model output; must parse JSON; not a contract |
| **Feature contract** | [core-features-and-upstream-parity.md](core-features-and-upstream-parity.md) “Gap / next step” rows | Stable, human-reviewed | Coarse; not line-level |
| **Project-driver phases** | First paragraph of [project-driver.md](project-driver.md) | Exact for **meta-orchestrator** slices | Does not list every V1–V7 coding-agent detail |
| **Session health** | `sde project status --plan …` (or `--session-dir`) | `plan_ok`, `red_flags`, rollups, DoD embed | Only applies when using a **session directory** |
| **Proof of behavior** | `uv run pytest …`, `sde validate --run-id …` | Objective | Scoped to what tests / runs cover |

**Rule:** After every implementation slice, **re-run at least one objective check** (tests, `project validate`, or `project status` on a fixture session) **and** refresh roadmap-review if you rely on `%` for planning.

---

## 4. Implementation loop (for an SDE-style agent)

Use this loop literally; do not skip the re-measure step.

1. **Baseline** — Run `sde roadmap-review` (and/or re-read core-features + project-driver gap paragraph). Write down: *current claim of %, listed `remaining`, and which rows in core-features still say “gap”.*
2. **Pick one slice** — One PR-sized change with a clear acceptance test (prefer a failing test first if adding behavior).
3. **Implement** — Minimal diff; match existing patterns in `src/orchestrator/` and `src/sde_pipeline/`.
4. **Verify** — `uv run pytest` on affected packages; fix failures.
5. **Re-measure** — Run `sde roadmap-review` again **or** update a short human note listing what gap rows are **still** open. Compare to step 1; if nothing moved, you picked the wrong slice or the metric is stale.
6. **Repeat** — Optional: `sde evolve` for a **bounded** cadence (round cap, target %); it still does not guarantee full vision completion (see [what.md](what.md)).

For **closing a project session** (not the whole V1–V7 spec):

- Ensure `sde project validate` is clean (or exit codes understood).
- Run `sde project run` / `continuous` until `stop_report.json` / `driver_state.json` reflect the intended terminal state, or fix plan and re-run.
- Use `sde project status` and `status_at_a_glance.red_flags` before declaring the session green.

---

## 5. Paste-ready brief (give this block to another agent)

```text
You are working inside the coding-agent / SDE repo. Ground truth for “what exists” is docs/sde/core-features-and-upstream-parity.md and docs/sde/implementation-contract.md — not your memory.

Task:
1. Read docs/sde/what.md, docs/sde/project-driver.md (first paragraph = gap inventory), docs/onboarding/action-plan.md (note “Shipped slice” vs vision).
2. Run: sde roadmap-review --repo-root .   (requires Ollama/support model as configured)
3. List concrete “remaining” items: cite doc section OR file/CLI gap, not vague percentages alone.
4. Pick the smallest shippable slice; implement with tests; run uv run pytest on touched areas.
5. Re-run sde roadmap-review OR explicitly reconcile docs/sde/core-features-and-upstream-parity.md “Gap” column — state what is STILL open after your change.

Do not claim “whole project complete” unless project_plan-driven session + verification + DoD match the user’s product scope; distinguish repo tool completeness from user app completeness.
```

---

## Related commands (quick reference)

- `sde roadmap-review` — structured “% / remaining” (support model).
- `sde evolve` — bounded rounds: roadmap-review + optional fixed task ([what.md](what.md)).
- `sde project validate` / `sde project status` / `sde project run` / `sde continuous --project-plan` — session meta-orchestrator ([project-driver.md](project-driver.md)).
