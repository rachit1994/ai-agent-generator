"""Public import surface for the orchestrator service.

Callers outside this package should import from ``orchestrator.api`` rather than
reaching into ``orchestrator.runtime`` unless they are extending runtime internals
(tests, mode plugins).
"""

from orchestrator.runtime.benchmark import run_benchmark
from orchestrator.runtime.report import generate_report
from orchestrator.runtime.runner import execute_single_task

__all__ = ["execute_single_task", "run_benchmark", "generate_report"]
