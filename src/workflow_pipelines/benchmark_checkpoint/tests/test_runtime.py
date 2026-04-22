from __future__ import annotations

from pathlib import Path

import pytest

from workflow_pipelines.benchmark_checkpoint import (
    build_benchmark_checkpoint_runtime,
    validate_benchmark_checkpoint_runtime_path,
    validate_benchmark_checkpoint_runtime_dict,
)


def test_build_benchmark_checkpoint_runtime_deterministic() -> None:
    checkpoint = {"run_id": "bench-ck", "finished": False, "completed_task_ids": ["a"]}
    one = build_benchmark_checkpoint_runtime(checkpoint=checkpoint)
    two = build_benchmark_checkpoint_runtime(checkpoint=checkpoint)
    assert one == two
    assert one["status"] == "in_progress"
    assert validate_benchmark_checkpoint_runtime_dict(one) == []


def test_validate_benchmark_checkpoint_runtime_fail_closed() -> None:
    errs = validate_benchmark_checkpoint_runtime_dict({"schema": "bad"})
    assert "benchmark_checkpoint_runtime_schema" in errs
    assert "benchmark_checkpoint_runtime_schema_version" in errs


def test_build_benchmark_checkpoint_runtime_finished_requires_completed_tasks() -> None:
    runtime = build_benchmark_checkpoint_runtime(
        checkpoint={"run_id": "bench-ck", "finished": True, "completed_task_ids": []}
    )
    assert runtime["status"] == "in_progress"
    assert runtime["checks"]["finished"] is False


def test_validate_benchmark_checkpoint_runtime_rejects_status_checks_mismatch() -> None:
    errs = validate_benchmark_checkpoint_runtime_dict(
        {
            "schema": "sde.benchmark_checkpoint_runtime.v1",
            "schema_version": "1.0",
            "run_id": "rid",
            "status": "finished",
            "checks": {
                "checkpoint_present": True,
                "finished": False,
                "has_completed_tasks": True,
            },
        }
    )
    assert "benchmark_checkpoint_runtime_status_checks_mismatch" in errs


def test_validate_benchmark_checkpoint_runtime_rejects_checkpoint_presence_mismatch() -> None:
    errs = validate_benchmark_checkpoint_runtime_dict(
        {
            "schema": "sde.benchmark_checkpoint_runtime.v1",
            "schema_version": "1.0",
            "run_id": "rid",
            "status": "in_progress",
            "checks": {
                "checkpoint_present": False,
                "finished": True,
                "has_completed_tasks": False,
            },
        }
    )
    assert "benchmark_checkpoint_runtime_checks_mismatch" in errs


def test_build_benchmark_checkpoint_runtime_treats_truthy_non_boolean_finished_as_false() -> None:
    runtime = build_benchmark_checkpoint_runtime(
        checkpoint={"run_id": "bench-ck", "finished": "true", "completed_task_ids": ["task-1"]}
    )
    assert runtime["status"] == "in_progress"
    assert runtime["checks"]["finished"] is False


def test_validate_benchmark_checkpoint_runtime_rejects_invalid_evidence_refs() -> None:
    runtime = build_benchmark_checkpoint_runtime(
        checkpoint={"run_id": "bench-ck", "finished": True, "completed_task_ids": ["a"]}
    )
    runtime["evidence"]["benchmark_checkpoint_ref"] = "../benchmark-checkpoint.json"
    errs = validate_benchmark_checkpoint_runtime_dict(runtime)
    assert "benchmark_checkpoint_runtime_evidence_ref:benchmark_checkpoint_ref" in errs


def test_validate_benchmark_checkpoint_runtime_path_unreadable(monkeypatch: pytest.MonkeyPatch) -> None:
    def _raise_os_error(_self: Path, encoding: str = "utf-8") -> str:
        del encoding
        raise OSError("boom")

    path = Path("ignored.json")
    monkeypatch.setattr(Path, "is_file", lambda _self: True)
    monkeypatch.setattr(Path, "read_text", _raise_os_error)
    errs = validate_benchmark_checkpoint_runtime_path(path)
    assert errs == ["benchmark_checkpoint_runtime_unreadable"]
