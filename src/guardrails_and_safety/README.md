# `guardrails_and_safety`

Completion-doc–aligned **CTO gates**: hard-stops (HS01–HS32), static analysis, balanced scores, metrics helpers, run profile, and review / run-directory validation.

| Subfolder | Role |
|-----------|------|
| **`risk_budgets/`** | Hard-stop modules, `hard_stop_schedule` (which **HS** rows run per **mode** + artifacts), `static_analysis`, `balanced_gates`, `metrics_helpers`, `run_profile`. |
| **`review_gating/`** | `build_review` → **`review.json`** (incl. **`review_findings`** §11), `validate_execution_run_directory`, **`policy_bundle_rollback`** (§11.E). **HS08** (in **`risk_budgets/hard_stops_guarded.py`**) enforces **`program/dual_control_ack.json`** when doc review requires dual control (§11.D). |
| **`autonomy_boundaries_tokens_expiry/`** | **`build_token_context`** (per-stage budgets + **`context_expires_at`** / anchor / TTL for §11.C). |

The package root **`guardrails_and_safety`** re-exports the historical aggregate surface (see **`__init__.py`**). Shared **constants**, **manifest**, and **time** helpers live in repo-root **`libs/`** (`gates_constants`, `gates_manifest`, `time_and_budget`); see [`libs/README.md`](../../libs/README.md). Full path list: [`docs/architecture/repository-layout-from-completion-inventory.md`](../../docs/architecture/repository-layout-from-completion-inventory.md) (Part A).

**Regression:** `orchestrator/tests/unit/test_public_export_surface.py` pins public **`def`** entrypoints on **`review_gating/*`**, **`autonomy_boundaries_tokens_expiry/*`**, and **`risk_budgets/*`** (including each **`evaluate_*_hard_stops`**) against the pre-layout **`sde_gates`** tree (see that file’s module docstring).
