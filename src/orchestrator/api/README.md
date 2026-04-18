# `orchestrator.api`

**Docs:** read **[`../../../docs/ESSENTIAL.md`](../../../docs/ESSENTIAL.md)** before you chase every file under `docs/`.

**In plain words:** this package is the **stable front door** for Python code that wants to drive SDE without reaching deep into `sde_pipeline` or `sde_modes`. The CLI in `orchestrator.runtime.cli.main` calls these same functions.

Prefer:

```python
from orchestrator.api import (
    append_roadmap_learning_line,
    describe_project_session,
    execute_single_task,
    generate_report,
    replay_run,
    roadmap_review,
    run_benchmark,
    run_bounded_evolve_loop,
    run_continuous_project_session,
    run_continuous_until,
    run_project_session,
    validate_project_session,
    validate_run,
)
```

| Import | Everyday job |
|--------|----------------|
| `execute_single_task` | One task → one folder under `outputs/runs/<id>/`. |
| `run_benchmark` / `generate_report` / `replay_run` | Suite runs, Markdown report, trajectory / optional rerun. |
| `validate_run` | Check an existing run folder (strict single-task contract **or** light benchmark-dir check). |
| `roadmap_review` / `append_roadmap_learning_line` | Ask the support model for a roadmap % digest; append a learning JSONL line. |
| `run_bounded_evolve_loop` | Bounded “review → optional task → repeat” cadence (not magic completion). |
| `run_continuous_until` / `run_continuous_project_session` | Task repeat loop **or** project session loop used by `sde continuous`. |
| `run_project_session` | Meta-orchestrator: walk `project_plan.json` steps, verification, progress (see `docs/sde/project-driver.md`). |
| `validate_project_session` / `describe_project_session` | Read-only plan + workspace checks; full JSON status snapshot (`status_at_a_glance`, rollups, caps). |

Use **`from orchestrator.api import …`** instead of importing `sde_pipeline`, `sde_modes`, or `sde_foundations` directly from outside this service (except tests and internal extensions).
