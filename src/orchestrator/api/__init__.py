"""Public import surface for the orchestrator service.

Callers outside this package should import from ``orchestrator.api`` rather than
reaching into ``sde_pipeline`` / ``sde_modes`` / ``sde_foundations`` unless extending internals
(tests, mode plugins).
"""

from sde_pipeline.benchmark import run_benchmark
from sde_pipeline.report import generate_report
from sde_pipeline.runner import execute_single_task

__all__ = ["execute_single_task", "run_benchmark", "generate_report"]
