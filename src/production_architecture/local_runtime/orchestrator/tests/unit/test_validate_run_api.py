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
    (run_dir / "benchmark-checkpoint-runtime.json").write_text(
        json.dumps(
            {
                "schema": "sde.benchmark_checkpoint_runtime.v1",
                "schema_version": "1.0",
                "run_id": "bench-complete",
                "status": "finished",
                "checks": {
                    "checkpoint_present": True,
                    "finished": True,
                    "has_completed_tasks": False,
                },
                "evidence": {},
            }
        ),
        encoding="utf-8",
    )
    (run_dir / "benchmark-manifest-runtime.json").write_text(
        json.dumps(
            {
                "schema": "sde.benchmark_aggregate_manifest_runtime.v1",
                "schema_version": "1.0",
                "run_id": "bench-complete",
                "status": "finished",
                "checks": {
                    "manifest_present": True,
                    "checkpoint_present": True,
                    "checkpoint_finished": True,
                },
                "evidence": {},
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
    (run_dir / "benchmark-summary-runtime.json").write_text(
        json.dumps(
            {
                "schema": "sde.benchmark_aggregate_summary_runtime.v1",
                "schema_version": "1.0",
                "run_id": "bench-complete",
                "status": "finished",
                "checks": {
                    "summary_present": True,
                    "summary_contract_valid": True,
                    "is_failed_summary": False,
                },
                "evidence": {},
            }
        ),
        encoding="utf-8",
    )
    (run_dir / "benchmark-orchestration-runtime.json").write_text(
        json.dumps(
            {
                "schema": "sde.benchmark_orchestration_jsonl_runtime.v1",
                "schema_version": "1.0",
                "run_id": "bench-complete",
                "status": "clean",
                "checks": {
                    "orchestration_present": False,
                    "resume_lines_valid": True,
                    "error_lines_valid": True,
                },
                "counts": {"row_count": 0, "resume_count": 0, "error_count": 0},
                "evidence": {},
            }
        ),
        encoding="utf-8",
    )
    (run_dir / "traces-event-row-runtime.json").write_text(
        json.dumps(
            {
                "schema": "sde.traces_jsonl_event_row_runtime.v1",
                "schema_version": "1.0",
                "run_id": "bench-complete",
                "status": "ready",
                "checks": {
                    "all_rows_valid": True,
                    "run_id_consistent": True,
                },
                "counts": {"row_count": 0},
                "evidence": {},
            }
        ),
        encoding="utf-8",
    )
    (run_dir / "offline-evaluation-runtime.json").write_text(
        json.dumps(
            {
                "schema": "sde.offline_evaluation_runtime.v1",
                "schema_version": "1.0",
                "run_id": "bench-complete",
                "status": "ready",
                "checks": {
                    "suite_contract_valid": True,
                    "summary_present": True,
                    "traces_present": True,
                    "checkpoint_finished": True,
                },
                "counts": {"suite_error_count": 0},
                "evidence": {},
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


def test_validate_run_benchmark_manifest_runtime_contract_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(_validate_run_module, "outputs_base", lambda: tmp_path)
    run_dir = tmp_path / "runs" / "bench-runtime-bad"
    run_dir.mkdir(parents=True)
    (run_dir / "benchmark-manifest.json").write_text(
        json.dumps(
            {
                "schema": "sde.benchmark_manifest.v1",
                "run_id": "bench-runtime-bad",
                "suite_path": "/tmp/suite.jsonl",
                "mode": "baseline",
                "tasks": [],
                "max_tasks": None,
                "continue_on_error": False,
            }
        ),
        encoding="utf-8",
    )
    (run_dir / "benchmark-manifest-runtime.json").write_text(json.dumps({"schema": "bad"}), encoding="utf-8")
    (run_dir / "benchmark-checkpoint.json").write_text(
        json.dumps(
            {
                "schema": "sde.benchmark_checkpoint.v1",
                "run_id": "bench-runtime-bad",
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
                "runId": "bench-runtime-bad",
                "suitePath": "/tmp/suite.jsonl",
                "mode": "baseline",
                "verdict": "passed",
                "perTaskDeltas": [],
            }
        ),
        encoding="utf-8",
    )
    (run_dir / "traces.jsonl").write_text("", encoding="utf-8")
    result = validate_run("bench-runtime-bad", mode=None)
    assert result["ok"] is False
    assert "benchmark_manifest_runtime_contract:benchmark_aggregate_manifest_runtime_schema" in result["errors"]


def test_validate_run_benchmark_checkpoint_runtime_contract_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(_validate_run_module, "outputs_base", lambda: tmp_path)
    run_dir = tmp_path / "runs" / "bench-checkpoint-runtime-bad"
    run_dir.mkdir(parents=True)
    (run_dir / "benchmark-manifest.json").write_text(
        json.dumps(
            {
                "schema": "sde.benchmark_manifest.v1",
                "run_id": "bench-checkpoint-runtime-bad",
                "suite_path": "/tmp/suite.jsonl",
                "mode": "baseline",
                "tasks": [],
                "max_tasks": None,
                "continue_on_error": False,
            }
        ),
        encoding="utf-8",
    )
    (run_dir / "benchmark-manifest-runtime.json").write_text(
        json.dumps(
            {
                "schema": "sde.benchmark_aggregate_manifest_runtime.v1",
                "schema_version": "1.0",
                "run_id": "bench-checkpoint-runtime-bad",
                "status": "finished",
                "checks": {
                    "manifest_present": True,
                    "checkpoint_present": True,
                    "checkpoint_finished": True,
                },
                "evidence": {},
            }
        ),
        encoding="utf-8",
    )
    (run_dir / "benchmark-checkpoint.json").write_text(
        json.dumps(
            {
                "schema": "sde.benchmark_checkpoint.v1",
                "run_id": "bench-checkpoint-runtime-bad",
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
    (run_dir / "benchmark-checkpoint-runtime.json").write_text(
        json.dumps({"schema": "bad"}),
        encoding="utf-8",
    )
    (run_dir / "summary.json").write_text(
        json.dumps(
            {
                "schema": "sde.benchmark_aggregate_summary.v1",
                "runId": "bench-checkpoint-runtime-bad",
                "suitePath": "/tmp/suite.jsonl",
                "mode": "baseline",
                "verdict": "passed",
                "perTaskDeltas": [],
            }
        ),
        encoding="utf-8",
    )
    (run_dir / "benchmark-summary-runtime.json").write_text(
        json.dumps(
            {
                "schema": "sde.benchmark_aggregate_summary_runtime.v1",
                "schema_version": "1.0",
                "run_id": "bench-checkpoint-runtime-bad",
                "status": "finished",
                "checks": {
                    "summary_present": True,
                    "summary_contract_valid": True,
                    "is_failed_summary": False,
                },
                "evidence": {},
            }
        ),
        encoding="utf-8",
    )
    (run_dir / "traces.jsonl").write_text("", encoding="utf-8")
    result = validate_run("bench-checkpoint-runtime-bad", mode=None)
    assert result["ok"] is False
    assert "benchmark_checkpoint_runtime_contract:benchmark_checkpoint_runtime_schema" in result["errors"]


def test_validate_run_benchmark_summary_runtime_contract_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(_validate_run_module, "outputs_base", lambda: tmp_path)
    run_dir = tmp_path / "runs" / "bench-summary-runtime-bad"
    run_dir.mkdir(parents=True)
    (run_dir / "benchmark-manifest.json").write_text(
        json.dumps(
            {
                "schema": "sde.benchmark_manifest.v1",
                "run_id": "bench-summary-runtime-bad",
                "suite_path": "/tmp/suite.jsonl",
                "mode": "baseline",
                "tasks": [],
                "max_tasks": None,
                "continue_on_error": False,
            }
        ),
        encoding="utf-8",
    )
    (run_dir / "benchmark-manifest-runtime.json").write_text(
        json.dumps(
            {
                "schema": "sde.benchmark_aggregate_manifest_runtime.v1",
                "schema_version": "1.0",
                "run_id": "bench-summary-runtime-bad",
                "status": "finished",
                "checks": {
                    "manifest_present": True,
                    "checkpoint_present": True,
                    "checkpoint_finished": True,
                },
                "evidence": {},
            }
        ),
        encoding="utf-8",
    )
    (run_dir / "benchmark-checkpoint.json").write_text(
        json.dumps(
            {
                "schema": "sde.benchmark_checkpoint.v1",
                "run_id": "bench-summary-runtime-bad",
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
                "runId": "bench-summary-runtime-bad",
                "suitePath": "/tmp/suite.jsonl",
                "mode": "baseline",
                "verdict": "passed",
                "perTaskDeltas": [],
            }
        ),
        encoding="utf-8",
    )
    (run_dir / "benchmark-summary-runtime.json").write_text(json.dumps({"schema": "bad"}), encoding="utf-8")
    (run_dir / "traces.jsonl").write_text("", encoding="utf-8")
    result = validate_run("bench-summary-runtime-bad", mode=None)
    assert result["ok"] is False
    assert "benchmark_summary_runtime_contract:benchmark_aggregate_summary_runtime_schema" in result["errors"]


def test_validate_run_benchmark_orchestration_runtime_contract_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(_validate_run_module, "outputs_base", lambda: tmp_path)
    run_dir = tmp_path / "runs" / "bench-orchestration-runtime-bad"
    run_dir.mkdir(parents=True)
    (run_dir / "benchmark-manifest.json").write_text(
        json.dumps(
            {
                "schema": "sde.benchmark_manifest.v1",
                "run_id": "bench-orchestration-runtime-bad",
                "suite_path": "/tmp/suite.jsonl",
                "mode": "baseline",
                "tasks": [],
                "max_tasks": None,
                "continue_on_error": False,
            }
        ),
        encoding="utf-8",
    )
    (run_dir / "benchmark-manifest-runtime.json").write_text(
        json.dumps(
            {
                "schema": "sde.benchmark_aggregate_manifest_runtime.v1",
                "schema_version": "1.0",
                "run_id": "bench-orchestration-runtime-bad",
                "status": "finished",
                "checks": {
                    "manifest_present": True,
                    "checkpoint_present": True,
                    "checkpoint_finished": True,
                },
                "evidence": {},
            }
        ),
        encoding="utf-8",
    )
    (run_dir / "benchmark-checkpoint.json").write_text(
        json.dumps(
            {
                "schema": "sde.benchmark_checkpoint.v1",
                "run_id": "bench-orchestration-runtime-bad",
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
    (run_dir / "benchmark-checkpoint-runtime.json").write_text(
        json.dumps(
            {
                "schema": "sde.benchmark_checkpoint_runtime.v1",
                "schema_version": "1.0",
                "run_id": "bench-orchestration-runtime-bad",
                "status": "finished",
                "checks": {
                    "checkpoint_present": True,
                    "finished": True,
                    "has_completed_tasks": False,
                },
                "evidence": {},
            }
        ),
        encoding="utf-8",
    )
    (run_dir / "summary.json").write_text(
        json.dumps(
            {
                "schema": "sde.benchmark_aggregate_summary.v1",
                "runId": "bench-orchestration-runtime-bad",
                "suitePath": "/tmp/suite.jsonl",
                "mode": "baseline",
                "verdict": "passed",
                "perTaskDeltas": [],
            }
        ),
        encoding="utf-8",
    )
    (run_dir / "benchmark-summary-runtime.json").write_text(
        json.dumps(
            {
                "schema": "sde.benchmark_aggregate_summary_runtime.v1",
                "schema_version": "1.0",
                "run_id": "bench-orchestration-runtime-bad",
                "status": "finished",
                "checks": {
                    "summary_present": True,
                    "summary_contract_valid": True,
                    "is_failed_summary": False,
                },
                "evidence": {},
            }
        ),
        encoding="utf-8",
    )
    (run_dir / "benchmark-orchestration-runtime.json").write_text(
        json.dumps({"schema": "bad"}),
        encoding="utf-8",
    )
    (run_dir / "traces-event-row-runtime.json").write_text(
        json.dumps(
            {
                "schema": "sde.traces_jsonl_event_row_runtime.v1",
                "schema_version": "1.0",
                "run_id": "bench-orchestration-runtime-bad",
                "status": "ready",
                "checks": {"all_rows_valid": True, "run_id_consistent": True},
                "counts": {"row_count": 0},
                "evidence": {},
            }
        ),
        encoding="utf-8",
    )
    (run_dir / "traces.jsonl").write_text("", encoding="utf-8")
    result = validate_run("bench-orchestration-runtime-bad", mode=None)
    assert result["ok"] is False
    assert (
        "benchmark_orchestration_runtime_contract:benchmark_orchestration_jsonl_runtime_schema"
        in result["errors"]
    )


def test_validate_run_traces_event_row_runtime_contract_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(_validate_run_module, "outputs_base", lambda: tmp_path)
    run_dir = tmp_path / "runs" / "bench-traces-runtime-bad"
    run_dir.mkdir(parents=True)
    (run_dir / "benchmark-manifest.json").write_text(
        json.dumps(
            {
                "schema": "sde.benchmark_manifest.v1",
                "run_id": "bench-traces-runtime-bad",
                "suite_path": "/tmp/suite.jsonl",
                "mode": "baseline",
                "tasks": [],
                "max_tasks": None,
                "continue_on_error": False,
            }
        ),
        encoding="utf-8",
    )
    (run_dir / "benchmark-manifest-runtime.json").write_text(
        json.dumps(
            {
                "schema": "sde.benchmark_aggregate_manifest_runtime.v1",
                "schema_version": "1.0",
                "run_id": "bench-traces-runtime-bad",
                "status": "finished",
                "checks": {"manifest_present": True, "checkpoint_present": True, "checkpoint_finished": True},
                "evidence": {},
            }
        ),
        encoding="utf-8",
    )
    (run_dir / "benchmark-checkpoint.json").write_text(
        json.dumps(
            {
                "schema": "sde.benchmark_checkpoint.v1",
                "run_id": "bench-traces-runtime-bad",
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
    (run_dir / "benchmark-checkpoint-runtime.json").write_text(
        json.dumps(
            {
                "schema": "sde.benchmark_checkpoint_runtime.v1",
                "schema_version": "1.0",
                "run_id": "bench-traces-runtime-bad",
                "status": "finished",
                "checks": {"checkpoint_present": True, "finished": True, "has_completed_tasks": False},
                "evidence": {},
            }
        ),
        encoding="utf-8",
    )
    (run_dir / "summary.json").write_text(
        json.dumps(
            {
                "schema": "sde.benchmark_aggregate_summary.v1",
                "runId": "bench-traces-runtime-bad",
                "suitePath": "/tmp/suite.jsonl",
                "mode": "baseline",
                "verdict": "passed",
                "perTaskDeltas": [],
            }
        ),
        encoding="utf-8",
    )
    (run_dir / "benchmark-summary-runtime.json").write_text(
        json.dumps(
            {
                "schema": "sde.benchmark_aggregate_summary_runtime.v1",
                "schema_version": "1.0",
                "run_id": "bench-traces-runtime-bad",
                "status": "finished",
                "checks": {"summary_present": True, "summary_contract_valid": True, "is_failed_summary": False},
                "evidence": {},
            }
        ),
        encoding="utf-8",
    )
    (run_dir / "benchmark-orchestration-runtime.json").write_text(
        json.dumps(
            {
                "schema": "sde.benchmark_orchestration_jsonl_runtime.v1",
                "schema_version": "1.0",
                "run_id": "bench-traces-runtime-bad",
                "status": "clean",
                "checks": {"orchestration_present": False, "resume_lines_valid": True, "error_lines_valid": True},
                "counts": {"row_count": 0, "resume_count": 0, "error_count": 0},
                "evidence": {},
            }
        ),
        encoding="utf-8",
    )
    (run_dir / "traces-event-row-runtime.json").write_text(json.dumps({"schema": "bad"}), encoding="utf-8")
    (run_dir / "traces.jsonl").write_text("", encoding="utf-8")
    result = validate_run("bench-traces-runtime-bad", mode=None)
    assert result["ok"] is False
    assert "traces_event_row_runtime_contract:traces_jsonl_event_row_runtime_schema" in result["errors"]


def test_validate_run_offline_evaluation_runtime_contract_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(_validate_run_module, "outputs_base", lambda: tmp_path)
    run_dir = tmp_path / "runs" / "bench-offline-runtime-bad"
    run_dir.mkdir(parents=True)
    (run_dir / "benchmark-manifest.json").write_text(
        json.dumps(
            {
                "schema": "sde.benchmark_manifest.v1",
                "run_id": "bench-offline-runtime-bad",
                "suite_path": "/tmp/suite.jsonl",
                "mode": "baseline",
                "tasks": [],
                "max_tasks": None,
                "continue_on_error": False,
            }
        ),
        encoding="utf-8",
    )
    (run_dir / "benchmark-manifest-runtime.json").write_text(
        json.dumps(
            {
                "schema": "sde.benchmark_aggregate_manifest_runtime.v1",
                "schema_version": "1.0",
                "run_id": "bench-offline-runtime-bad",
                "status": "finished",
                "checks": {"manifest_present": True, "checkpoint_present": True, "checkpoint_finished": True},
                "evidence": {},
            }
        ),
        encoding="utf-8",
    )
    (run_dir / "benchmark-checkpoint.json").write_text(
        json.dumps(
            {
                "schema": "sde.benchmark_checkpoint.v1",
                "run_id": "bench-offline-runtime-bad",
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
    (run_dir / "benchmark-checkpoint-runtime.json").write_text(
        json.dumps(
            {
                "schema": "sde.benchmark_checkpoint_runtime.v1",
                "schema_version": "1.0",
                "run_id": "bench-offline-runtime-bad",
                "status": "finished",
                "checks": {"checkpoint_present": True, "finished": True, "has_completed_tasks": False},
                "evidence": {},
            }
        ),
        encoding="utf-8",
    )
    (run_dir / "summary.json").write_text(
        json.dumps(
            {
                "schema": "sde.benchmark_aggregate_summary.v1",
                "runId": "bench-offline-runtime-bad",
                "suitePath": "/tmp/suite.jsonl",
                "mode": "baseline",
                "verdict": "passed",
                "perTaskDeltas": [],
            }
        ),
        encoding="utf-8",
    )
    (run_dir / "benchmark-summary-runtime.json").write_text(
        json.dumps(
            {
                "schema": "sde.benchmark_aggregate_summary_runtime.v1",
                "schema_version": "1.0",
                "run_id": "bench-offline-runtime-bad",
                "status": "finished",
                "checks": {"summary_present": True, "summary_contract_valid": True, "is_failed_summary": False},
                "evidence": {},
            }
        ),
        encoding="utf-8",
    )
    (run_dir / "benchmark-orchestration-runtime.json").write_text(
        json.dumps(
            {
                "schema": "sde.benchmark_orchestration_jsonl_runtime.v1",
                "schema_version": "1.0",
                "run_id": "bench-offline-runtime-bad",
                "status": "clean",
                "checks": {"orchestration_present": False, "resume_lines_valid": True, "error_lines_valid": True},
                "counts": {"row_count": 0, "resume_count": 0, "error_count": 0},
                "evidence": {},
            }
        ),
        encoding="utf-8",
    )
    (run_dir / "traces-event-row-runtime.json").write_text(
        json.dumps(
            {
                "schema": "sde.traces_jsonl_event_row_runtime.v1",
                "schema_version": "1.0",
                "run_id": "bench-offline-runtime-bad",
                "status": "ready",
                "checks": {"all_rows_valid": True, "run_id_consistent": True},
                "counts": {"row_count": 0},
                "evidence": {},
            }
        ),
        encoding="utf-8",
    )
    (run_dir / "offline-evaluation-runtime.json").write_text(json.dumps({"schema": "bad"}), encoding="utf-8")
    (run_dir / "traces.jsonl").write_text("", encoding="utf-8")
    result = validate_run("bench-offline-runtime-bad", mode=None)
    assert result["ok"] is False
    assert "offline_evaluation_runtime_contract:offline_evaluation_runtime_schema" in result["errors"]


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
