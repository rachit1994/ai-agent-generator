"""Structural contract for ``learning/canary_report.json`` (shadow / canary artifact slice of §13 online eval, **HS28**)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Final

ONLINE_EVAL_SHADOW_CONTRACT: Final = "sde.online_eval_shadow.v1"


def _errs_schema_version(body: dict[str, Any]) -> list[str]:
    sv = body.get("schema_version", body.get("schemaVersion"))
    if not isinstance(sv, str) or not sv.strip():
        return ["online_eval_shadow_schema_version"]
    return []


def _errs_shadow_metrics(body: dict[str, Any]) -> list[str]:
    sm = body.get("shadow_metrics", body.get("shadowMetrics"))
    if not isinstance(sm, dict):
        return ["online_eval_shadow_metrics"]
    return []


def _errs_promote_flag(body: dict[str, Any]) -> list[str]:
    if "promote" not in body:
        return ["online_eval_shadow_promote_missing"]
    if not isinstance(body.get("promote"), bool):
        return ["online_eval_shadow_promote_type"]
    return []


def _errs_recorded_at(body: dict[str, Any]) -> list[str]:
    ra = body.get("recorded_at", body.get("recordedAt"))
    if not isinstance(ra, str) or not ra.strip():
        return ["online_eval_shadow_recorded_at"]
    return []


def validate_canary_report_dict(body: Any) -> list[str]:
    """Return stable error tokens; empty means HS28-compatible shadow/canary artifact shape."""
    if not isinstance(body, dict):
        return ["online_eval_shadow_not_object"]
    b = body
    errs: list[str] = []
    errs.extend(_errs_schema_version(b))
    errs.extend(_errs_shadow_metrics(b))
    errs.extend(_errs_promote_flag(b))
    errs.extend(_errs_recorded_at(b))
    return errs


def validate_canary_report_path(path: Path) -> list[str]:
    """Return stable error tokens for JSON on disk (no raise)."""
    if not path.is_file():
        return ["online_eval_shadow_file_missing"]
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return ["online_eval_shadow_unreadable"]
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return ["online_eval_shadow_json"]
    return validate_canary_report_dict(parsed)
