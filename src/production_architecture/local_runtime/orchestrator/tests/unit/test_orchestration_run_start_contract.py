"""§10.I — ``orchestration.jsonl`` first ``run_start`` line shape."""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

from workflow_pipelines.orchestration_run_start.orchestration_run_start_contract import (
    ORCHESTRATION_RUN_START_CONTRACT,
    validate_orchestration_run_start_dict,
)
from workflow_pipelines.traces_jsonl.persist_traces import (
    append_orchestration_run_start,
)


def test_orchestration_run_start_contract_id() -> None:
    assert ORCHESTRATION_RUN_START_CONTRACT == "sde.orchestration_run_start.v1"


def test_validate_orchestration_run_start_ok() -> None:
    body = {
        "run_id": "r-1",
        "type": "run_start",
        "mode": "baseline",
        "provider": "ollama",
        "model": "qwen3:14b",
    }
    assert validate_orchestration_run_start_dict(body) == []


def test_validate_orchestration_run_start_bad_mode() -> None:
    body = {
        "run_id": "r",
        "type": "run_start",
        "mode": "both",
        "provider": "p",
        "model": "m",
    }
    assert "orchestration_run_start_mode" in validate_orchestration_run_start_dict(body)


def test_validate_orchestration_run_start_bad_type() -> None:
    body = {
        "run_id": "r",
        "type": "stage_event",
        "mode": "baseline",
        "provider": "p",
        "model": "m",
    }
    assert "orchestration_run_start_type" in validate_orchestration_run_start_dict(body)


def test_validate_orchestration_run_start_rejects_unknown_keys() -> None:
    body = {
        "run_id": "r-1",
        "type": "run_start",
        "mode": "baseline",
        "provider": "ollama",
        "model": "qwen3:14b",
        "extra": True,
    }
    assert "orchestration_run_start_unknown_key:extra" in validate_orchestration_run_start_dict(body)


def test_append_orchestration_run_start_writes_valid_line() -> None:
    with TemporaryDirectory() as td:
        path = Path(td) / "orchestration.jsonl"
        append_orchestration_run_start(path, "run-x", "guarded_pipeline")
        text = path.read_text(encoding="utf-8").strip()
        assert '"type": "run_start"' in text
        assert "run-x" in text
