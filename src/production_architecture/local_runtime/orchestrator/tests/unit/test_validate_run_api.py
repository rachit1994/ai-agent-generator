from __future__ import annotations

import json
from pathlib import Path

import importlib

import pytest

from orchestrator.api import validate_run

_validate_run_module = importlib.import_module("orchestrator.api.validate_run")


def test_validate_run_missing_directory(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(_validate_run_module, "outputs_base", lambda: tmp_path)
    result = validate_run("nonexistent-run-id")
    assert result["ok"] is False
    assert "run_directory_missing" in result["errors"][0]


def test_validate_run_reads_mode_from_manifest(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(_validate_run_module, "outputs_base", lambda: tmp_path)
    run_dir = tmp_path / "runs" / "run-xyz"
    run_dir.mkdir(parents=True)
    (run_dir / "run-manifest.json").write_text(
        json.dumps({"schema": "sde.run_manifest.v1", "run_id": "run-xyz", "mode": "guarded_pipeline", "task": "t"}),
        encoding="utf-8",
    )
    result = validate_run("run-xyz", mode=None)
    assert "errors" in result
    assert isinstance(result.get("hard_stops"), list)


def test_validate_run_invalid_mode_from_manifest(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(_validate_run_module, "outputs_base", lambda: tmp_path)
    run_dir = tmp_path / "runs" / "run-bad"
    run_dir.mkdir(parents=True)
    (run_dir / "run-manifest.json").write_text(
        json.dumps({"schema": "sde.run_manifest.v1", "run_id": "run-bad", "mode": "weird", "task": "t"}),
        encoding="utf-8",
    )
    result = validate_run("run-bad", mode=None)
    assert result["ok"] is False
    assert result["validation_ready"] is False
    assert result["errors"] == ["invalid_mode_in_manifest:weird"]


def test_validate_run_reads_mode_from_benchmark_manifest(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(_validate_run_module, "outputs_base", lambda: tmp_path)
    run_dir = tmp_path / "runs" / "bench-xyz"
    run_dir.mkdir(parents=True)
    (run_dir / "benchmark-manifest.json").write_text(
        json.dumps({"schema": "sde.benchmark_manifest.v1", "run_id": "bench-xyz", "mode": "guarded_pipeline"}),
        encoding="utf-8",
    )
    result = validate_run("bench-xyz", mode=None)
    assert result.get("run_kind") == "benchmark_aggregate"
    assert result.get("execution_gates_applied") is False
    assert result["ok"] is False
    assert "missing_benchmark_checkpoint_json" in result["errors"]
    assert isinstance(result.get("hard_stops"), list)


def test_validate_run_benchmark_aggregate_ok(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(_validate_run_module, "outputs_base", lambda: tmp_path)
    run_dir = tmp_path / "runs" / "bench-complete"
    run_dir.mkdir(parents=True)
    (run_dir / "benchmark-manifest.json").write_text(
        json.dumps(
            {
                "schema": "sde.benchmark_manifest.v1",
                "run_id": "bench-complete",
                "suite_path": "/tmp/suite.jsonl",
                "mode": "baseline",
                "tasks": [],
                "max_tasks": None,
                "continue_on_error": False,
            }
        ),
        encoding="utf-8",
    )
    (run_dir / "benchmark-checkpoint.json").write_text(
        json.dumps(
            {
                "schema": "sde.benchmark_checkpoint.v1",
                "run_id": "bench-complete",
                "suite_path": "/tmp/suite.jsonl",
                "mode": "baseline",
                "max_tasks": None,
                "continue_on_error": False,
                "completed_task_ids": [],
                "finished": True,
                "updated_at_ms": 0,
            }
        ),
        encoding="utf-8",
    )
    (run_dir / "summary.json").write_text(
        json.dumps(
            {
                "schema": "sde.benchmark_aggregate_summary.v1",
                "runId": "bench-complete",
                "suitePath": "/tmp/suite.jsonl",
                "mode": "baseline",
                "verdict": "passed",
                "perTaskDeltas": [],
            }
        ),
        encoding="utf-8",
    )
    (run_dir / "traces.jsonl").write_text("", encoding="utf-8")
    result = validate_run("bench-complete", mode=None)
    assert result["ok"] is True
    assert result.get("execution_gates_applied") is False
    assert result.get("run_kind") == "benchmark_aggregate"
    assert result["errors"] == []


def test_validate_run_single_task_prefers_run_manifest_over_benchmark(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """If both manifests exist, treat as single-task (execution gates), not benchmark-only."""
    monkeypatch.setattr(_validate_run_module, "outputs_base", lambda: tmp_path)
    run_dir = tmp_path / "runs" / "hybrid"
    run_dir.mkdir(parents=True)
    (run_dir / "benchmark-manifest.json").write_text(
        json.dumps({"schema": "sde.benchmark_manifest.v1", "run_id": "hybrid", "mode": "baseline"}),
        encoding="utf-8",
    )
    (run_dir / "run-manifest.json").write_text(
        json.dumps({"schema": "sde.run_manifest.v1", "run_id": "hybrid", "mode": "baseline", "task": "t"}),
        encoding="utf-8",
    )
    result = validate_run("hybrid", mode=None)
    assert result.get("run_kind") == "single_task"
    assert result.get("execution_gates_applied") is True


def test_validate_run_benchmark_mode_both_requires_override(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(_validate_run_module, "outputs_base", lambda: tmp_path)
    run_dir = tmp_path / "runs" / "bench-both"
    run_dir.mkdir(parents=True)
    (run_dir / "benchmark-manifest.json").write_text(
        json.dumps({"schema": "sde.benchmark_manifest.v1", "run_id": "bench-both", "mode": "both"}),
        encoding="utf-8",
    )
    result = validate_run("bench-both", mode=None)
    assert result["ok"] is False
    assert result["validation_ready"] is False
    assert result["errors"] == ["benchmark_manifest_mode_both_requires_mode_override"]
