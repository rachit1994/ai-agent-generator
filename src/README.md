# `src`

**Docs:** the minimum reading list for this tree is **[`../docs/ESSENTIAL.md`](../docs/ESSENTIAL.md)** (do not start from the big `docs/README.md` stack).

**In plain words:** all runnable Python lives here in a **flat** tree: one **`orchestrator`** package (CLI + small API) and four **`sde_*`** packages. When someone runs `sde`, the tool writes under repo-root **`outputs/`** (usually gitignored)—not under `src/`.

## Where to look first

- **Orchestrator:** [`orchestrator/`](orchestrator/) — [`api/`](orchestrator/api/) (**import here from other code**; see [`api/README.md`](orchestrator/api/README.md)), `runtime/cli/main.py` (**where terminal commands start**), `tests/unit/` (pytest). Session **Stage 1 plan lock** (readiness, `project_plan_lock.json`, `validate --require-plan-lock`, `run` / `continuous --enforce-plan-lock`): `api/project_plan_lock.py`, `project_driver.py`, `continuous_run.py`, `project_validate.py` — see [`docs/sde/project-driver.md`](../docs/sde/project-driver.md).
- **CLI:** `sde` / `agent` → `orchestrator.runtime.cli.main:main` (`pyproject.toml`).
- **Foundations:** [`sde_foundations/`](sde_foundations/) — types, storage, utils, model adapter, safeguards.
- **Gates:** [`sde_gates/`](sde_gates/) — CTO gates, review, hard-stops, `validate_execution_run_directory`, split **hard-stop** helpers (`hard_stops_events.py`, `hard_stops_memory.py`, …) aligned with specs.
- **Modes:** [`sde_modes/modes/`](sde_modes/modes/) — baseline, guarded, guarded pipeline (`phased_pipeline` too).
- **Pipeline:** [`sde_pipeline/`](sde_pipeline/) — config, **`runner/single_task.py`** (heart of one run), benchmark, report, replay, plus **post-run layers** that write extra harness folders on guarded success paths:
  - `completion_layer.py` — V3 completion stubs (`program/`, `step_reviews/`, …).
  - `event_lineage_layer.py` — replay manifest + event store envelope.
  - `memory_artifact_layer.py`, `evolution_layer.py`, `organization_layer.py` — memory / evolution / org harness files + matching gate modules under `sde_gates/`.

**CI / Python:** [`.github/workflows/ci.yml`](../.github/workflows/ci.yml) uses **3.11**, same as repo-root **`.python-version`** for **`uv`**. Check with **`uv run python -V`**; use **`uv run --python 3.11 …`** only if **`uv`** is not honoring the pin.

## Master OS layout

The full multi-service tree (contracts, services, infra, tools, …) is described in **[`docs/architecture/operating-system-folder-structure.md`](../docs/architecture/operating-system-folder-structure.md)** as the **target** layout. This repo keeps **`src/`** minimal until those slices ship.

## Documentation

- **Easy on-ramp:** **[`docs/onboarding/start-here-reading-the-docs.md`](../docs/onboarding/start-here-reading-the-docs.md)** · **[`docs/onboarding/start-here-reading-the-code.md`](../docs/onboarding/start-here-reading-the-code.md)**
- **Engineers:** **[`docs/onboarding/developer-walkthrough.md`](../docs/onboarding/developer-walkthrough.md)** · **[`docs/onboarding/action-plan.md`](../docs/onboarding/action-plan.md)**
