"""§10.G — ``benchmark-checkpoint.json`` shape (benchmark resume progress)."""

from __future__ import annotations

import json
from pathlib import Path

from workflow_pipelines.production_pipeline_task_to_promote.benchmark.benchmark_checkpoint_contract import (
    BENCHMARK_CHECKPOINT_CONTRACT,
    validate_benchmark_checkpoint_dict,
    validate_benchmark_checkpoint_path,
)


def test_benchmark_checkpoint_contract_id() -> None:
    assert BENCHMARK_CHECKPOINT_CONTRACT == "sde.benchmark_checkpoint.v1"


def test_validate_benchmark_checkpoint_ok() -> None:
    body = {
        "schema": BENCHMARK_CHECKPOINT_CONTRACT,
        "run_id": "r1",
        "suite_path": "/tmp/s.jsonl",
        "mode": "both",
        "max_tasks": 2,
        "continue_on_error": True,
        "completed_task_ids": ["a", "b"],
        "finished": False,
        "updated_at_ms": 123,
    }
    assert validate_benchmark_checkpoint_dict(body) == []


def test_validate_benchmark_checkpoint_bad_schema() -> None:
    body = {
        "schema": "x",
        "run_id": "r",
        "suite_path": "/s",
        "mode": "baseline",
        "max_tasks": None,
        "continue_on_error": False,
        "completed_task_ids": [],
        "finished": True,
        "updated_at_ms": 0,
    }
    assert "benchmark_checkpoint_schema" in validate_benchmark_checkpoint_dict(body)


def test_validate_benchmark_checkpoint_blank_completed_id() -> None:
    body = {
        "schema": BENCHMARK_CHECKPOINT_CONTRACT,
        "run_id": "r",
        "suite_path": "/s",
        "mode": "baseline",
        "max_tasks": None,
        "continue_on_error": False,
        "completed_task_ids": ["ok", ""],
        "finished": False,
        "updated_at_ms": 1,
    }
    assert "benchmark_checkpoint_completed_task_id:1" in validate_benchmark_checkpoint_dict(body)


def test_validate_benchmark_checkpoint_path_ok(tmp_path: Path) -> None:
    p = tmp_path / "benchmark-checkpoint.json"
    p.write_text(
        json.dumps(
            {
                "schema": BENCHMARK_CHECKPOINT_CONTRACT,
                "run_id": "rid",
                "suite_path": "/abs/s.jsonl",
                "mode": "guarded_pipeline",
                "continue_on_error": False,
                "completed_task_ids": [],
                "finished": True,
                "updated_at_ms": 0,
            }
        ),
        encoding="utf-8",
    )
    assert validate_benchmark_checkpoint_path(p) == []
