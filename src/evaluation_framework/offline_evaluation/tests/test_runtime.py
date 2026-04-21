from __future__ import annotations

from evaluation_framework.offline_evaluation import (
    build_offline_evaluation_runtime,
    validate_offline_evaluation_runtime_dict,
)


def test_build_offline_evaluation_runtime_deterministic() -> None:
    one = build_offline_evaluation_runtime(
        run_id="rid-offline",
        suite_errors=[],
        traces_present=True,
        summary_present=True,
        checkpoint_finished=True,
    )
    two = build_offline_evaluation_runtime(
        run_id="rid-offline",
        suite_errors=[],
        traces_present=True,
        summary_present=True,
        checkpoint_finished=True,
    )
    assert one == two
    assert one["status"] == "ready"
    assert validate_offline_evaluation_runtime_dict(one) == []


def test_validate_offline_evaluation_runtime_fail_closed() -> None:
    errs = validate_offline_evaluation_runtime_dict({"schema": "bad"})
    assert "offline_evaluation_runtime_schema" in errs
    assert "offline_evaluation_runtime_schema_version" in errs
