from __future__ import annotations

from pathlib import Path

import pytest

from workflow_pipelines.benchmark_aggregate_summary import (
    build_benchmark_aggregate_summary_runtime,
    validate_benchmark_aggregate_summary_runtime_dict,
    validate_benchmark_aggregate_summary_runtime_path,
)


def test_build_benchmark_aggregate_summary_runtime_deterministic() -> None:
    summary = {
        "schema": "sde.benchmark_aggregate_summary.v1",
        "runId": "bench-sum",
        "suitePath": "/tmp/s.jsonl",
        "mode": "baseline",
        "verdict": "passed",
        "perTaskDeltas": [],
    }
    one = build_benchmark_aggregate_summary_runtime(summary=summary)
    two = build_benchmark_aggregate_summary_runtime(summary=summary)
    assert one == two
    assert one["status"] == "finished"
    assert validate_benchmark_aggregate_summary_runtime_dict(one) == []


def test_validate_benchmark_aggregate_summary_runtime_fail_closed() -> None:
    errs = validate_benchmark_aggregate_summary_runtime_dict({"schema": "bad"})
    assert "benchmark_aggregate_summary_runtime_schema" in errs
    assert "benchmark_aggregate_summary_runtime_schema_version" in errs


def test_validate_benchmark_aggregate_summary_runtime_rejects_status_checks_mismatch() -> None:
    errs = validate_benchmark_aggregate_summary_runtime_dict(
        {
            "schema": "sde.benchmark_aggregate_summary_runtime.v1",
            "schema_version": "1.0",
            "run_id": "bench-runtime",
            "status": "finished",
            "checks": {
                "summary_present": True,
                "summary_contract_valid": False,
                "is_failed_summary": False,
            },
            "evidence": {
                "benchmark_summary_ref": "summary.json",
                "benchmark_summary_runtime_ref": "benchmark-summary-runtime.json",
            },
        }
    )
    assert "benchmark_aggregate_summary_runtime_status_finished_requires_valid_summary" in errs


def test_validate_benchmark_aggregate_summary_runtime_rejects_invalid_evidence_refs() -> None:
    errs = validate_benchmark_aggregate_summary_runtime_dict(
        {
            "schema": "sde.benchmark_aggregate_summary_runtime.v1",
            "schema_version": "1.0",
            "run_id": "bench-runtime",
            "status": "failed",
            "checks": {
                "summary_present": True,
                "summary_contract_valid": False,
                "is_failed_summary": True,
            },
            "evidence": {
                "benchmark_summary_ref": "../summary.json",
                "benchmark_summary_runtime_ref": "benchmark-summary-runtime.json",
            },
        }
    )
    assert "benchmark_aggregate_summary_runtime_evidence_ref:benchmark_summary_ref" in errs


def test_validate_benchmark_aggregate_summary_runtime_rejects_finished_without_summary_present() -> None:
    errs = validate_benchmark_aggregate_summary_runtime_dict(
        {
            "schema": "sde.benchmark_aggregate_summary_runtime.v1",
            "schema_version": "1.0",
            "run_id": "bench-runtime",
            "status": "finished",
            "checks": {
                "summary_present": False,
                "summary_contract_valid": True,
                "is_failed_summary": False,
            },
            "evidence": {
                "benchmark_summary_ref": "summary.json",
                "benchmark_summary_runtime_ref": "benchmark-summary-runtime.json",
            },
        }
    )
    assert "benchmark_aggregate_summary_runtime_status_finished_requires_summary" in errs


def test_validate_benchmark_aggregate_summary_runtime_rejects_finished_when_summary_failed() -> None:
    errs = validate_benchmark_aggregate_summary_runtime_dict(
        {
            "schema": "sde.benchmark_aggregate_summary_runtime.v1",
            "schema_version": "1.0",
            "run_id": "bench-runtime",
            "status": "finished",
            "checks": {
                "summary_present": True,
                "summary_contract_valid": True,
                "is_failed_summary": True,
            },
            "evidence": {
                "benchmark_summary_ref": "summary.json",
                "benchmark_summary_runtime_ref": "benchmark-summary-runtime.json",
            },
        }
    )
    assert "benchmark_aggregate_summary_runtime_status_finished_mismatch" in errs


def test_validate_benchmark_aggregate_summary_runtime_rejects_failed_without_failed_flag() -> None:
    errs = validate_benchmark_aggregate_summary_runtime_dict(
        {
            "schema": "sde.benchmark_aggregate_summary_runtime.v1",
            "schema_version": "1.0",
            "run_id": "bench-runtime",
            "status": "failed",
            "checks": {
                "summary_present": True,
                "summary_contract_valid": False,
                "is_failed_summary": False,
            },
            "evidence": {
                "benchmark_summary_ref": "summary.json",
                "benchmark_summary_runtime_ref": "benchmark-summary-runtime.json",
            },
        }
    )
    assert "benchmark_aggregate_summary_runtime_status_failed_mismatch" in errs


def test_validate_benchmark_aggregate_summary_runtime_path_unreadable(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    runtime_path = tmp_path / "benchmark-summary-runtime.json"
    runtime_path.write_text("{}", encoding="utf-8")

    def _raise_oserror(self: Path, encoding: str = "utf-8") -> str:
        raise OSError("unreadable")

    monkeypatch.setattr(Path, "read_text", _raise_oserror)
    errs = validate_benchmark_aggregate_summary_runtime_path(runtime_path)
    assert errs == ["benchmark_aggregate_summary_runtime_unreadable"]
