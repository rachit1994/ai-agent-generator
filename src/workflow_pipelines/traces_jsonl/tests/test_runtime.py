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
