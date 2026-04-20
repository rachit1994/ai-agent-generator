"""§13.B — regression surface anchors vs disk."""

from __future__ import annotations

from pathlib import Path

from workflow_pipelines.production_pipeline_task_to_promote.benchmark.regression_surface_contract import (
    REGRESSION_DIMENSION_ANCHORS,
    REGRESSION_SURFACE_CONTRACT,
    validate_regression_anchors,
)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[5]


def test_regression_surface_contract_id() -> None:
    assert REGRESSION_SURFACE_CONTRACT == "sde.regression_surface.v1"


def test_regression_dimension_anchors_non_empty() -> None:
    assert len(REGRESSION_DIMENSION_ANCHORS) >= 4


def test_validate_regression_anchors_clean_on_repo_tree() -> None:
    assert validate_regression_anchors(_repo_root()) == []
