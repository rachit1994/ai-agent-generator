"""§10.K — flattened ``stage_event`` line for ``orchestration.jsonl``."""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

from workflow_pipelines.production_pipeline_task_to_promote.runner.orchestration_stage_event_contract import (
    ORCHESTRATION_STAGE_EVENT_CONTRACT,
    validate_orchestration_stage_event_line_dict,
)
from workflow_pipelines.production_pipeline_task_to_promote.runner.persist_traces import (
    append_orchestration_stage_events,
)


def test_orchestration_stage_event_contract_id() -> None:
    assert ORCHESTRATION_STAGE_EVENT_CONTRACT == "sde.orchestration_stage_event.v1"


def test_validate_stage_event_line_ok_minimal() -> None:
    body = {
        "run_id": "r-1",
        "type": "stage_event",
        "stage": "executor",
        "retry_count": 0,
        "errors": [],
        "agent": None,
        "model": None,
        "model_error": None,
        "attempt": None,
        "raw_response_excerpt": None,
        "started_at": "2026-01-01T00:00:00+00:00",
        "ended_at": "2026-01-01T00:00:01+00:00",
        "latency_ms": 1000,
    }
    assert validate_orchestration_stage_event_line_dict(body) == []


def test_validate_stage_event_line_bad_errors_type() -> None:
    body = {
        "run_id": "r",
        "type": "stage_event",
        "stage": "x",
        "retry_count": 0,
        "errors": "nope",
        "started_at": "a",
        "ended_at": "b",
        "latency_ms": 0,
    }
    assert "orchestration_stage_event_errors" in validate_orchestration_stage_event_line_dict(body)


def test_validate_stage_event_line_bad_latency() -> None:
    body = {
        "run_id": "r",
        "type": "stage_event",
        "stage": "x",
        "retry_count": 0,
        "errors": [],
        "started_at": "a",
        "ended_at": "b",
        "latency_ms": -1,
    }
    assert "orchestration_stage_event_latency_ms" in validate_orchestration_stage_event_line_dict(body)


def test_append_orchestration_stage_events_writes_lines() -> None:
    trace = {
        "stage": "finalize",
        "retry_count": 0,
        "errors": [],
        "started_at": "2026-01-01T00:00:00+00:00",
        "ended_at": "2026-01-01T00:00:05+00:00",
        "latency_ms": 5000,
        "metadata": {"attempt": 0, "agent": {"name": "t", "type": "llm", "role": "finalize"}},
    }
    with TemporaryDirectory() as td:
        path = Path(td) / "orchestration.jsonl"
        append_orchestration_stage_events(path, "run-z", [trace])
        text = path.read_text(encoding="utf-8").strip()
        assert '"type": "stage_event"' in text
        assert "run-z" in text
