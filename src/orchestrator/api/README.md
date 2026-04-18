# `orchestrator.api`

Stable import surface for the orchestrator service. Prefer:

```python
from orchestrator.api import (
    execute_single_task,
    generate_report,
    roadmap_review,
    run_benchmark,
    run_bounded_evolve_loop,
    run_continuous_until,
    validate_run,
)
```

instead of importing `sde_pipeline`, `sde_modes`, or `sde_foundations` directly from outside this service (except tests and extensions).
