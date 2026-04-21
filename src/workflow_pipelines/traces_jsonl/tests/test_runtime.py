from __future__ import annotations

from workflow_pipelines.traces_jsonl import (
    build_traces_jsonl_event_row_runtime,
    validate_traces_jsonl_event_row_runtime_dict,
)


def test_build_traces_jsonl_event_row_runtime_deterministic() -> None:
    rows = [
        {
            "run_id": "rid-trace",
            "task_id": "t-1",
            "mode": "baseline",
            "model": "m",
            "provider": "p",
            "stage": "finalize",
            "started_at": "a",
            "ended_at": "b",
            "latency_ms": 1,
            "token_input": 0,
            "token_output": 0,
            "estimated_cost_usd": 0.0,
            "retry_count": 0,
            "errors": [],
            "score": {"passed": True, "reliability": 1.0, "validity": 1.0},
            "metadata": None,
        }
    ]
    one = build_traces_jsonl_event_row_runtime(run_id="rid-trace", trace_rows=rows)
    two = build_traces_jsonl_event_row_runtime(run_id="rid-trace", trace_rows=rows)
    assert one == two
    assert one["status"] == "ready"
    assert validate_traces_jsonl_event_row_runtime_dict(one) == []


def test_validate_traces_jsonl_event_row_runtime_fail_closed() -> None:
    errs = validate_traces_jsonl_event_row_runtime_dict({"schema": "bad"})
    assert "traces_jsonl_event_row_runtime_schema" in errs
    assert "traces_jsonl_event_row_runtime_schema_version" in errs


def test_validate_traces_jsonl_event_row_runtime_rejects_status_checks_mismatch() -> None:
    payload = {
        "schema": "sde.traces_jsonl_event_row_runtime.v1",
        "schema_version": "1.0",
        "run_id": "rid-trace",
        "status": "ready",
        "checks": {"all_rows_valid": True, "run_id_consistent": False},
        "counts": {"row_count": 1},
        "evidence": {
            "traces_ref": "traces.jsonl",
            "runtime_ref": "traces/event_row_runtime.json",
        },
    }
    errs = validate_traces_jsonl_event_row_runtime_dict(payload)
    assert "traces_jsonl_event_row_runtime_status_checks_mismatch" in errs


def test_validate_traces_jsonl_event_row_runtime_rejects_missing_counts() -> None:
    payload = {
        "schema": "sde.traces_jsonl_event_row_runtime.v1",
        "schema_version": "1.0",
        "run_id": "rid-trace",
        "status": "degraded",
        "checks": {"all_rows_valid": False, "run_id_consistent": False},
    }
    errs = validate_traces_jsonl_event_row_runtime_dict(payload)
    assert "traces_jsonl_event_row_runtime_counts" in errs


def test_validate_traces_jsonl_event_row_runtime_rejects_ready_with_zero_rows() -> None:
    payload = {
        "schema": "sde.traces_jsonl_event_row_runtime.v1",
        "schema_version": "1.0",
        "run_id": "rid-trace",
        "status": "ready",
        "checks": {"all_rows_valid": True, "run_id_consistent": True},
        "counts": {"row_count": 0},
        "evidence": {
            "traces_ref": "traces.jsonl",
            "runtime_ref": "traces/event_row_runtime.json",
        },
    }
    errs = validate_traces_jsonl_event_row_runtime_dict(payload)
    assert "traces_jsonl_event_row_runtime_status_counts_mismatch" in errs


def test_build_traces_jsonl_event_row_runtime_degraded_with_zero_rows() -> None:
    payload = build_traces_jsonl_event_row_runtime(run_id="rid-trace", trace_rows=[])
    assert payload["status"] == "degraded"
    assert payload["checks"]["all_rows_valid"] is False
    assert payload["checks"]["run_id_consistent"] is False
    assert validate_traces_jsonl_event_row_runtime_dict(payload) == []
