# Production Workflow Manifest

## What this file is
The **production workflow manifest** is the version-controlled list of **every** persona workflow that must compile, run, pass gates, and ship evidence for **production exit**. It is the same set as `critical_workflows` in `docs/implementation/2026-04-13-persona-agent-platform-release-gate-spec.md`.

**Normative interpretation:** `docs/implementation/2026-04-13-persona-agent-platform-doc-precedence.md`.

## Rules
1. **One row per workflow** the compiler supports from `docs/personas` and `docs/more_personas`.
2. **No implicit scope:** if a workflow is not listed, it is **out of production exit** until the manifest is updated with EM + Tech Lead sign-off and gate re-evidence is planned.
3. **Freeze** means changes require manifest revision, DOR, and updated CI/evidence mapping—not “fewer workflows.”

## Stable `workflow_id` (Phase 1 → Phase 2 handoff)
Until the compiler is the single generator of IDs, **each** `workflow_id` is the **dotted repo path** of the persona Markdown **without** the `.md` suffix, rooted at `docs`, with `/` replaced by `.`:
- Example file `docs/personas/software-engineer.md` → `workflow_id` **`docs.personas.software-engineer`**
- Example file `docs/more_personas/data-ai-and-crm-intelligence.md` → **`docs.more_personas.data-ai-and-crm-intelligence`**

**Do not invent alternate slugs** in Phase 1; if the compiler later needs a different internal key, the **same PR** that introduces the compiler must either (a) keep these dotted paths as the external stable IDs or (b) update **every** manifest row, CI mapping, and gate packet reference with **EM + Tech Lead** sign-off in the promotion packet.

**Inventory procedure (intern-safe):**
1. Enumerate all `*.md` files under `docs/personas/` and `docs/more_personas/` (exclude `README.md` and other index-only files unless they are themselves compiled personas—when in doubt, ask Tech Lead before adding a row).
2. Add one table row per file using the rule above **unless** the compiler contract defines **multiple** `workflow_id` values from a single source file (for example several compiled task types). In that case, add **one row per compiler-emitted `workflow_id`** and record the `(source path → id list)` mapping in the Phase 2 PR description and gate packet.
3. Tech Lead signs the manifest PR as “IDs match compiler contract for Phase 2.”

## Column literals (no free-form ambiguity)
| Column | Allowed values |
|--------|----------------|
| `Compiler version / commit` | `pre-compiler` until Phase 2 first successful compile for that row; thereafter the **merge commit SHA** (full 40 chars) of the build that produced the green compile. |
| `Owner DRI` | `pending-DOR-assignment` until a named human is assigned at that workflow’s first DOR; then **legal name** of primary DRI. While `pending-DOR-assignment`, **Tech Lead** is accountable. |
| `Last green gate run (link)` | `no-evidence-yet` until first CI or packet URL exists; thereafter **immutable URL** or repo path under `evidence/gate-packets/`. |

## Table (production inventory — Phase 1 approved)

| `workflow_id` | Source path (persona doc) | Compiler version / commit | Owner DRI | Last green gate run (link) |
|----------------|---------------------------|-----------------------------|-----------|----------------------------|
| `docs.personas.software-engineer` | `docs/personas/software-engineer.md` | `pre-compiler` | `pending-DOR-assignment` | `no-evidence-yet` |
| `docs.personas.sales` | `docs/personas/sales.md` | `pre-compiler` | `pending-DOR-assignment` | `no-evidence-yet` |
| `docs.personas.data-analyst` | `docs/personas/data-analyst.md` | `pre-compiler` | `pending-DOR-assignment` | `no-evidence-yet` |
| `docs.personas.internet-researcher` | `docs/personas/internet-researcher.md` | `pre-compiler` | `pending-DOR-assignment` | `no-evidence-yet` |
| `docs.personas.event-network-roles` | `docs/personas/event-network-roles.md` | `pre-compiler` | `pending-DOR-assignment` | `no-evidence-yet` |
| `docs.personas.product-manager` | `docs/personas/product-manager.md` | `pre-compiler` | `pending-DOR-assignment` | `no-evidence-yet` |
| `docs.personas.social-media-marketing` | `docs/personas/social-media-marketing.md` | `pre-compiler` | `pending-DOR-assignment` | `no-evidence-yet` |
| `docs.more_personas.event-operations-and-regional-programs` | `docs/more_personas/event-operations-and-regional-programs.md` | `pre-compiler` | `pending-DOR-assignment` | `no-evidence-yet` |
| `docs.more_personas.revenue-and-sponsor-growth` | `docs/more_personas/revenue-and-sponsor-growth.md` | `pre-compiler` | `pending-DOR-assignment` | `no-evidence-yet` |
| `docs.more_personas.content-facilitation-and-community` | `docs/more_personas/content-facilitation-and-community.md` | `pre-compiler` | `pending-DOR-assignment` | `no-evidence-yet` |
| `docs.more_personas.technical-production-and-accessibility` | `docs/more_personas/technical-production-and-accessibility.md` | `pre-compiler` | `pending-DOR-assignment` | `no-evidence-yet` |
| `docs.more_personas.executive-recruitment-and-concierge` | `docs/more_personas/executive-recruitment-and-concierge.md` | `pre-compiler` | `pending-DOR-assignment` | `no-evidence-yet` |
| `docs.more_personas.people-hr-and-innovation` | `docs/more_personas/people-hr-and-innovation.md` | `pre-compiler` | `pending-DOR-assignment` | `no-evidence-yet` |
| `docs.more_personas.executive-leadership-and-strategy` | `docs/more_personas/executive-leadership-and-strategy.md` | `pre-compiler` | `pending-DOR-assignment` | `no-evidence-yet` |
| `docs.more_personas.data-ai-and-crm-intelligence` | `docs/more_personas/data-ai-and-crm-intelligence.md` | `pre-compiler` | `pending-DOR-assignment` | `no-evidence-yet` |
| `docs.more_personas.legal-compliance-security-and-risk` | `docs/more_personas/legal-compliance-security-and-risk.md` | `pre-compiler` | `pending-DOR-assignment` | `no-evidence-yet` |
| `docs.more_personas.finance-and-performance-analytics` | `docs/more_personas/finance-and-performance-analytics.md` | `pre-compiler` | `pending-DOR-assignment` | `no-evidence-yet` |

## Empty table (definition)
If the table has **zero** data rows (header only), production exit is **impossible** by definition. The table above is **non-empty**; Phase 1 inventory for listed paths is **complete** until personas are added or removed under change control.
