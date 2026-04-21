"""Contracts for benchmark-orchestration runtime artifact."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

BENCHMARK_ORCHESTRATION_JSONL_RUNTIME_CONTRACT = "sde.benchmark_orchestration_jsonl_runtime.v1"
BENCHMARK_ORCHESTRATION_JSONL_RUNTIME_SCHEMA_VERSION = "1.0"


def validate_benchmark_orchestration_jsonl_runtime_dict(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["benchmark_orchestration_jsonl_runtime_not_object"]
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
    checks = body.get("checks")
    if not isinstance(checks, dict):
        errs.append("benchmark_orchestration_jsonl_runtime_checks")
    else:
        for key in ("orchestration_present", "resume_lines_valid", "error_lines_valid"):
            if not isinstance(checks.get(key), bool):
                errs.append(f"benchmark_orchestration_jsonl_runtime_check_type:{key}")
    return errs


def validate_benchmark_orchestration_jsonl_runtime_path(path: Path) -> list[str]:
    if not path.is_file():
        return ["benchmark_orchestration_jsonl_runtime_file_missing"]
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ["benchmark_orchestration_jsonl_runtime_json"]
    return validate_benchmark_orchestration_jsonl_runtime_dict(body)
