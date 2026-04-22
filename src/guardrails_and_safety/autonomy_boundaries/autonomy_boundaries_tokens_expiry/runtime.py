"""Deterministic autonomy-boundaries runtime payload builder."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .contracts import (
    AUTONOMY_BOUNDARIES_CONTRACT,
    AUTONOMY_BOUNDARIES_SCHEMA_VERSION,
    validate_token_context_payload,
)


def build_autonomy_boundaries_runtime_payload(
    *,
    run_id: str,
    token_context: dict[str, Any],
    now_utc: datetime | None = None,
) -> dict[str, Any]:
    if not isinstance(run_id, str) or not run_id.strip():
        raise ValueError("autonomy_boundaries_run_id")
    if not isinstance(token_context, dict):
        raise ValueError("token_context_not_object")
    normalized_run_id = run_id.strip()
    token_context_run_id = token_context.get("run_id")
    if not isinstance(token_context_run_id, str) or token_context_run_id.strip() != normalized_run_id:
        raise ValueError("autonomy_boundaries_run_id_mismatch")
    current_time = now_utc or datetime.now(timezone.utc)
    errs = validate_token_context_payload(token_context, now_utc=current_time)
    if errs:
        raise ValueError(",".join(errs))
    return {
        "schema": AUTONOMY_BOUNDARIES_CONTRACT,
        "schema_version": AUTONOMY_BOUNDARIES_SCHEMA_VERSION,
        "run_id": normalized_run_id,
        "token_context": token_context,
        "evidence": {
            "token_context_ref": "token_context.json",
        },
    }
