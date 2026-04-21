from __future__ import annotations

from workflow_pipelines.retry_repeat_profile import (
    build_retry_repeat_profile_runtime,
    validate_retry_repeat_profile_runtime_dict,
)


def test_build_retry_repeat_profile_runtime_is_deterministic() -> None:
    attempts = [
        {"run_id": "r1", "output_dir": "/tmp/r1", "output": "{}"},
        {"run_id": "r2", "output_dir": "/tmp/r2", "output": "{}"},
    ]
    one = build_retry_repeat_profile_runtime(
        run_id="r1",
        repeat=2,
        attempts=attempts,
        all_runs_no_pipeline_error=True,
        validation_ready_all=True,
    )
    two = build_retry_repeat_profile_runtime(
        run_id="r1",
        repeat=2,
        attempts=attempts,
        all_runs_no_pipeline_error=True,
        validation_ready_all=True,
    )
    assert one == two
    assert one["status"] == "repeat_ok"
    assert validate_retry_repeat_profile_runtime_dict(one) == []


def test_validate_retry_repeat_profile_runtime_fail_closed() -> None:
    errs = validate_retry_repeat_profile_runtime_dict({"schema": "bad"})
    assert "retry_repeat_profile_runtime_schema" in errs
    assert "retry_repeat_profile_runtime_schema_version" in errs
