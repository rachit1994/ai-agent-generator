from __future__ import annotations

from pathlib import Path

from production_architecture.storage.storage.storage import ensure_dir
from workflow_pipelines.orchestration_run_end import validate_orchestration_run_end_runtime_path
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.orchestration_run_end_layer import (
    write_orchestration_run_end_runtime_artifact,
)


def test_orchestration_run_end_runtime_written_and_valid(tmp_path: Path) -> None:
    run_id = "run-end-runtime"
    run_dir = tmp_path / "runs" / run_id
    ensure_dir(run_dir)
    (run_dir / "orchestration.jsonl").write_text(
        '{"run_id":"run-end-runtime","type":"run_end","artifacts":{"answer_txt":"/tmp/answer.txt"},"output_refusal":null,"checks":[]}\n',
        encoding="utf-8",
    )
    payload = write_orchestration_run_end_runtime_artifact(output_dir=run_dir, run_id=run_id)
    assert payload["run_id"] == run_id
    assert payload["status"] == "ready"
    assert validate_orchestration_run_end_runtime_path(
        run_dir / "orchestration" / "run_end_runtime.json"
    ) == []
