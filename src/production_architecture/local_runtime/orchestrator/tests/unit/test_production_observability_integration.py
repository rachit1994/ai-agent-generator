from __future__ import annotations

from pathlib import Path

from production_architecture.observability import validate_production_observability_path
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.observability_layer import (
    write_production_observability_artifact,
)


def test_production_observability_written_and_valid(tmp_path: Path) -> None:
    run_id = "run-production-observability"
    run_dir = tmp_path / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "traces.jsonl").write_text('{"stage":"finalize"}\n', encoding="utf-8")
    (run_dir / "orchestration.jsonl").write_text('{"type":"run_start"}\n', encoding="utf-8")
    (run_dir / "run.log").write_text("run log line\n", encoding="utf-8")
    payload = write_production_observability_artifact(
        output_dir=run_dir,
        run_id=run_id,
        mode="guarded_pipeline",
    )
    assert payload["run_id"] == run_id
    path = run_dir / "observability" / "production_observability.json"
    assert validate_production_observability_path(path) == []
