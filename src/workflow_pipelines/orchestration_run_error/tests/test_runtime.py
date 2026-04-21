from __future__ import annotations

from workflow_pipelines.orchestration_run_error import (
    build_orchestration_run_error_runtime,
    validate_orchestration_run_error_runtime_dict,
)


def test_build_orchestration_run_error_runtime_is_deterministic() -> None:
    rows = [
        {
            "run_id": "rid-error",
            "type": "run_error",
            "mode": "baseline",
            "error_type": "RuntimeError",
            "error_message": "x",
        }
    ]
    one = build_orchestration_run_error_runtime(run_id="rid-error", orchestration_rows=rows)
    two = build_orchestration_run_error_runtime(run_id="rid-error", orchestration_rows=rows)
    assert one == two
    assert one["status"] == "has_error"
    assert validate_orchestration_run_error_runtime_dict(one) == []


def test_validate_orchestration_run_error_runtime_fail_closed() -> None:
    errs = validate_orchestration_run_error_runtime_dict({"schema": "bad"})
    assert "orchestration_run_error_runtime_schema" in errs
    assert "orchestration_run_error_runtime_schema_version" in errs
