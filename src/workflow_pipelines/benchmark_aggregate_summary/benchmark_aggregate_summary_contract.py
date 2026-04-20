"""Contract for benchmark harness ``summary.json`` (success envelope + early-abort failure)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Final

BENCHMARK_AGGREGATE_SUMMARY_CONTRACT: Final = "sde.benchmark_aggregate_summary.v1"

_SUMMARY_MODES: Final = frozenset({"baseline", "guarded_pipeline", "both"})


def _errs_aggregate_summary_common(b: dict[str, Any]) -> list[str]:
    errs: list[str] = []
    rid = b.get("runId", b.get("run_id"))
    if not isinstance(rid, str) or not rid.strip():
        errs.append("benchmark_aggregate_summary_run_id")
    sp = b.get("suitePath", b.get("suite_path"))
    if not isinstance(sp, str) or not sp.strip():
        errs.append("benchmark_aggregate_summary_suite_path")
    mode = b.get("mode")
    if mode not in _SUMMARY_MODES:
        errs.append("benchmark_aggregate_summary_mode")
    return errs


def _errs_aggregate_summary_failed(b: dict[str, Any]) -> list[str]:
    errs: list[str] = []
    err = b.get("error")
    if not isinstance(err, dict):
        errs.append("benchmark_aggregate_summary_error")
        return errs
    if not isinstance(err.get("type"), str) or not str(err.get("type")).strip():
        errs.append("benchmark_aggregate_summary_error_type")
    if not isinstance(err.get("message"), str):
        errs.append("benchmark_aggregate_summary_error_message_type")
    return errs


def _errs_aggregate_summary_success(b: dict[str, Any]) -> list[str]:
    errs: list[str] = []
    v = b.get("verdict")
    if not isinstance(v, str) or not v.strip():
        errs.append("benchmark_aggregate_summary_verdict")
    ptd = b.get("perTaskDeltas")
    if not isinstance(ptd, list):
        errs.append("benchmark_aggregate_summary_per_task_deltas")
    return errs


def validate_benchmark_aggregate_summary_dict(body: Any) -> list[str]:
    """Return stable error tokens for ``run_benchmark`` ``summary.json`` (aggregate run only)."""
    if not isinstance(body, dict):
        return ["benchmark_aggregate_summary_not_object"]
    b = body
    errs: list[str] = []
    errs.extend(_errs_aggregate_summary_common(b))
    if errs:
        return errs
    rs = b.get("runStatus", b.get("run_status"))
    if rs == "failed":
        errs.extend(_errs_aggregate_summary_failed(b))
    else:
        errs.extend(_errs_aggregate_summary_success(b))
    return errs


def validate_benchmark_aggregate_summary_path(path: Path) -> list[str]:
    if not path.is_file():
        return ["benchmark_aggregate_summary_file_missing"]
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return ["benchmark_aggregate_summary_unreadable"]
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return ["benchmark_aggregate_summary_json"]
    return validate_benchmark_aggregate_summary_dict(parsed)
