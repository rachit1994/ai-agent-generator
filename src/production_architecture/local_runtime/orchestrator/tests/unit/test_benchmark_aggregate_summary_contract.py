"""§10.H — benchmark harness ``summary.json`` (aggregate success + abort failure)."""

from __future__ import annotations

import json
from pathlib import Path

from workflow_pipelines.benchmark_aggregate_summary.benchmark_aggregate_summary_contract import (
    BENCHMARK_AGGREGATE_SUMMARY_CONTRACT,
    validate_benchmark_aggregate_summary_dict,
    validate_benchmark_aggregate_summary_path,
)


def test_benchmark_aggregate_summary_contract_id() -> None:
    assert BENCHMARK_AGGREGATE_SUMMARY_CONTRACT == "sde.benchmark_aggregate_summary.v1"


def test_validate_success_summary_ok() -> None:
    body = {
        "runId": "r1",
        "suitePath": "/tmp/s.jsonl",
        "mode": "baseline",
        "verdict": "passed",
        "perTaskDeltas": [],
    }
    assert validate_benchmark_aggregate_summary_dict(body) == []


def test_validate_failure_summary_ok() -> None:
    body = {
        "runId": "r1",
        "suitePath": "/tmp/s.jsonl",
        "mode": "both",
        "runStatus": "failed",
        "error": {"type": "RuntimeError", "message": "boom"},
    }
    assert validate_benchmark_aggregate_summary_dict(body) == []


def test_validate_missing_verdict_on_success_path() -> None:
    body = {
        "runId": "r1",
        "suitePath": "/s",
        "mode": "guarded_pipeline",
        "perTaskDeltas": [],
    }
    assert "benchmark_aggregate_summary_verdict" in validate_benchmark_aggregate_summary_dict(body)


def test_validate_failure_missing_error() -> None:
    body = {
        "runId": "r1",
        "suitePath": "/s",
        "mode": "baseline",
        "runStatus": "failed",
    }
    assert "benchmark_aggregate_summary_error" in validate_benchmark_aggregate_summary_dict(body)


def test_validate_path_ok(tmp_path: Path) -> None:
    p = tmp_path / "summary.json"
    p.write_text(
        json.dumps(
            {
                "runId": "x",
                "suitePath": "/abs/s.jsonl",
                "mode": "baseline",
                "verdict": "inconclusive",
                "perTaskDeltas": [{"taskId": "t"}],
            }
        ),
        encoding="utf-8",
    )
    assert validate_benchmark_aggregate_summary_path(p) == []
