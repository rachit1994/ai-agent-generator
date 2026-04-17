# Documentation index

## Extension map (single canonical tree)

All coding-agent capability specs live under **`docs/coding-agent/`** — no `docs/v1/`-style directories or numbered mirrors.

| Extension | Role | Spec |
|-----------|------|------|
| Execution | Artifacts, balanced CTO gates, HS01–HS06 | [coding-agent/execution.md](coding-agent/execution.md) |
| Planning | Self-learning-first planning and doc gates, HS07–HS12 | [coding-agent/planning.md](coding-agent/planning.md) |
| Completion | Atomic execution, verification, HS13–HS16 | [coding-agent/completion.md](coding-agent/completion.md) |
| Events | Event store, replay, lineage, HS17–HS20 | [coding-agent/events.md](coding-agent/events.md) |
| Memory | Memory subsystem, HS21–HS24 | [coding-agent/memory.md](coding-agent/memory.md) |
| Evolution | Learning, evaluation, lifecycle, HS25–HS28 | [coding-agent/evolution.md](coding-agent/evolution.md) |
| Organization | Multi-agent, IAM, federation, HS29–HS32 | [coding-agent/organization.md](coding-agent/organization.md) |

## Coding-agent extension specs (read in order)

These specs ladder from **task delivery** (execution through completion) toward the full **[AI Professional Evolution — master architecture](AI-Professional-Evolution-Master-Architecture.md)** platform spine (events through organization). Later extensions map explicitly to master sections (see **Repository version specifications** under §17 in that document).

1. **[SDE baseline](sde/what.md)** — CLI scope, `sde` commands, implementation contract entry points.
2. **[Execution — runtime and CTO gate contracts](coding-agent/execution.md)** — Per-run artifacts under `outputs/runs/<run-id>/`, strict balanced gates (Reliability, Delivery, Governance), hard-stops **HS01–HS06**, token/context evidence.
3. **[Planning — documentation and learning gates](coding-agent/planning.md)** — **Self-learning first** (mandatory `learning_events.jsonl` minima, synthesis, playbook deltas); discovery through plan lock; question workbook, in-repo doc pack, documentation review before implementation; hard-stops **HS07–HS12**.
4. **[Completion at scale](coding-agent/completion.md)** — Atomic steps with per-step reviews, batching/resume, verification bundle, Definition of Done, hard-stops **HS13–HS16**.
5. **[Events and replay](coding-agent/events.md)** — Append-only events, replay manifests, kill switch lineage, idempotency; hard-stops **HS17–HS20**; master **§12**, **§15** (foundation), **§17 Phase 0**, **§14** replay, **§19.D P0**.
6. **[Memory system](coding-agent/memory.md)** — Episodic/semantic/skill memory, provenance, quarantine, quality metrics; hard-stops **HS21–HS24**; master **§8**, **§17 Phase 1**.
7. **[Evolution — learning, evaluation, lifecycle](coding-agent/evolution.md)** — Reflection bundles, promotion packages, practice loop, canary; hard-stops **HS25–HS28**; master **§6**, **§9**, **§11**, **§13**, **§17 Phases 1–3**.
8. **[Organization — multi-agent and IAM](coding-agent/organization.md)** — Leases, IAM matrix, federated shards, strategy proposals; hard-stops **HS29–HS32**; master **§5**, **§15** (IAM), **§16**, **§17 Phases 2–4**.

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

- **[AI Professional Evolution — master architecture](AI-Professional-Evolution-Master-Architecture.md)**
- **[Architecture goal completion](architecture-goal-completion.md)** — When “all versions” are done: how extension specs map to the master goal, §14 gates, §17 phases, and what remains for §28-style operational completeness
- **[Operating system folder structure](operating-system-folder-structure.md)**
- **[Swarm token and system requirements](swarm-token-and-system-requirements-math.md)**

## SDE baseline deep links

- [How checklist](sde/how-checklist.md)
- [Implementation contract](sde/implementation-contract.md)
- [Decision / A–B protocol](sde/decision/ab-protocol-and-controls.md)
