"""Contract for ``run_error`` lines appended to ``orchestration.jsonl`` (single-task failures)."""

from __future__ import annotations

from typing import Any, Final

ORCHESTRATION_RUN_ERROR_CONTRACT: Final = "sde.orchestration_run_error.v1"

_ALLOWED_KEYS: Final = frozenset({"run_id", "type", "mode", "error_type", "error_message", "detail"})
_ALLOWED_MODES: Final = frozenset({"baseline", "guarded_pipeline", "phased_pipeline"})


def _errs_run_error_unknown_keys(body: dict[str, Any]) -> list[str]:
    extra = set(body.keys()) - _ALLOWED_KEYS
    if extra:
        return ["orchestration_run_error_unknown_keys"]
    return []


def _errs_run_error_run_id(body: dict[str, Any]) -> list[str]:
    rid = body.get("run_id")
    if not isinstance(rid, str) or not rid.strip():
        return ["orchestration_run_error_run_id"]
    return []


def _errs_run_error_type(body: dict[str, Any]) -> list[str]:
    if body.get("type") != "run_error":
        return ["orchestration_run_error_type"]
    return []


def _errs_run_error_mode(body: dict[str, Any]) -> list[str]:
    mode = body.get("mode")
    if mode not in _ALLOWED_MODES:
        return ["orchestration_run_error_mode"]
    return []


def _errs_run_error_message_fields(body: dict[str, Any]) -> list[str]:
    errs: list[str] = []
    et = body.get("error_type")
    if not isinstance(et, str) or not et.strip():
        errs.append("orchestration_run_error_error_type")
    em = body.get("error_message")
    if not isinstance(em, str):
        errs.append("orchestration_run_error_error_message")
    det = body.get("detail")
    if det is not None and (not isinstance(det, str) or not det.strip()):
        errs.append("orchestration_run_error_detail")
    return errs


def validate_orchestration_run_error_dict(body: Any) -> list[str]:
    """Return stable error tokens for a ``run_error`` orchestration line."""
    if not isinstance(body, dict):
        return ["orchestration_run_error_not_object"]
    b = body
    errs: list[str] = []
    errs.extend(_errs_run_error_unknown_keys(b))
    errs.extend(_errs_run_error_run_id(b))
    errs.extend(_errs_run_error_type(b))
    errs.extend(_errs_run_error_mode(b))
    errs.extend(_errs_run_error_message_fields(b))
    return errs
