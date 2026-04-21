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

