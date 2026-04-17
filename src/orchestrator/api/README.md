# `orchestrator.api`

Stable import surface for the orchestrator service. Prefer:

```python
from orchestrator.api import execute_single_task, run_benchmark, generate_report
```

instead of importing `sde_pipeline`, `sde_modes`, or `sde_foundations` directly from outside this service (except tests and extensions).
