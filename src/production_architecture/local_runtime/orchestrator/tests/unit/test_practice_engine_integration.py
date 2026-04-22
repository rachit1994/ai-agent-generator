from __future__ import annotations

import json
from pathlib import Path

from core_components.practice_engine import validate_practice_engine_path
from production_architecture.storage.storage.storage import ensure_dir, write_json
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.practice_engine_layer import (
    write_practice_engine_artifact,
)


def test_write_practice_engine_artifact_and_validate(tmp_path: Path) -> None:
    run_id = "run-practice-engine"
    output_dir = tmp_path / "runs" / run_id
    ensure_dir(output_dir / "practice")
    ensure_dir(output_dir / "learning")
    write_json(output_dir / "practice" / "task_spec.json", {"task": "deliberate_practice_cycle"})
    write_json(output_dir / "practice" / "evaluation_result.json", {"passed": False})
    write_json(output_dir / "learning" / "reflection_bundle.json", {"root_causes": ["a", "b"]})
    write_json(output_dir / "review.json", {"status": "completed_review_pass"})
    payload = write_practice_engine_artifact(output_dir=output_dir, run_id=run_id)
    assert payload["run_id"] == run_id
    assert validate_practice_engine_path(output_dir / "practice" / "practice_engine.json") == []
    body = json.loads((output_dir / "practice" / "practice_engine.json").read_text(encoding="utf-8"))
    assert body["run_id"] == run_id


def test_write_practice_engine_artifact_fails_closed_without_review_pass(
    tmp_path: Path,
) -> None:
    run_id = "run-practice-engine-no-review-pass"
    output_dir = tmp_path / "runs" / run_id
    ensure_dir(output_dir / "practice")
    ensure_dir(output_dir / "learning")
    write_json(output_dir / "practice" / "task_spec.json", {"task": "deliberate_practice_cycle"})
    write_json(output_dir / "practice" / "evaluation_result.json", {"passed": True})
    write_json(output_dir / "learning" / "reflection_bundle.json", {"root_causes": []})
    payload = write_practice_engine_artifact(output_dir=output_dir, run_id=run_id)
    assert payload["status"] != "ready"
    assert payload["result"]["passed"] is False


def test_validate_practice_engine_path_rejects_status_scores_mismatch(tmp_path: Path) -> None:
    run_id = "run-practice-engine-status-mismatch"
    output_dir = tmp_path / "runs" / run_id
    ensure_dir(output_dir / "practice")
    path = output_dir / "practice" / "practice_engine.json"
    path.write_text(
        json.dumps(
            {
                "schema": "sde.practice_engine.v1",
                "schema_version": "1.0",
                "run_id": run_id,
                "status": "ready",
                "scores": {
                    "gap_severity": 0.5,
                    "readiness_signal": 0.4,
                    "expected_improvement": 0.3,
                },
                "plan": {
                    "task": "deliberate_practice_cycle",
                    "focus_area": "delivery.structured_output",
                    "acceptance_criteria": ["focus:delivery.structured_output"],
                },
                "result": {"passed": True},
                "evidence": {
                    "task_spec_ref": "practice/task_spec.json",
                    "evaluation_result_ref": "practice/evaluation_result.json",
                    "practice_engine_ref": "practice/practice_engine.json",
                },
            }
        ),
        encoding="utf-8",
    )
    errs = validate_practice_engine_path(path)
    assert "practice_engine_status_scores_mismatch" in errs


def test_write_practice_engine_artifact_fail_closes_malformed_upstream_json(tmp_path: Path) -> None:
    run_id = "run-practice-engine-malformed-upstream"
    output_dir = tmp_path / "runs" / run_id
    ensure_dir(output_dir / "practice")
    ensure_dir(output_dir / "learning")
    (output_dir / "practice" / "task_spec.json").write_text("{bad", encoding="utf-8")
    (output_dir / "practice" / "evaluation_result.json").write_text("{bad", encoding="utf-8")
    (output_dir / "learning" / "reflection_bundle.json").write_text("{bad", encoding="utf-8")
    (output_dir / "review.json").write_text("{bad", encoding="utf-8")
    payload = write_practice_engine_artifact(output_dir=output_dir, run_id=run_id)
    assert payload["result"]["passed"] is False

