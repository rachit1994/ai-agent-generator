"""Deterministic benchmark-orchestration runtime derivation."""

from __future__ import annotations

from typing import Any

from .contracts import (
    BENCHMARK_ORCHESTRATION_JSONL_RUNTIME_CONTRACT,
    BENCHMARK_ORCHESTRATION_JSONL_RUNTIME_SCHEMA_VERSION,
)
from .orchestration_benchmark_jsonl_contract import (
    validate_orchestration_benchmark_error_dict,
    validate_orchestration_benchmark_resume_dict,
)


def _validate_rows(rows: list[dict[str, Any]], *, line_type: str) -> bool:
    for row in rows:
        if line_type == "benchmark_resume":
            if validate_orchestration_benchmark_resume_dict(row):
                return False
        elif line_type == "benchmark_error":
            if validate_orchestration_benchmark_error_dict(row):
                return False
    return True


def build_benchmark_orchestration_jsonl_runtime(
    *,
    run_id: str,
    orchestration_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    resume_rows = [r for r in orchestration_rows if r.get("type") == "benchmark_resume"]
    error_rows = [r for r in orchestration_rows if r.get("type") == "benchmark_error"]
    unknown_rows = [
        r
        for r in orchestration_rows
        if r.get("type") not in ("benchmark_resume", "benchmark_error")
    ]
    orchestration_present = len(orchestration_rows) > 0
    resume_lines_valid = _validate_rows(resume_rows, line_type="benchmark_resume")
    error_lines_valid = _validate_rows(error_rows, line_type="benchmark_error")
    status = (
        "clean"
        if resume_lines_valid and error_lines_valid and len(unknown_rows) == 0
        else "has_error"
    )
    return {
        "schema": BENCHMARK_ORCHESTRATION_JSONL_RUNTIME_CONTRACT,
        "schema_version": BENCHMARK_ORCHESTRATION_JSONL_RUNTIME_SCHEMA_VERSION,
        "run_id": run_id,
        "status": status,
        "checks": {
            "orchestration_present": orchestration_present,
            "resume_lines_valid": resume_lines_valid,
            "error_lines_valid": error_lines_valid,
        },
        "counts": {
            "row_count": len(orchestration_rows),
            "resume_count": len(resume_rows),
            "error_count": len(error_rows),
        },
        "evidence": {
            "orchestration_ref": "orchestration.jsonl",
            "runtime_ref": "benchmark-orchestration-runtime.json",
        },
    }
