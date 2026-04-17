# Documentation index

## Documentation layout

| Folder | What lives here |
|--------|-----------------|
| **[`onboarding/`](onboarding/)** | Easy entry guides, engineer walkthrough, and the **[action plan](onboarding/action-plan.md)** (product goal, precedence, phases). |
| **[`architecture/`](architecture/)** | Master blueprint, completion definition vs full OS deploy, target folder layout, swarm/token math. |
| **[`coding-agent/`](coding-agent/)** | Versioned extension specs (V1–V7): execution through organization — the conformance spine for the SDE slice. |
| **[`sde/`](sde/)** | SDE baseline: CLI scope, contracts, prompts, pipeline planning. |
| **[`research/`](research/)** | External research mapped to specs (e.g. self-improvement techniques). |

---

## New here? Pick one path

| Audience | Start here |
|----------|------------|
| **Easy entry — documentation** | **[start-here-reading-the-docs.md](onboarding/start-here-reading-the-docs.md)** — glossary, why the project exists, what V1–V7 mean, simple reading order |
| **Easy entry — code** | **[start-here-reading-the-code.md](onboarding/start-here-reading-the-code.md)** — folder map, which files to open first, what is built vs still on paper |
| **Engineer onboarding** | **[Developer walkthrough](onboarding/developer-walkthrough.md)** — repo map, CLI flow, first-day checklist |

## New to the codebase?

Start with **[Developer walkthrough](onboarding/developer-walkthrough.md)** — reading order, repository map, where the CLI enters the code, how `outputs/` works, and a first-day checklist.

**Product + delivery plan:** **[Action plan](onboarding/action-plan.md)** — full-stack / company-process goal, **global precedence** (V1 safety before self-learning and speed), **V1–V7 as one combined product**, parallel junior agents, capability yardsticks, phased implementation.

---

## Extension map (single canonical tree)

All coding-agent capability specs live under **`docs/coding-agent/`** — no `docs/v1/`-style directories or numbered mirrors. **V1–V7 are staged slices of one product** (see [action-plan.md](onboarding/action-plan.md) §3).

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

These specs ladder from **task delivery** (execution through completion) toward the full **[AI Professional Evolution — master architecture](architecture/AI-Professional-Evolution-Master-Architecture.md)** platform spine (events through organization). Each spec now includes a **"How it works in practice"** section with concrete orchestration flows. See [action-plan.md](onboarding/action-plan.md) §2 for the end-to-end story.

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

Each extension spec under `docs/coding-agent/` includes **Success is not assumed** — a mandatory **checklist** and **benchmark table**. An extension is **not** treated as successful unless every box is checked and every benchmark passes with retained evidence.

## Research alignment (self-learning and improvement)

- **[Self-improvement and self-training research](research/self-improvement-research-alignment.md)** — Bibliography (Self-Refine, EVOLVE, STaR, ReST^EM, B-STaR, Mind the Gap, Sol-Ver, S3FT, Constitutional AI, DSVD), technique summaries, and mapping to `docs/coding-agent/*.md`.

## Architecture (system-wide)

- **[AI Professional Evolution — master architecture](architecture/AI-Professional-Evolution-Master-Architecture.md)**
- **[Action plan](onboarding/action-plan.md)** — Product goal, precedence, version rollup, parallel agents, phased execution, capability metrics
- **[Architecture goal completion](architecture/architecture-goal-completion.md)** — When “all versions” are done: how extension specs map to the master goal, §14 gates, §17 phases, and what remains for §28-style operational completeness
- **[Operating system folder structure](architecture/operating-system-folder-structure.md)**
- **[Swarm token and system requirements](architecture/swarm-token-and-system-requirements-math.md)**

## SDE baseline deep links

- [How checklist](sde/how-checklist.md)
- [Implementation contract](sde/implementation-contract.md)
- [Decision / A–B protocol](sde/decision/ab-protocol-and-controls.md)
