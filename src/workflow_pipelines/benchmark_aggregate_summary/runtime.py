"""Deterministic benchmark aggregate summary runtime derivation."""

from __future__ import annotations

from typing import Any

from .benchmark_aggregate_summary_contract import validate_benchmark_aggregate_summary_dict
from .contracts import (
    BENCHMARK_AGGREGATE_SUMMARY_RUNTIME_CONTRACT,
    BENCHMARK_AGGREGATE_SUMMARY_RUNTIME_SCHEMA_VERSION,
)


def build_benchmark_aggregate_summary_runtime(*, summary: dict[str, Any]) -> dict[str, Any]:
    run_id = str(summary.get("runId") or summary.get("run_id") or "").strip()
    summary_present = bool(summary)
    summary_contract_valid = summary_present and not validate_benchmark_aggregate_summary_dict(summary)
    is_failed_summary = str(summary.get("runStatus") or summary.get("run_status") or "") == "failed"
    status = "failed" if is_failed_summary else "finished"
    return {
        "schema": BENCHMARK_AGGREGATE_SUMMARY_RUNTIME_CONTRACT,
        "schema_version": BENCHMARK_AGGREGATE_SUMMARY_RUNTIME_SCHEMA_VERSION,
        "run_id": run_id,
        "status": status,
        "checks": {
            "summary_present": summary_present,
            "summary_contract_valid": bool(summary_contract_valid),
            "is_failed_summary": is_failed_summary,
        },
        "evidence": {
            "benchmark_summary_ref": "summary.json",
            "benchmark_summary_runtime_ref": "benchmark-summary-runtime.json",
        },
    }
