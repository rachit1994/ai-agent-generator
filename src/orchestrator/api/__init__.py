"""Public import surface for the orchestrator service.

Callers outside this package should import from ``orchestrator.api`` rather than
reaching into ``sde_pipeline`` / ``sde_modes`` / ``sde_foundations`` unless extending internals
(tests, mode plugins).
"""

from sde_pipeline.benchmark import run_benchmark
from sde_pipeline.replay import replay_run
from sde_pipeline.report import generate_report
from sde_pipeline.runner import execute_single_task

from .gemma_roadmap_review import append_roadmap_learning_line, roadmap_review
from .continuous_run import run_continuous_project_session, run_continuous_until
from .project_driver import run_project_session
from .project_status import describe_project_session
from .project_validate import validate_project_session
from .self_evolve import run_bounded_evolve_loop
from .validate_run import validate_run

__all__ = [
    "append_roadmap_learning_line",
    "execute_single_task",
    "generate_report",
    "replay_run",
    "roadmap_review",
    "run_benchmark",
    "run_bounded_evolve_loop",
    "run_continuous_project_session",
    "run_continuous_until",
    "run_project_session",
    "describe_project_session",
    "validate_project_session",
    "validate_run",
]
