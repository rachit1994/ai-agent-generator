"""Contracts for ``run_benchmark`` ``orchestration.jsonl`` lines (resume + error)."""

from __future__ import annotations

from typing import Any, Final

ORCHESTRATION_BENCHMARK_RESUME_CONTRACT: Final = "sde.orchestration_benchmark_resume.v1"
ORCHESTRATION_BENCHMARK_ERROR_CONTRACT: Final = "sde.orchestration_benchmark_error.v1"


def _errs_benchmark_resume_run_id(body: dict[str, Any]) -> list[str]:
    rid = body.get("run_id")
    if not isinstance(rid, str) or not rid.strip():
        return ["orchestration_benchmark_resume_run_id"]
    return []


def _errs_benchmark_resume_type(body: dict[str, Any]) -> list[str]:
    if body.get("type") != "benchmark_resume":
        return ["orchestration_benchmark_resume_type"]
    return []


def _errs_benchmark_resume_pending(body: dict[str, Any]) -> list[str]:
    n = body.get("pending_task_count")
    if not isinstance(n, int) or n < 0:
        return ["orchestration_benchmark_resume_pending_task_count"]
    return []


def validate_orchestration_benchmark_resume_dict(body: Any) -> list[str]:
    """Return stable error tokens for a ``benchmark_resume`` orchestration line."""
    if not isinstance(body, dict):
        return ["orchestration_benchmark_resume_not_object"]
    b = body
    errs: list[str] = []
    errs.extend(_errs_benchmark_resume_run_id(b))
    errs.extend(_errs_benchmark_resume_type(b))
    errs.extend(_errs_benchmark_resume_pending(b))
    return errs


def _errs_benchmark_error_run_id(body: dict[str, Any]) -> list[str]:
    rid = body.get("run_id")
    if not isinstance(rid, str) or not rid.strip():
        return ["orchestration_benchmark_error_run_id"]
    return []


def _errs_benchmark_error_type(body: dict[str, Any]) -> list[str]:
    if body.get("type") != "benchmark_error":
        return ["orchestration_benchmark_error_type"]
    return []


def _errs_benchmark_error_fields(body: dict[str, Any]) -> list[str]:
    errs: list[str] = []
    et = body.get("error_type")
    if not isinstance(et, str) or not et.strip():
        errs.append("orchestration_benchmark_error_error_type")
    em = body.get("error_message")
    if not isinstance(em, str):
        errs.append("orchestration_benchmark_error_error_message")
    return errs


def validate_orchestration_benchmark_error_dict(body: Any) -> list[str]:
    """Return stable error tokens for a ``benchmark_error`` orchestration line."""
    if not isinstance(body, dict):
        return ["orchestration_benchmark_error_not_object"]
    b = body
    errs: list[str] = []
    errs.extend(_errs_benchmark_error_run_id(b))
    errs.extend(_errs_benchmark_error_type(b))
    errs.extend(_errs_benchmark_error_fields(b))
    return errs
