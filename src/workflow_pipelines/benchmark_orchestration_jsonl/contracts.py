"""Contracts for benchmark-orchestration runtime artifact."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

BENCHMARK_ORCHESTRATION_JSONL_RUNTIME_CONTRACT = "sde.benchmark_orchestration_jsonl_runtime.v1"
BENCHMARK_ORCHESTRATION_JSONL_RUNTIME_SCHEMA_VERSION = "1.0"
_CANONICAL_EVIDENCE_REFS = {
    "orchestration_ref": "orchestration.jsonl",
    "runtime_ref": "benchmark-orchestration-runtime.json",
}


def validate_benchmark_orchestration_jsonl_runtime_dict(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["benchmark_orchestration_jsonl_runtime_not_object"]
    errs, status = _validate_core_fields(body)
    checks = body.get("checks")
    errs.extend(_validate_checks(checks))
    counts = body.get("counts")
    errs.extend(_validate_counts(counts))
    errs.extend(_validate_evidence(body.get("evidence")))
    if not errs and isinstance(checks, dict) and isinstance(counts, dict):
        errs.extend(_validate_status_semantics(status=status, checks=checks, counts=counts))
    return errs


def _validate_core_fields(body: dict[str, Any]) -> tuple[list[str], Any]:
    errs: list[str] = []
    if body.get("schema") != BENCHMARK_ORCHESTRATION_JSONL_RUNTIME_CONTRACT:
        errs.append("benchmark_orchestration_jsonl_runtime_schema")
    if body.get("schema_version") != BENCHMARK_ORCHESTRATION_JSONL_RUNTIME_SCHEMA_VERSION:
        errs.append("benchmark_orchestration_jsonl_runtime_schema_version")
    run_id = body.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errs.append("benchmark_orchestration_jsonl_runtime_run_id")
    status = body.get("status")
    if status not in ("clean", "has_error"):
        errs.append("benchmark_orchestration_jsonl_runtime_status")
    return errs, status


def _validate_checks(checks: Any) -> list[str]:
    if not isinstance(checks, dict):
        return ["benchmark_orchestration_jsonl_runtime_checks"]
    errs: list[str] = []
    for key in ("orchestration_present", "resume_lines_valid", "error_lines_valid"):
        if not isinstance(checks.get(key), bool):
            errs.append(f"benchmark_orchestration_jsonl_runtime_check_type:{key}")
    return errs


def _validate_counts(counts: Any) -> list[str]:
    if not isinstance(counts, dict):
        return ["benchmark_orchestration_jsonl_runtime_counts"]
    errs: list[str] = []
    for key in ("row_count", "resume_count", "error_count"):
        value = counts.get(key)
        if isinstance(value, bool) or not isinstance(value, int):
            errs.append(f"benchmark_orchestration_jsonl_runtime_count_type:{key}")
            continue
        if value < 0:
            errs.append(f"benchmark_orchestration_jsonl_runtime_count_range:{key}")
    return errs


def _validate_status_semantics(status: Any, checks: dict[str, Any], counts: dict[str, Any]) -> list[str]:
    orchestration_present = checks.get("orchestration_present")
    resume_lines_valid = checks.get("resume_lines_valid")
    error_lines_valid = checks.get("error_lines_valid")
    row_count = counts.get("row_count")
    resume_count = counts.get("resume_count")
    error_count = counts.get("error_count")
    if (
        status not in ("clean", "has_error")
        or not isinstance(orchestration_present, bool)
        or not isinstance(resume_lines_valid, bool)
        or not isinstance(error_lines_valid, bool)
        or isinstance(row_count, bool)
        or not isinstance(row_count, int)
        or isinstance(resume_count, bool)
        or not isinstance(resume_count, int)
        or isinstance(error_count, bool)
        or not isinstance(error_count, int)
    ):
        return []
    errs: list[str] = []
    if orchestration_present != (row_count > 0):
        errs.append("benchmark_orchestration_jsonl_runtime_counts_mismatch")
    if resume_count + error_count > row_count:
        errs.append("benchmark_orchestration_jsonl_runtime_counts_mismatch")
    expected_status = "clean" if resume_lines_valid and error_lines_valid else "has_error"
    if status != expected_status:
        errs.append("benchmark_orchestration_jsonl_runtime_status_checks_mismatch")
    return errs


def _validate_evidence(evidence: Any) -> list[str]:
    if evidence is None:
        return []
    if not isinstance(evidence, dict):
        return ["benchmark_orchestration_jsonl_runtime_evidence"]
    if not evidence:
        return []
    errs: list[str] = []
    for key, expected in _CANONICAL_EVIDENCE_REFS.items():
        if key not in evidence:
            continue
        value = evidence.get(key)
        if not isinstance(value, str) or not value.strip():
            errs.append(f"benchmark_orchestration_jsonl_runtime_evidence_ref:{key}")
            continue
        normalized = value.strip()
        if normalized.startswith("/") or ".." in normalized.split("/") or normalized != expected:
            errs.append(f"benchmark_orchestration_jsonl_runtime_evidence_ref:{key}")
    return errs


def validate_benchmark_orchestration_jsonl_runtime_path(path: Path) -> list[str]:
    if not path.is_file():
        return ["benchmark_orchestration_jsonl_runtime_file_missing"]
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except OSError:
        return ["benchmark_orchestration_jsonl_runtime_unreadable"]
    except json.JSONDecodeError:
        return ["benchmark_orchestration_jsonl_runtime_json"]
    return validate_benchmark_orchestration_jsonl_runtime_dict(body)
