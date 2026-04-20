"""§10.N — ``traces.jsonl`` row shape (``TraceEvent`` mirror)."""

from __future__ import annotations

import logging
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from core_components.orchestrator.sde_types.types import Score, TraceEvent
from workflow_pipelines.traces_jsonl.persist_traces import persist_traces
from workflow_pipelines.traces_jsonl.traces_jsonl_event_contract import (
    TRACES_JSONL_EVENT_CONTRACT,
    validate_traces_jsonl_event_dict,
)


def test_traces_jsonl_event_contract_id() -> None:
    assert TRACES_JSONL_EVENT_CONTRACT == "sde.traces_jsonl_event.v1"


def _valid_trace_dict() -> dict:
    ev = TraceEvent(
        run_id="r-1",
        task_id="t-1",
        mode="baseline",
        model="m",
        provider="p",
        stage="finalize",
        started_at="2026-01-01T00:00:00+00:00",
        ended_at="2026-01-01T00:00:01+00:00",
        latency_ms=10,
        token_input=1,
        token_output=2,
        estimated_cost_usd=0.01,
        retry_count=0,
        errors=[],
        score=Score(True, 1.0, 1.0),
        metadata=None,
    )
    return ev.to_dict()


def test_validate_traces_jsonl_event_ok_from_trace_event() -> None:
    assert validate_traces_jsonl_event_dict(_valid_trace_dict()) == []


def test_validate_traces_jsonl_event_unknown_key() -> None:
    body = dict(_valid_trace_dict())
    body["extra"] = 1
    assert "traces_jsonl_event_unknown_keys" in validate_traces_jsonl_event_dict(body)


def test_validate_traces_jsonl_event_bad_mode() -> None:
    body = dict(_valid_trace_dict())
    body["mode"] = "both"
    assert "traces_jsonl_event_mode" in validate_traces_jsonl_event_dict(body)


def test_validate_traces_jsonl_event_errors_item_not_str() -> None:
    body = dict(_valid_trace_dict())
    body["errors"] = [1]
    assert "traces_jsonl_event_errors_item:0" in validate_traces_jsonl_event_dict(body)


def test_validate_traces_jsonl_event_rejects_bool_numeric_fields() -> None:
    body = dict(_valid_trace_dict())
    body["latency_ms"] = True
    body["token_input"] = False
    body["token_output"] = True
    body["estimated_cost_usd"] = False
    body["retry_count"] = True
    body["score"] = {"passed": True, "reliability": True, "validity": False}
    errs = validate_traces_jsonl_event_dict(body)
    assert "traces_jsonl_event_latency_ms" in errs
    assert "traces_jsonl_event_token_input" in errs
    assert "traces_jsonl_event_token_output" in errs
    assert "traces_jsonl_event_estimated_cost_usd" in errs
    assert "traces_jsonl_event_retry_count" in errs
    assert "traces_jsonl_event_score_metrics" in errs


def test_persist_traces_raises_on_invalid_event() -> None:
    bad = {"run_id": ""}
    log = logging.getLogger("test_traces_jsonl_event_contract")
    with TemporaryDirectory() as td:
        out = Path(td)
        out.mkdir(exist_ok=True)
        with pytest.raises(ValueError, match="^traces_jsonl_event_contract:"):
            persist_traces(out, [bad], log)


def test_persist_traces_writes_valid_line() -> None:
    log = logging.getLogger("test_traces_jsonl_event_contract_write")
    with TemporaryDirectory() as td:
        out = Path(td)
        out.mkdir(exist_ok=True)
        persist_traces(out, [_valid_trace_dict()], log)
        text = (out / "traces.jsonl").read_text(encoding="utf-8").strip()
        assert '"run_id": "r-1"' in text
        assert '"task_id": "t-1"' in text
