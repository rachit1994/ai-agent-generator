from __future__ import annotations

import json
from pathlib import Path

import pytest

from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.dual_control_layer import (
    write_dual_control_artifact,
)


def _write_json(path: Path, body: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(body), encoding="utf-8")


def test_runner_layer_writes_valid_dual_control_runtime(tmp_path: Path) -> None:
    output_dir = tmp_path / "run"
    _write_json(output_dir / "program" / "doc_review.json", {"passed": True, "dual_control": {"required": False}})
    _write_json(
        output_dir / "program" / "dual_control_ack.json",
        {
            "schema_version": "1.0",
            "implementor_actor_id": "alice",
            "independent_reviewer_actor_id": "bob",
            "acknowledged_at": "2026-01-01T00:00:00Z",
        },
    )
    payload = write_dual_control_artifact(output_dir=output_dir, run_id="rid-layer")
    assert payload["status"] == "validated"
    first = (output_dir / "program" / "dual_control_runtime.json").read_text(encoding="utf-8")
    payload_two = write_dual_control_artifact(output_dir=output_dir, run_id="rid-layer")
    second = (output_dir / "program" / "dual_control_runtime.json").read_text(encoding="utf-8")
    assert payload_two == payload
    assert second == first


def test_runner_layer_raises_for_invalid_doc_review_json(tmp_path: Path) -> None:
    output_dir = tmp_path / "run"
    bad_path = output_dir / "program" / "doc_review.json"
    bad_path.parent.mkdir(parents=True, exist_ok=True)
    bad_path.write_text("{bad", encoding="utf-8")
    with pytest.raises(ValueError, match="dual_control_contract:dual_control_json:doc_review.json"):
        write_dual_control_artifact(output_dir=output_dir, run_id="rid-layer")


def test_runner_layer_raises_for_non_object_ack_json(tmp_path: Path) -> None:
    output_dir = tmp_path / "run"
    _write_json(output_dir / "program" / "doc_review.json", {"passed": True})
    ack_path = output_dir / "program" / "dual_control_ack.json"
    ack_path.parent.mkdir(parents=True, exist_ok=True)
    ack_path.write_text(json.dumps(["bad"]), encoding="utf-8")
    with pytest.raises(ValueError, match="dual_control_contract:dual_control_not_object:dual_control_ack.json"):
        write_dual_control_artifact(output_dir=output_dir, run_id="rid-layer")


def test_runner_layer_raises_for_invalid_ack_json(tmp_path: Path) -> None:
    output_dir = tmp_path / "run"
    _write_json(output_dir / "program" / "doc_review.json", {"passed": True})
    ack_path = output_dir / "program" / "dual_control_ack.json"
    ack_path.parent.mkdir(parents=True, exist_ok=True)
    ack_path.write_text("{bad", encoding="utf-8")
    with pytest.raises(ValueError, match="dual_control_contract:dual_control_json:dual_control_ack.json"):
        write_dual_control_artifact(output_dir=output_dir, run_id="rid-layer")
