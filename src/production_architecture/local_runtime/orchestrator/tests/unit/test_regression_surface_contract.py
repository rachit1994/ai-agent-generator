"""§13.B — regression surface anchors vs disk."""

from __future__ import annotations

from pathlib import Path

import pytest

from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.benchmark.regression_surface_contract import (
    REGRESSION_DIMENSION_ANCHORS,
    REGRESSION_DIMENSIONS,
    REGRESSION_SURFACE_CONTRACT,
    validate_regression_anchors,
)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[6]


def test_regression_surface_contract_id() -> None:
    assert REGRESSION_SURFACE_CONTRACT == "sde.regression_surface.v1"


def test_regression_dimension_anchors_non_empty() -> None:
    assert len(REGRESSION_DIMENSION_ANCHORS) >= 4


def test_regression_dimension_anchors_cover_expected_dimensions() -> None:
    assert set(REGRESSION_DIMENSIONS) == {"capability", "safety", "memory", "coordination"}
    assert {dimension for dimension, _ in REGRESSION_DIMENSION_ANCHORS} == set(REGRESSION_DIMENSIONS)


def test_validate_regression_anchors_clean_on_repo_tree() -> None:
    assert validate_regression_anchors(_repo_root()) == []


def test_validate_regression_anchors_reports_all_missing_tokens_in_order(tmp_path: Path) -> None:
    errors = validate_regression_anchors(tmp_path)
    expected = [
        f"regression_surface_missing_{dimension}_{Path(rel).stem}"
        for dimension, rel in REGRESSION_DIMENSION_ANCHORS
    ]
    assert errors == expected


def test_validate_regression_anchors_rejects_unknown_dimension(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    rel = "src/production_architecture/local_runtime/orchestrator/tests/unit/test_eval.py"
    path = tmp_path / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("ok", encoding="utf-8")
    monkeypatch.setattr(
        "workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.benchmark.regression_surface_contract.REGRESSION_DIMENSION_ANCHORS",
        (("unknown", rel),),
    )
    errors = validate_regression_anchors(tmp_path)
    assert "regression_surface_unknown_dimension_unknown" in errors


def test_validate_regression_anchors_rejects_duplicate_anchor(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    rel = "src/production_architecture/local_runtime/orchestrator/tests/unit/test_eval.py"
    path = tmp_path / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("ok", encoding="utf-8")
    monkeypatch.setattr(
        "workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.benchmark.regression_surface_contract.REGRESSION_DIMENSION_ANCHORS",
        (("capability", rel), ("safety", rel)),
    )
    errors = validate_regression_anchors(tmp_path)
    assert "regression_surface_duplicate_anchor_test_eval" in errors
    assert "regression_surface_dimension_uncovered_memory" in errors
    assert "regression_surface_dimension_uncovered_coordination" in errors
