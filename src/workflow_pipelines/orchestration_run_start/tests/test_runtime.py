from __future__ import annotations

from workflow_pipelines.orchestration_run_start import (
    build_orchestration_run_start_runtime,
    validate_orchestration_run_start_runtime_dict,
)


def test_build_orchestration_run_start_runtime_is_deterministic() -> None:
    rows = [
        {
            "run_id": "rid-start",
            "type": "run_start",
            "mode": "baseline",
            "provider": "p",
            "model": "m",
        }
    ]
    one = build_orchestration_run_start_runtime(run_id="rid-start", orchestration_rows=rows)
    two = build_orchestration_run_start_runtime(run_id="rid-start", orchestration_rows=rows)
    assert one == two
    assert one["status"] == "ready"
    assert validate_orchestration_run_start_runtime_dict(one) == []


def test_validate_orchestration_run_start_runtime_fail_closed() -> None:
    errs = validate_orchestration_run_start_runtime_dict({"schema": "bad"})
    assert "orchestration_run_start_runtime_schema" in errs
    assert "orchestration_run_start_runtime_schema_version" in errs
