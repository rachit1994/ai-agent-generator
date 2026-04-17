# `src`

Flat Python source tree: **`orchestrator`** (CLI + public API) and four **`sde_*`** packages (foundation, gates, modes, pipeline). Run artifacts stay under repo-root **`outputs/`** (gitignored), not here.

## Where to look first

- **Orchestrator:** [`orchestrator/`](orchestrator/) — `api/` (public surface), `runtime/cli/` (CLI entrypoint), `tests/unit/` (pytest).
- **CLI:** `sde` / `agent` → `orchestrator.runtime.cli.main:main` (`pyproject.toml`).
- **Foundations:** [`sde_foundations/`](sde_foundations/) — types, storage, utils, model adapter, safeguards.
- **Gates:** [`sde_gates/`](sde_gates/) — CTO gates, review, hard-stops, run-directory validation.
- **Modes:** [`sde_modes/modes/`](sde_modes/modes/) — baseline, guarded, guarded pipeline.
- **Pipeline:** [`sde_pipeline/`](sde_pipeline/) — config, runner, benchmark, report, run logging.

## Master OS layout

The full multi-service tree (contracts, services, infra, tools, …) is described in **[`docs/architecture/operating-system-folder-structure.md`](../docs/architecture/operating-system-folder-structure.md)** as the **target** layout. This repo keeps **`src/`** minimal until those slices ship.

## Documentation

- **Easy on-ramp:** **[`docs/onboarding/start-here-reading-the-docs.md`](../docs/onboarding/start-here-reading-the-docs.md)** · **[`docs/onboarding/start-here-reading-the-code.md`](../docs/onboarding/start-here-reading-the-code.md)**
- **Engineers:** **[`docs/onboarding/developer-walkthrough.md`](../docs/onboarding/developer-walkthrough.md)** · **[`docs/onboarding/action-plan.md`](../docs/onboarding/action-plan.md)**
