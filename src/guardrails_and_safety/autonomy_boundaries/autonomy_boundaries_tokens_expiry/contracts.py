"""Contracts for autonomy-boundaries token/expiry artifacts."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from guardrails_and_safety.risk_budgets_permission_matrix.time_and_budget.time_util import parse_iso_utc

AUTONOMY_BOUNDARIES_CONTRACT = "sde.autonomy_boundaries_tokens_expiry.v1"
AUTONOMY_BOUNDARIES_SCHEMA_VERSION = "1.0"
AUTONOMY_BOUNDARIES_ERROR_PREFIX = "autonomy_boundaries_contract:"
VALID_BUDGET_STATUSES = ("ok", "fail_closed")


def _safe_int(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        raw = value.strip()
        if raw.startswith(("+", "-")):
            sign = raw[0]
            digits = raw[1:]
            if digits.isdigit():
                return int(sign + digits)
            return None
        if raw.isdigit():
            return int(raw)
        return None
    return None


def validate_stage_budget_row(row: Any) -> list[str]:
    if not isinstance(row, dict):
        return ["token_context_stage_not_object"]
    errs: list[str] = []
    budget_status = row.get("budget_status")
    if budget_status not in VALID_BUDGET_STATUSES:
        errs.append("token_context_stage_budget_status")
    int_fields = (
        "input_token_budget",
        "output_token_budget",
        "planned_input_tokens",
        "actual_input_tokens",
        "actual_output_tokens",
    )
    parsed: dict[str, int] = {}
    for field in int_fields:
        val = _safe_int(row.get(field))
        if val is None:
            errs.append(f"token_context_stage_int:{field}")
            continue
        parsed[field] = val
        if val < 0:
            errs.append(f"token_context_stage_negative:{field}")
    if errs:
        return errs
    return errs


def validate_high_risk_approval_token_row(row: Any, *, now_utc: datetime) -> list[str]:
    if not isinstance(row, dict):
        return ["approval_token_row_not_object"]
    risk_value = str(row.get("risk", "")).strip().lower()
    if risk_value != "high":
        return []
    errs: list[str] = []
    token_id = row.get("approval_token_id")
    if not isinstance(token_id, str) or not token_id.strip():
        errs.append("approval_token_id")
    raw_exp = row.get("approval_token_expires_at")
    if raw_exp is None or str(raw_exp).strip() == "":
        errs.append("approval_token_expires_at_missing")
        return errs
    exp = parse_iso_utc(str(raw_exp).strip())
    if exp is None:
        errs.append("approval_token_expires_at_invalid")
        return errs
    if exp < now_utc:
        errs.append("approval_token_expired")
    return errs


def validate_token_context_payload(body: Any, *, now_utc: datetime) -> list[str]:
    if not isinstance(body, dict):
        return ["token_context_not_object"]
    errs: list[str] = []
    run_id = body.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errs.append("token_context_run_id")
    anchor_raw = body.get("autonomy_anchor_at")
    expiry_raw = body.get("context_expires_at")
    anchor = parse_iso_utc(str(anchor_raw).strip()) if isinstance(anchor_raw, str) and anchor_raw.strip() else None
    expiry = parse_iso_utc(str(expiry_raw).strip()) if isinstance(expiry_raw, str) and expiry_raw.strip() else None
    if anchor is None:
        errs.append("token_context_autonomy_anchor_at")
    if expiry is None:
        errs.append("token_context_context_expires_at")
    ttl = _safe_int(body.get("context_ttl_seconds"))
    if ttl is None:
        errs.append("token_context_context_ttl_seconds")
    elif ttl <= 0:
        errs.append("token_context_context_ttl_seconds_range")
    stages = body.get("stages")
    if not isinstance(stages, list):
        errs.append("token_context_stages")
        stages = []
    for idx, row in enumerate(stages, start=1):
        for token in validate_stage_budget_row(row):
            errs.append(f"{token}:{idx}")
    if anchor is not None and expiry is not None:
        if expiry < anchor:
            errs.append("token_context_expiry_before_anchor")
        if expiry < now_utc:
            errs.append("token_context_expired")
    return errs


def validate_autonomy_boundaries_runtime_dict(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["autonomy_boundaries_not_object"]
    errs: list[str] = []
    if body.get("schema") != AUTONOMY_BOUNDARIES_CONTRACT:
        errs.append("autonomy_boundaries_schema")
    if body.get("schema_version") != AUTONOMY_BOUNDARIES_SCHEMA_VERSION:
        errs.append("autonomy_boundaries_schema_version")
    run_id = body.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errs.append("autonomy_boundaries_run_id")
    token_context = body.get("token_context")
    now = datetime(9999, 12, 31, 23, 59, 59, tzinfo=timezone.utc)
    # Runtime artifact validity checks shape/ordering only; expiry-at-now is checked by HS06.
    if isinstance(token_context, dict):
        token_context_run_id = token_context.get("run_id")
        if (
            isinstance(run_id, str)
            and run_id.strip()
            and (not isinstance(token_context_run_id, str) or token_context_run_id.strip() != run_id.strip())
        ):
            errs.append("autonomy_boundaries_run_id_mismatch")
        errs.extend(
            token
            for token in validate_token_context_payload(token_context, now_utc=now)
            if token != "token_context_expired"
        )
    else:
        errs.append("token_context_not_object")
    evidence = body.get("evidence")
    if not isinstance(evidence, dict):
        errs.append("autonomy_boundaries_evidence")
    else:
        for key in ("token_context_ref",):
            value = evidence.get(key)
            if not isinstance(value, str) or not value.strip():
                errs.append(f"autonomy_boundaries_evidence_ref:{key}")
    return errs


def validate_autonomy_boundaries_runtime_path(path: Path) -> list[str]:
    if not path.is_file():
        return ["autonomy_boundaries_file_missing"]
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ["autonomy_boundaries_json"]
    return validate_autonomy_boundaries_runtime_dict(body)
