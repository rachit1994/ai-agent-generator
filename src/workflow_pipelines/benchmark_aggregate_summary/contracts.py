"""Contracts for benchmark aggregate summary runtime artifact."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

BENCHMARK_AGGREGATE_SUMMARY_RUNTIME_CONTRACT = "sde.benchmark_aggregate_summary_runtime.v1"
BENCHMARK_AGGREGATE_SUMMARY_RUNTIME_SCHEMA_VERSION = "1.0"
_CANONICAL_EVIDENCE_REFS = {
    "benchmark_summary_ref": "summary.json",
    "benchmark_summary_runtime_ref": "benchmark-summary-runtime.json",
}


def _validate_checks(checks: Any) -> tuple[list[str], dict[str, bool] | None]:
    if not isinstance(checks, dict):
        return (["benchmark_aggregate_summary_runtime_checks"], None)
    errs: list[str] = []
    values: dict[str, bool] = {}
    for key in ("summary_present", "summary_contract_valid", "is_failed_summary"):
        value = checks.get(key)
        if not isinstance(value, bool):
            errs.append(f"benchmark_aggregate_summary_runtime_check_type:{key}")
            continue
        values[key] = value
    if errs:
        return (errs, None)
    return ([], values)


def _validate_evidence(evidence: Any) -> list[str]:
    if not isinstance(evidence, dict):
        return ["benchmark_aggregate_summary_runtime_evidence"]
    errs: list[str] = []
    for key, expected in _CANONICAL_EVIDENCE_REFS.items():
        value = evidence.get(key)
        if not isinstance(value, str) or not value.strip():
            errs.append(f"benchmark_aggregate_summary_runtime_evidence_ref:{key}")
            continue
        normalized = value.strip()
        if normalized != expected:
            errs.append(f"benchmark_aggregate_summary_runtime_evidence_ref:{key}")
            continue
        ref_path = Path(normalized)
        if ref_path.is_absolute() or ".." in ref_path.parts:
            errs.append(f"benchmark_aggregate_summary_runtime_evidence_ref:{key}")
    return errs


def _validate_status_checks_coherence(status: Any, values: dict[str, bool] | None) -> list[str]:
    if values is None:
        return []
    errs: list[str] = []
    if status == "finished" and values["summary_present"] is not True:
        errs.append("benchmark_aggregate_summary_runtime_status_finished_requires_summary")
    if status == "finished" and values["summary_contract_valid"] is not True:
        errs.append("benchmark_aggregate_summary_runtime_status_finished_requires_valid_summary")
    if status == "finished" and values["is_failed_summary"] is True:
        errs.append("benchmark_aggregate_summary_runtime_status_finished_mismatch")
    if status == "failed" and values["is_failed_summary"] is not True:
        errs.append("benchmark_aggregate_summary_runtime_status_failed_mismatch")
    return errs


def validate_benchmark_aggregate_summary_runtime_dict(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["benchmark_aggregate_summary_runtime_not_object"]
    errs: list[str] = []
    if body.get("schema") != BENCHMARK_AGGREGATE_SUMMARY_RUNTIME_CONTRACT:
        errs.append("benchmark_aggregate_summary_runtime_schema")
    if body.get("schema_version") != BENCHMARK_AGGREGATE_SUMMARY_RUNTIME_SCHEMA_VERSION:
        errs.append("benchmark_aggregate_summary_runtime_schema_version")
    run_id = body.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errs.append("benchmark_aggregate_summary_runtime_run_id")
    status = body.get("status")
    if status not in ("failed", "finished"):
        errs.append("benchmark_aggregate_summary_runtime_status")
    check_errs, values = _validate_checks(body.get("checks"))
    errs.extend(check_errs)
    errs.extend(_validate_status_checks_coherence(status, values))
    errs.extend(_validate_evidence(body.get("evidence")))
    return errs


def validate_benchmark_aggregate_summary_runtime_path(path: Path) -> list[str]:
    if not path.is_file():
        return ["benchmark_aggregate_summary_runtime_file_missing"]
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except OSError:
        return ["benchmark_aggregate_summary_runtime_unreadable"]
    except json.JSONDecodeError:
        return ["benchmark_aggregate_summary_runtime_json"]
    return validate_benchmark_aggregate_summary_runtime_dict(body)
