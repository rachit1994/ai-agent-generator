from __future__ import annotations

from workflow_pipelines.orchestration_run_end import (
    build_orchestration_run_end_runtime,
    validate_orchestration_run_end_runtime_dict,
)


def test_build_orchestration_run_end_runtime_deterministic() -> None:
    rows = [
        {"run_id": "r-1", "type": "run_start", "mode": "baseline"},
        {
            "run_id": "r-1",
            "type": "run_end",
            "artifacts": {"answer_txt": "/tmp/a"},
            "output_refusal": None,
            "checks": [{"name": "x", "passed": True}],
        },
    ]
    one = build_orchestration_run_end_runtime(run_id="r-1", orchestration_rows=rows)
    two = build_orchestration_run_end_runtime(run_id="r-1", orchestration_rows=rows)
    assert one == two
    assert one["status"] == "ready"
    assert validate_orchestration_run_end_runtime_dict(one) == []


def test_validate_orchestration_run_end_runtime_fail_closed() -> None:
    errs = validate_orchestration_run_end_runtime_dict({"schema": "bad"})
    assert "orchestration_run_end_runtime_schema" in errs
    assert "orchestration_run_end_runtime_schema_version" in errs
