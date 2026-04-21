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


def test_validate_production_observability_path_rejects_status_metrics_mismatch(
    tmp_path: Path,
) -> None:
    run_id = "run-production-observability-mismatch"
    run_dir = tmp_path / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "observability").mkdir(parents=True, exist_ok=True)
    (run_dir / "observability" / "production_observability.json").write_text(
        '{"schema":"sde.production_observability.v1","schema_version":"1.0","run_id":"rid","mode":"baseline","status":"missing","metrics":{"trace_rows":1,"orchestration_rows":1,"run_log_lines":1},"evidence":{"traces_ref":"traces.jsonl","orchestration_ref":"orchestration.jsonl","run_log_ref":"run.log","observability_ref":"observability/production_observability.json"}}',
        encoding="utf-8",
    )
    errs = validate_production_observability_path(
        run_dir / "observability" / "production_observability.json"
    )
    assert "production_observability_status_metrics_mismatch" in errs


def test_validate_production_observability_path_rejects_missing_evidence_ref(
    tmp_path: Path,
) -> None:
    run_id = "run-production-observability-bad-evidence"
    run_dir = tmp_path / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "observability").mkdir(parents=True, exist_ok=True)
    (run_dir / "observability" / "production_observability.json").write_text(
        '{"schema":"sde.production_observability.v1","schema_version":"1.0","run_id":"rid","mode":"baseline","status":"healthy","metrics":{"trace_rows":1,"orchestration_rows":1,"run_log_lines":1},"evidence":{"traces_ref":"traces.jsonl","orchestration_ref":"orchestration.jsonl","run_log_ref":"","observability_ref":"observability/production_observability.json"}}',
        encoding="utf-8",
    )
    errs = validate_production_observability_path(
        run_dir / "observability" / "production_observability.json"
    )
    assert "production_observability_evidence_ref:run_log_ref" in errs


def test_validate_production_observability_path_rejects_non_canonical_evidence_ref(
    tmp_path: Path,
) -> None:
    run_id = "run-production-observability-non-canonical-evidence"
    run_dir = tmp_path / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "observability").mkdir(parents=True, exist_ok=True)
    (run_dir / "observability" / "production_observability.json").write_text(
        '{"schema":"sde.production_observability.v1","schema_version":"1.0","run_id":"rid","mode":"baseline","status":"healthy","metrics":{"trace_rows":1,"orchestration_rows":1,"run_log_lines":1},"evidence":{"traces_ref":"traces.jsonl","orchestration_ref":"orchestration-events.jsonl","run_log_ref":"run.log","observability_ref":"observability/production_observability.json"}}',
        encoding="utf-8",
    )
    errs = validate_production_observability_path(
        run_dir / "observability" / "production_observability.json"
    )
    assert "production_observability_evidence_ref_mismatch:orchestration_ref" in errs
