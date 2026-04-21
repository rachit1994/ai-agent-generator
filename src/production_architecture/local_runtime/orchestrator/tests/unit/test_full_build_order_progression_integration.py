from __future__ import annotations

import json
from pathlib import Path

from scalability_strategy.full_build_order_progression import validate_full_build_order_progression_path
from production_architecture.storage.storage.storage import ensure_dir
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.full_build_order_progression_layer import (
    write_full_build_order_progression_artifact,
)


def test_write_full_build_order_progression_artifact_and_validate(tmp_path: Path) -> None:
    run_id = "run-fbop"
    output_dir = tmp_path / "runs" / run_id
    ensure_dir(output_dir)
    (output_dir / "orchestration.jsonl").write_text(
        '{"type":"stage_event","stage":"planner_doc"}\n'
        '{"type":"stage_event","stage":"planner_prompt"}\n'
        '{"type":"stage_event","stage":"executor"}\n'
        '{"type":"stage_event","stage":"finalize"}\n',
        encoding="utf-8",
    )
    payload = write_full_build_order_progression_artifact(
        output_dir=output_dir, run_id=run_id, mode="guarded_pipeline"
    )
    assert payload["run_id"] == run_id
    assert (
        validate_full_build_order_progression_path(
            output_dir / "strategy" / "full_build_order_progression.json"
        )
        == []
    )
    body = json.loads(
        (output_dir / "strategy" / "full_build_order_progression.json").read_text(encoding="utf-8")
    )
    assert body["run_id"] == run_id


def test_write_full_build_order_progression_marks_out_of_order_for_unknown_stage(
    tmp_path: Path,
) -> None:
    run_id = "run-fbop-unknown-stage"
    output_dir = tmp_path / "runs" / run_id
    ensure_dir(output_dir)
    (output_dir / "orchestration.jsonl").write_text(
        '{"type":"stage_event","stage":"planner_doc"}\n'
        '{"type":"stage_event","stage":"weird_stage"}\n'
        '{"type":"stage_event","stage":"finalize"}\n',
        encoding="utf-8",
    )
    payload = write_full_build_order_progression_artifact(
        output_dir=output_dir,
        run_id=run_id,
        mode="guarded_pipeline",
    )
    assert payload["status"] == "out_of_order"
    assert payload["checks"]["all_stages_known"] is False
    assert validate_full_build_order_progression_path(
        output_dir / "strategy" / "full_build_order_progression.json"
    ) == []


def test_validate_full_build_order_progression_path_rejects_summary_sequence_mismatch(
    tmp_path: Path,
) -> None:
    run_id = "run-fbop-summary-mismatch"
    output_dir = tmp_path / "runs" / run_id
    ensure_dir(output_dir / "strategy")
    path = output_dir / "strategy" / "full_build_order_progression.json"
    path.write_text(
        json.dumps(
            {
                "schema": "sde.full_build_order_progression.v1",
                "schema_version": "1.0",
                "run_id": run_id,
                "mode": "guarded_pipeline",
                "status": "ordered",
                "stage_sequence": ["planner_doc", "planner_prompt", "executor", "finalize"],
                "expected_order": [
                    "planner_doc",
                    "planner_prompt",
                    "executor",
                    "verifier",
                    "executor_fix",
                    "verifier_fix",
                    "repair",
                    "finalize",
                ],
                "checks": {
                    "all_stages_known": True,
                    "starts_with_allowed_entry_stage": True,
                    "ends_with_finalize": True,
                    "monotonic_progression": True,
                    "required_stages_present": True,
                },
                "summary": {
                    "observed_stage_count": 4,
                    "distinct_stage_count": 4,
                    "required_stage_count": 4,
                    "required_stage_present_count": 0,
                    "order_score": 1.0,
                },
            }
        ),
        encoding="utf-8",
    )
    errs = validate_full_build_order_progression_path(path)
    assert "full_build_order_progression_summary_sequence_mismatch" in errs

