# Documentation index

**In plain words:** This folder is the **rulebook** for the project. The code under `src/` tries to follow these rules. When a sentence sounds formal, it usually means “here is what must be true so we can trust runs, reviews, and logs.” **HS01, HS02, …** are numbered **hard-stops**: checks that must pass (or the run is not allowed to pretend it succeeded).

**How to read this (humans or LLMs):**

1. If you are **new**, start in **[`onboarding/`](onboarding/)** — short guides and the **[action plan](onboarding/action-plan.md)** (what we want and how work is supposed to flow).
2. If you are **implementing or reviewing code**, read **[`sde/what.md`](sde/what.md)** and **[`coding-agent/execution.md`](coding-agent/execution.md)** next — they describe what a “good run” looks like on disk.
3. If you are **mapping big-picture vision to this repo**, use **[`architecture/`](architecture/)** — especially **[architecture-goal-completion](architecture/architecture-goal-completion.md)** (what “done” means here vs in the huge master doc).
4. Use this **index** as a map; follow links in order when a doc tells you to.

---

## Where everything lives

| Folder | In everyday terms |
|--------|-------------------|
| **[`onboarding/`](onboarding/)** | **Front door for readers:** gentle doc/code guides, engineer walkthrough, and the **story + phases** of delivery ([action plan](onboarding/action-plan.md)). |
| **[`architecture/`](architecture/)** | **Big blueprint and “are we finished yet?”** — long master architecture, shorter “completion” explainer, dream folder layout, token/budget math. |
| **[`coding-agent/`](coding-agent/)** | **Staged product specs (V1–V7):** each file adds rules for safer, more complete automation (runs → planning → shipping → events → memory → learning → many agents). |
| **[`sde/`](sde/)** | **What the local tool (`sde`) does today:** commands, checklists, contracts, prompts, pipeline order. |
| **[`research/`](research/)** | **Outside papers** tied back to our specs — ideas for learning and quality, **not** permission to skip safety rules. |

---

## New here? Pick one path

| Audience | Start here |
|----------|------------|
| **Easy entry — documentation** | **[start-here-reading-the-docs.md](onboarding/start-here-reading-the-docs.md)** — glossary, why the project exists, what V1–V7 mean, simple reading order |
| **Easy entry — code** | **[start-here-reading-the-code.md](onboarding/start-here-reading-the-code.md)** — folder map, which files to open first, what is built vs still on paper |
| **Engineer onboarding** | **[Developer walkthrough](onboarding/developer-walkthrough.md)** — repo map, CLI flow, first-day checklist |

## New to the codebase?

Start with **[Developer walkthrough](onboarding/developer-walkthrough.md)** — what to open first, where Python and tests live, how runs land under **`outputs/`**, and a simple first-day checklist.

**Product + delivery plan:** **[Action plan](onboarding/action-plan.md)** — what “good” looks like for a **real app** (not a one-off demo), why **safety and run quality (V1) come before** speed and learning tricks, and how **V1–V7** are **one roadmap** built in slices.

---

## Extension map (single canonical tree)

All **coding-agent** specs live as **flat files** under **`docs/coding-agent/`** (we do not mirror versions in extra folders). **V1–V7** are **labels for slices of the same product**, not seven separate products — see [action-plan.md](onboarding/action-plan.md) §3.

| Extension | Role | Spec |
|-----------|------|------|
| Execution (V1) | Artifacts, balanced CTO gates, HS01–HS06 — **trust base** for all later extensions | [coding-agent/execution.md](coding-agent/execution.md) |
| Planning (V2) | Planning, doc gates, motivated self-learning (`learning_events.jsonl`), HS07–HS12 — **subordinate to V1** | [coding-agent/planning.md](coding-agent/planning.md) |
| Completion (V3) | Atomic execution, verification, HS13–HS16 | [coding-agent/completion.md](coding-agent/completion.md) |
| Events (V4) | Event store, replay, lineage, HS17–HS20 | [coding-agent/events.md](coding-agent/events.md) |
| Memory (V5) | Memory subsystem, HS21–HS24 | [coding-agent/memory.md](coding-agent/memory.md) |
| Evolution (V6) | Learning, evaluation, lifecycle, HS25–HS28 | [coding-agent/evolution.md](coding-agent/evolution.md) |
| Organization (V7) | Multi-agent, IAM, federation, HS29–HS32 | [coding-agent/organization.md](coding-agent/organization.md) |

## Coding-agent extension specs (read in order)

Read from **V1 upward** unless a doc sends you elsewhere. Early specs describe **one task, one run folder, provable checks**; later specs add **history, memory, learning, and many agents** — still on paper in places, but the **contracts** are written first on purpose. Each spec includes a **“How it works in practice”** section (concrete steps and files). The full **[master architecture](architecture/AI-Professional-Evolution-Master-Architecture.md)** is the long-form vision; [action-plan.md](onboarding/action-plan.md) §2 is the **short end-to-end story**.

1. **[SDE baseline](sde/what.md)** — CLI scope, `sde` commands, implementation contract entry points.
2. **[Execution — runtime and CTO gate contracts](coding-agent/execution.md)** — Per-run artifacts, strict balanced gates, hard-stops **HS01–HS06**. **HOW:** §"How the runtime drives a full-stack task" — pipeline stages, continuous gates, agent-as-junior model.
3. **[Planning — documentation and learning gates](coding-agent/planning.md)** — Motivated self-learning **inside the V1 safety envelope**; hard-stops **HS07–HS12**. **HOW:** §"How planning and learning work in practice" — Planner→Reviewer pipeline, learning feedback within runs.
4. **[Completion at scale](coding-agent/completion.md)** — Atomic steps, verification, DoD, hard-stops **HS13–HS16**. **HOW:** §"How the build loop works in practice" — step loop, bounded retries, verification, terminal honesty.
5. **[Events and replay](coding-agent/events.md)** — Append-only events, replay, hard-stops **HS17–HS20**. **HOW:** §"How the event trail works in practice" — event envelopes, replay verification, decision traceability.
6. **[Memory system](coding-agent/memory.md)** — Episodic/semantic/skill memory, hard-stops **HS21–HS24**. **HOW:** §"How memory supports full-stack delivery" — cross-run learning, provenance, contradiction handling.
7. **[Evolution — learning, evaluation, lifecycle](coding-agent/evolution.md)** — Reflection, promotion, practice, canary; hard-stops **HS25–HS28**. **HOW:** §"How self-improvement and progression work" — reflection→practice→promotion pipeline, canary testing.
8. **[Organization — multi-agent and IAM](coding-agent/organization.md)** — Leases, IAM matrix, federation; hard-stops **HS29–HS32**. **HOW:** §"How multi-agent spawning works" — workstream decomposition, parallel lanes, lease enforcement.

### Hard-stop index (cumulative by enabled extensions)

| Profile | Hard-stop range |
|---------|-----------------|
| Execution (delivery + gates) | HS01–HS06 |
| + Planning / documentation | HS01–HS12 |
| + Completion at scale | HS01–HS16 |
| + Event store / replay | HS01–HS20 |
| + Memory | HS01–HS24 |
| + Learning / lifecycle | HS01–HS28 |
| + Multi-agent / organization | HS01–HS32 |

Each extension under `docs/coding-agent/` ends with **Success is not assumed** — a **checklist** and **benchmark table**. “Done” means **every item checked**, benchmarks met, and **proof kept** (run ids, CI logs, artifacts) — not “we feel it works.”

## Research alignment (self-learning and improvement)

- **[Self-improvement and self-training research](research/self-improvement-research-alignment.md)** — Outside papers (Self-Refine, EVOLVE, STaR, and others), short explanations, and **how each idea maps to our specs**. **Does not** override V1 safety; it only suggests **how to measure and train** inside the rules.

## Architecture (system-wide)

- **[AI Professional Evolution — master architecture](architecture/AI-Professional-Evolution-Master-Architecture.md)** — Long **north-star** design for the whole platform (read in chunks).
- **[Action plan](onboarding/action-plan.md)** — **Shorter** story: goals, order of work, parallel agents, phases, “how good is good enough” metrics.
- **[Architecture goal completion](architecture/architecture-goal-completion.md)** — **Plain answer** to “if we finish every V1–V7 spec in this repo, did we finish the whole master doc?” (Usually: **strong on behavior and evidence**, **not** the same as deploying every service name in the master doc.)
- **[Operating system folder structure](architecture/operating-system-folder-structure.md)** — **Dream** repo layout aligned to the master doc; shows how this repo **differs** today.
- **[Swarm token and system requirements](architecture/swarm-token-and-system-requirements-math.md)** — **Math and budgets** for tokens, cost, and machine sizing — planning aid, not a tutorial.

## SDE baseline deep links

- [How checklist](sde/how-checklist.md)
- [Implementation contract](sde/implementation-contract.md)
- [Core features and upstream parity](sde/core-features-and-upstream-parity.md) — what is built vs SWE-agent / OpenHands patterns; suggested next steps
- [Project driver (meta-orchestrator)](sde/project-driver.md) — `project_plan.json`, `sde project run` / `status` / `validate`
- [SDE self-assessment and implementation loop](sde/sde-self-assessment-and-implementation-loop.md) — measure remaining work, re-check after each slice, paste-ready agent brief
- [Upstream harvest licenses](sde/upstream-harvest-licenses.md) — before vendoring code from `ideas/` checkouts
- [Decision / A–B protocol](sde/decision/ab-protocol-and-controls.md)
