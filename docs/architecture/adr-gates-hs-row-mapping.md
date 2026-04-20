# ADR: Hard-stop modules and row ownership (Part C TBD resolution)

**Status:** Accepted for folder migration (repo-only imports).  
**Context:** [`repository-layout-from-completion-inventory.md`](repository-layout-from-completion-inventory.md) Part C.1 marks several `sde_gates` targets as TBD or split across completion rows. Physical splits would force cross-section imports among mutually dependent modules (`hard_stops.py` aggregates all HS families; `review.py` / `run_directory.py` depend on manifest and metrics; several `hard_stops_*.py` depend on `run_profile.py`).

## Decision

1. **HS01–HS32 remain implemented in the same Python modules as today** (`hard_stops.py`, `hard_stops_guarded.py`, `hard_stops_events.py`, `hard_stops_memory.py`, `hard_stops_evolution.py`, `hard_stops_organization.py`). No loss of callables; no behavioral split across files for a single HS.

2. **Primary physical row for “enforcement + run profile + static + balanced + metrics”:** `src/guardrails_and_safety/risk_budgets/` — hosts all `hard_stops*.py`, `run_profile.py`, `static_analysis.py`, `balanced_gates.py`, `metrics_helpers.py`. Rationale: completion rows for permission/risk/static tooling are the closest umbrella; keeps the hard-stop dependency graph local.

3. **Review surface row:** `src/guardrails_and_safety/review_gating/` — hosts `review.py`, `run_directory.py`. Allowed to import sibling row `risk_budgets` within the same section (same `guardrails_and_safety` package family).

4. **Autonomy / token schema row:** `src/guardrails_and_safety/autonomy_boundaries_tokens_expiry/` — hosts `token_context.py`.

5. **Shared leaf modules → `libs/`** (no imports from other `sde_gates` internals except as noted):
   - `constants.py` → `libs/gates_constants/`
   - `time_util.py` → `libs/time_and_budget/`
   - `manifest.py` → `libs/gates_manifest/` (used by review, run_directory, hard-stop flows; avoids duplicating logic or creating forbidden cross-section edges)

6. **Public aggregate:** A thin `src/guardrails_and_safety/__init__.py` or dedicated facade module re-exports the symbols historically exported from `sde_gates.__init__` for callers that expect one import path (updated to the new paths in code during the migration).

## HS → owning *module file* (unchanged from pre-migration)

| HS range | Module file | Post-migration directory |
|----------|-------------|---------------------------|
| HS01–HS06 | `hard_stops.py` | `guardrails_and_safety/risk_budgets/` |
| HS07–HS16 | `hard_stops_guarded.py` | `guardrails_and_safety/risk_budgets/` |
| HS17–HS20 | `hard_stops_events.py` | `guardrails_and_safety/risk_budgets/` |
| HS21–HS24 | `hard_stops_memory.py` | `guardrails_and_safety/risk_budgets/` |
| HS25–HS28 | `hard_stops_evolution.py` | `guardrails_and_safety/risk_budgets/` |
| HS29–HS32 | `hard_stops_organization.py` | `guardrails_and_safety/risk_budgets/` |

Semantic alignment with completion-doc rows (memory, events, evolution, org services) remains **documentation / scoring**; physical tree prioritizes **import acyclicity** and **zero-loss**.

## Consequences

- Completion inventory paths that suggested splitting `hard_stops_*` across `memory_architecture`, `event_sourced_architecture`, etc. are **not** applied as physical file locations in this migration.
- Future work may duplicate thin facades into domain rows if import-linter rules require stricter boundaries.
