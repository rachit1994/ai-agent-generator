"""§13.C — ``promotion_package.json`` structural contract (promotion eval / **HS26**)."""

from __future__ import annotations

from pathlib import Path

from workflow_pipelines.production_pipeline_task_to_promote.benchmark.promotion_eval_contract import (
    PROMOTION_EVAL_PACKAGE_CONTRACT,
    validate_promotion_package_dict,
    validate_promotion_package_path,
)
from workflow_pipelines.production_pipeline_task_to_promote.runner.evolution_layer import (
    write_evolution_artifacts,
)


def test_promotion_eval_contract_constant_is_stable() -> None:
    assert PROMOTION_EVAL_PACKAGE_CONTRACT == "sde.promotion_eval_package.v1"


def test_validate_promotion_package_dict_minimal_ok() -> None:
    body = {
        "schema_version": "1.0",
        "aggregate_id": "run-1",
        "current_stage": "junior",
        "proposed_stage": "junior",
        "independent_evaluator_signal_ids": ["eval-1"],
        "evidence_window": ["run-1"],
    }
    assert validate_promotion_package_dict(body) == []


def test_validate_promotion_package_dict_not_object() -> None:
    assert validate_promotion_package_dict([]) == ["promotion_package_not_object"]


def test_validate_promotion_package_dict_empty_signals() -> None:
    body = {
        "schema_version": "1.0",
        "aggregate_id": "r",
        "current_stage": "a",
        "proposed_stage": "b",
        "independent_evaluator_signal_ids": [],
        "evidence_window": ["r"],
    }
    assert "promotion_package_evaluator_signals" in validate_promotion_package_dict(body)


def test_validate_promotion_package_path_missing(tmp_path: Path) -> None:
    assert validate_promotion_package_path(tmp_path / "missing.json") == ["promotion_package_file_missing"]


def test_validate_promotion_package_path_bad_json(tmp_path: Path) -> None:
    p = tmp_path / "x.json"
    p.write_text("{", encoding="utf-8")
    assert validate_promotion_package_path(p) == ["promotion_package_json"]


def test_write_evolution_artifacts_writes_valid_promotion_package(tmp_path: Path) -> None:
    write_evolution_artifacts(output_dir=tmp_path, run_id="rid-99")
    pp = tmp_path / "lifecycle" / "promotion_package.json"
    assert validate_promotion_package_path(pp) == []
