"""Per-stage token budget snapshot for token_context.json."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta, timezone
from typing import Any

from gates_constants.constants import TOKEN_CONTEXT_SCHEMA


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
    stages_out: list[dict[str, Any]] = []
    for event in events:
        stage = str(event.get("stage", "unknown"))
        ti = int(event.get("token_input", 0) or 0)
        to = int(event.get("token_output", 0) or 0)
        meta = event.get("metadata") if isinstance(event.get("metadata"), dict) else {}
        planned_in = max(len(json.dumps(meta)) // 4, 1)
        budget_in = max_tokens
        budget_out = max_tokens
        over_in = ti > budget_in
        over_out = to > budget_out
        status = "fail_closed" if (over_in or over_out) else "ok"
        stages_out.append(
            {
                "name": stage,
                "input_token_budget": budget_in,
                "output_token_budget": budget_out,
                "planned_input_tokens": planned_in,
                "actual_input_tokens": ti,
                "actual_output_tokens": to,
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
