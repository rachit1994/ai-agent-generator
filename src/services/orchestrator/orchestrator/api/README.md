# `orchestrator.api`

Stable import surface for the orchestrator service. Prefer:

```python
from orchestrator.api import execute_single_task, run_benchmark, generate_report
```

instead of importing submodules under `orchestrator.runtime` from outside this service.
