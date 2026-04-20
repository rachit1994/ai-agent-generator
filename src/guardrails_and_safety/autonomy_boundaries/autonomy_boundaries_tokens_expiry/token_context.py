"""Per-stage token budget snapshot for token_context.json."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta, timezone
from typing import Any

from guardrails_and_safety.risk_budgets_permission_matrix.gates_constants.constants import TOKEN_CONTEXT_SCHEMA


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


def build_token_context(
    run_id: str,
    events: list[dict[str, Any]],
    *,
    max_tokens: int,
    model_context_limit: int = 8192,
    context_ttl_seconds: int = 604_800,
) -> dict[str, Any]:
    policy_items = ["required_instructions", "recent_task_state", "historical_context"]
    policy_hash = hashlib.sha256("|".join(policy_items).encode()).hexdigest()[:16]
    if not isinstance(max_tokens, int) or max_tokens <= 0:
        raise ValueError("max_tokens must be a positive integer")
    if not isinstance(model_context_limit, int) or model_context_limit <= 0:
        raise ValueError("model_context_limit must be a positive integer")
    if not isinstance(context_ttl_seconds, int) or context_ttl_seconds <= 0:
        raise ValueError("context_ttl_seconds must be a positive integer")
    effective_budget = min(max_tokens, model_context_limit)
    stages_out: list[dict[str, Any]] = []
    for event in events:
        stage = str(event.get("stage", "unknown"))
        ti_raw = event.get("token_input", 0)
        to_raw = event.get("token_output", 0)
        ti = _safe_int(ti_raw)
        to = _safe_int(to_raw)
        invalid_tokens = ti is None or to is None
        ti_safe = ti if ti is not None else 0
        to_safe = to if to is not None else 0
        meta = event.get("metadata") if isinstance(event.get("metadata"), dict) else {}
        planned_in = max(len(json.dumps(meta)) // 4, 1)
        budget_in = effective_budget
        budget_out = effective_budget
        over_in = ti_safe > budget_in
        over_out = to_safe > budget_out
        status = "fail_closed" if (invalid_tokens or over_in or over_out) else "ok"
        stages_out.append(
            {
                "name": stage,
                "input_token_budget": budget_in,
                "output_token_budget": budget_out,
                "planned_input_tokens": planned_in,
                "actual_input_tokens": ti_safe,
                "actual_output_tokens": to_safe,
                "budget_status": status,
            }
        )
    anchor = datetime.now(timezone.utc).replace(microsecond=0)
    expires = anchor + timedelta(seconds=int(context_ttl_seconds))
    return {
        "schema_version": TOKEN_CONTEXT_SCHEMA,
        "run_id": run_id,
        "model_context_limit": model_context_limit,
        "stages": stages_out,
        "context_policy": {"priority": policy_items, "version_hash": policy_hash},
        "reductions": [],
        "truncation_events": [],
        "autonomy_anchor_at": anchor.isoformat(),
        "context_expires_at": expires.isoformat(),
        "context_ttl_seconds": int(context_ttl_seconds),
    }
