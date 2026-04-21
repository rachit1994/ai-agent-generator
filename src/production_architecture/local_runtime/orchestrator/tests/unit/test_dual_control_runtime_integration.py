from __future__ import annotations

import json
from pathlib import Path

from guardrails_and_safety.dual_control import validate_dual_control_path
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.completion_layer import (
    write_completion_artifacts,
)
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.dual_control_layer import (
    write_dual_control_artifact,
)


def test_dual_control_runtime_written_and_valid(tmp_path: Path) -> None:
    run_id = "run-dual-control"
    run_dir = tmp_path / "runs" / run_id
    write_completion_artifacts(
        output_dir=run_dir,
        run_id=run_id,
        task="dual control validation",
        parsed={},
        events=[],
    )
    payload = write_dual_control_artifact(output_dir=run_dir, run_id=run_id)
    assert payload["run_id"] == run_id
    assert validate_dual_control_path(run_dir / "program" / "dual_control_runtime.json") == []


def test_dual_control_runtime_marks_invalid_ack_for_bad_acknowledged_at_shape(tmp_path: Path) -> None:
    run_id = "run-dual-control-bad-ts"
    run_dir = tmp_path / "runs" / run_id
    write_completion_artifacts(
        output_dir=run_dir,
        run_id=run_id,
        task="dual control validation",
        parsed={},
        events=[],
    )
    (run_dir / "program" / "doc_review.json").write_text(
        json.dumps({"passed": True, "dual_control": {"required": True}}),
        encoding="utf-8",
    )
    (run_dir / "program" / "dual_control_ack.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "implementor_actor_id": "alice",
                "independent_reviewer_actor_id": "bob",
                "acknowledged_at": "2026-01-01 00:00:00",
            }
        ),
        encoding="utf-8",
    )
    payload = write_dual_control_artifact(output_dir=run_dir, run_id=run_id)
    assert payload["status"] == "invalid_ack"
    assert validate_dual_control_path(run_dir / "program" / "dual_control_runtime.json") == []


def test_validate_dual_control_path_rejects_validated_when_required_ack_missing(tmp_path: Path) -> None:
    run_id = "run-dual-control-status-mismatch"
    run_dir = tmp_path / "runs" / run_id
    (run_dir / "program").mkdir(parents=True, exist_ok=True)
    path = run_dir / "program" / "dual_control_runtime.json"
    path.write_text(
        json.dumps(
            {
                "schema": "sde.dual_control.v1",
                "schema_version": "1.0",
                "run_id": run_id,
                "status": "validated",
                "metrics": {
                    "doc_review_passed": True,
                    "dual_required": True,
                    "ack_present": False,
                    "ack_valid": False,
                    "distinct_actors": False,
                },
                "evidence": {
                    "doc_review_ref": "program/doc_review.json",
                    "dual_control_ack_ref": "program/dual_control_ack.json",
                    "dual_control_runtime_ref": "program/dual_control_runtime.json",
                },
            }
        ),
        encoding="utf-8",
    )
    errs = validate_dual_control_path(path)
    assert "dual_control_semantics" in errs
