"""§10.F — ``benchmark-manifest.json`` shape (benchmark aggregate harness)."""

from __future__ import annotations

import json
from pathlib import Path

from workflow_pipelines.production_pipeline_task_to_promote.benchmark.benchmark_manifest_contract import (
    BENCHMARK_MANIFEST_CONTRACT,
    validate_benchmark_manifest_dict,
    validate_benchmark_manifest_path,
)


def test_benchmark_manifest_contract_id() -> None:
    assert BENCHMARK_MANIFEST_CONTRACT == "sde.benchmark_manifest.v1"


def test_validate_benchmark_manifest_ok() -> None:
    body = {
        "schema": BENCHMARK_MANIFEST_CONTRACT,
        "run_id": "b-1",
        "suite_path": "/tmp/suite.jsonl",
        "mode": "both",
        "tasks": [{"taskId": "t1", "prompt": "p1"}],
        "max_tasks": None,
        "continue_on_error": False,
    }
    assert validate_benchmark_manifest_dict(body) == []


def test_validate_benchmark_manifest_bad_schema() -> None:
    body = {
        "schema": "x",
        "run_id": "r",
        "suite_path": "/s",
        "mode": "both",
        "tasks": [],
        "continue_on_error": True,
    }
    assert "benchmark_manifest_schema" in validate_benchmark_manifest_dict(body)


def test_validate_benchmark_manifest_bad_mode() -> None:
    body = {
        "schema": BENCHMARK_MANIFEST_CONTRACT,
        "run_id": "r",
        "suite_path": "/s",
        "mode": "phased_pipeline",
        "tasks": [{"taskId": "t", "prompt": ""}],
        "continue_on_error": False,
    }
    assert "benchmark_manifest_mode" in validate_benchmark_manifest_dict(body)


def test_validate_benchmark_manifest_missing_continue_on_error() -> None:
    body = {
        "schema": BENCHMARK_MANIFEST_CONTRACT,
        "run_id": "r",
        "suite_path": "/s",
        "mode": "baseline",
        "tasks": [],
    }
    assert "benchmark_manifest_continue_on_error" in validate_benchmark_manifest_dict(body)


def test_validate_benchmark_manifest_path_ok(tmp_path: Path) -> None:
    p = tmp_path / "benchmark-manifest.json"
    p.write_text(
        json.dumps(
            {
                "schema": BENCHMARK_MANIFEST_CONTRACT,
                "run_id": "rid",
                "suite_path": "/abs/suite.jsonl",
                "mode": "guarded_pipeline",
                "tasks": [{"taskId": "a", "prompt": "x"}],
                "max_tasks": 3,
                "continue_on_error": True,
            }
        ),
        encoding="utf-8",
    )
    assert validate_benchmark_manifest_path(p) == []
