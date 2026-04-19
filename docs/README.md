# Documentation

**In plain words:** do **not** treat this folder like a book you read cover to cover.

## Start here (required path)

**[`ESSENTIAL.md`](ESSENTIAL.md)** — the **only** reading list you need to follow the code and use the CLI. It points to **four** Markdown files at most, then **`src/`** READMEs and `main.py`.

---

## Optional reference (open only when you need it)

| Area | What it is |
|------|-------------|
| **[`onboarding/`](onboarding/)** | Longer onboarding pages (glossary, walkthrough, action plan). **Not** required if you followed **`ESSENTIAL.md`**. |
| **[`sde/`](sde/)** | SDE contracts, parity tables, project driver detail, checklists. |
| **[`coding-agent/`](coding-agent/)** | **Stub only** — old V1–V7 Markdown specs were removed; see [`coding-agent/README.md`](coding-agent/README.md). |
| **[`architecture/`](architecture/)** | North-star architecture, “when are we done?”, dream folder layout, **[full OS delivery checklist](architecture/company-os-full-delivery-checklist.md)**, **[path to 100% / milestones vs `src/`](architecture/company-os-path-to-100-percent.md)**. |
| **[`versioning/`](versioning/)** | **[Per-feature version plans](versioning/README.md)** (checklist → `plans/` + [`INDEX`](versioning/INDEX.md)). |
| **[`runbooks/`](runbooks/)** | Operator recovery guides for failure modes (for example **[Stage 1 intake failures](runbooks/stage1-intake-failures.md)**). |
| **[`adrs/`](adrs/)** | Architecture Decision Records (S1a policy: reviewer attestation, model revise scope). |
| **[`research/`](research/)** | Papers mapped to specs — never overrides V1 safety; **[stable libraries brief (2026)](research/stable-libraries-advancements-2026.md)** for LangGraph, memory, RAG, jobs, sandboxes. |

### SDE deep links (same as `sde/` folder)

- [Implementation contract](sde/implementation-contract.md)
- [Project driver](sde/project-driver.md)
- [Core features vs upstream](sde/core-features-and-upstream-parity.md)
- [How checklist](sde/how-checklist.md)
- [Upstream harvest licenses](sde/upstream-harvest-licenses.md)
- [Decision / A–B protocol](sde/decision/ab-protocol-and-controls.md)

### Handy scripts

- Stage 1 verification subset: `scripts/run-stage1-suite.sh` (optional wall clock: `STAGE1_SUITE_MAX_SECONDS`; flags/env for lock enforcement: [`sde/project-driver.md`](sde/project-driver.md) Stage 1 section).
- Stage 1 golden CLI path (scaffold → lock → validate → export): `scripts/stage1-cold-start-demo.sh` (see [`runbooks/stage1-intake-failures.md`](runbooks/stage1-intake-failures.md) §Golden cold start).
- Version plan index only: `scripts/version-index-only.sh` — refreshes [`versioning/INDEX.md`](versioning/INDEX.md) from `plans/*.md` titles without overwriting plan bodies ([`versioning/README.md`](versioning/README.md)).
