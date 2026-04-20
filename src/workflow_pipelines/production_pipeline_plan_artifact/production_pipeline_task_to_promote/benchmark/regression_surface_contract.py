"""Repo-honest anchors for §13 regression dimensions (capability / safety / memory / coordination)."""

from __future__ import annotations

from pathlib import Path
from typing import Final

REGRESSION_SURFACE_CONTRACT: Final = "sde.regression_surface.v1"

_ORCH_UNIT: Final = (
    "src/production_architecture/local_runtime/orchestrator/tests/unit"
)

REGRESSION_DIMENSION_ANCHORS: Final[tuple[tuple[str, str], ...]] = (
    ("capability", f"{_ORCH_UNIT}/test_eval.py"),
    ("capability", f"{_ORCH_UNIT}/test_verify_core_hints.py"),
    ("safety", f"{_ORCH_UNIT}/test_safeguards.py"),
    ("safety", f"{_ORCH_UNIT}/test_static_gates.py"),
    ("memory", f"{_ORCH_UNIT}/test_memory_hard_stops.py"),
    ("memory", f"{_ORCH_UNIT}/test_context_pack.py"),
    ("coordination", f"{_ORCH_UNIT}/test_project_parallel.py"),
    ("coordination", f"{_ORCH_UNIT}/test_evolution_organization_hard_stops.py"),
)


def validate_regression_anchors(root: Path) -> list[str]:
    """Return stable error tokens; empty means every anchor file exists under ``root``."""
    errs: list[str] = []
    for dimension, rel in REGRESSION_DIMENSION_ANCHORS:
        path = root / rel
        if not path.is_file():
            errs.append(f"regression_surface_missing_{dimension}_{path.stem}")
    return errs
