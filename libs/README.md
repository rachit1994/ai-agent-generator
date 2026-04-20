# `libs/` (repo-root shared Python packages)

Small, importable packages used from **`src/guardrails_and_safety/`**, **`src/workflow_pipelines/`**, and **`orchestrator`**. **`libs/`** must not import from `src/` section trees.

| Package | Role |
|---------|------|
| **`storage`** | JSON / JSONL persistence helpers. |
| **`common`** | Shared utilities (`outputs_base`, run ids, …). |
| **`sde_types`** | Trace/score types (name avoids stdlib **`types`**). |
| **`sde_eval`** | Metrics aggregation and gate verdict helpers. |
| **`artifacts`**, **`model_adapter`**, **`safeguards`** | Run artifacts, model boundary, execution safeguards. |
| **`gates_constants`**, **`gates_manifest`**, **`time_and_budget`** | Gate constants, manifest paths, shared time helpers. |

Import table for old **`sde_foundations.*`** names → **`CHANGELOG.md`**. Layout inventory: [`docs/architecture/repository-layout-from-completion-inventory.md`](../docs/architecture/repository-layout-from-completion-inventory.md) Part A.

**Regression:** `test_public_export_surface.py` (under **`orchestrator/tests/unit/`**) asserts migrated **`libs/`** modules still expose the same top-level names as pre-layout **`sde_foundations`** / gate leaf modules (see file docstring for git baseline).
