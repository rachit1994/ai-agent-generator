from __future__ import annotations

from workflow_pipelines.orchestration_stage_event import (
    build_orchestration_stage_event_runtime,
    validate_orchestration_stage_event_runtime_dict,
)


def test_build_orchestration_stage_event_runtime_is_deterministic() -> None:
    rows = [
        {
            "run_id": "rid-stage",
            "type": "stage_event",
            "stage": "executor",
            "retry_count": 0,
            "errors": [],
            "agent": None,
            "model": None,
            "model_error": None,
            "attempt": None,
            "raw_response_excerpt": None,
            "started_at": "a",
            "ended_at": "b",
            "latency_ms": 1,
        }
    ]
    one = build_orchestration_stage_event_runtime(run_id="rid-stage", orchestration_rows=rows)
    two = build_orchestration_stage_event_runtime(run_id="rid-stage", orchestration_rows=rows)
    assert one == two
    assert one["status"] == "ready"
    assert validate_orchestration_stage_event_runtime_dict(one) == []


def test_validate_orchestration_stage_event_runtime_fail_closed() -> None:
    errs = validate_orchestration_stage_event_runtime_dict({"schema": "bad"})
    assert "orchestration_stage_event_runtime_schema" in errs
    assert "orchestration_stage_event_runtime_schema_version" in errs
