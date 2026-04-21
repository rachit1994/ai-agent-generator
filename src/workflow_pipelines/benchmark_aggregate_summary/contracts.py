"""Contracts for benchmark aggregate summary runtime artifact."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

BENCHMARK_AGGREGATE_SUMMARY_RUNTIME_CONTRACT = "sde.benchmark_aggregate_summary_runtime.v1"
BENCHMARK_AGGREGATE_SUMMARY_RUNTIME_SCHEMA_VERSION = "1.0"


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
    checks = body.get("checks")
    if not isinstance(checks, dict):
        errs.append("benchmark_aggregate_summary_runtime_checks")
    else:
        for key in ("summary_present", "summary_contract_valid", "is_failed_summary"):
            if not isinstance(checks.get(key), bool):
                errs.append(f"benchmark_aggregate_summary_runtime_check_type:{key}")
    return errs


def validate_benchmark_aggregate_summary_runtime_path(path: Path) -> list[str]:
    if not path.is_file():
        return ["benchmark_aggregate_summary_runtime_file_missing"]
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ["benchmark_aggregate_summary_runtime_json"]
    return validate_benchmark_aggregate_summary_runtime_dict(body)
