# Production Workflow Manifest (Template)

## What this file is
The **production workflow manifest** is the version-controlled list of **every** persona workflow that must compile, run, pass gates, and ship evidence for **production exit**. It is the same set as `critical_workflows` in `docs/implementation/2026-04-13-persona-agent-platform-release-gate-spec.md`.

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

## Table (copy and fill)

| `workflow_id` | Source path (persona doc) | Compiler version / commit | Owner DRI | Last green gate run (link) |
|----------------|---------------------------|-----------------------------|-----------|----------------------------|
| `example.persona.workflow` | `docs/personas/...` | `git SHA` | Name | CI URL or artifact path |

## Empty manifest
If the table is empty, **production exit is impossible** by definition. Phase 1 of the implementation roadmap must produce the first approved rows before Phase 2 compiler acceptance against “100% of manifest” applies.
