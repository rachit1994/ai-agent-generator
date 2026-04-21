"""Contracts for self-learning loop artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

SELF_LEARNING_LOOP_CONTRACT = "sde.self_learning_loop.v1"
SELF_LEARNING_LOOP_SCHEMA_VERSION = "1.0"
_ALLOWED_MODES = {"baseline", "guarded_pipeline", "phased_pipeline"}
_ALLOWED_LOOP_STATE = {"hold", "iterate", "promote"}


def _validate_signals(signals: Any) -> list[str]:
    if not isinstance(signals, dict):
        return ["self_learning_loop_signals"]
    errs: list[str] = []
    for key in (
        "finalize_pass_rate",
        "capability_score",
        "transfer_efficiency",
        "growth_signal",
        "practice_readiness",
    ):
        value = signals.get(key)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            errs.append(f"self_learning_loop_signal_type:{key}")
            continue
        numeric = float(value)
        if numeric < 0.0 or numeric > 1.0:
            errs.append(f"self_learning_loop_signal_range:{key}")
    return errs


def _validate_decision(decision: Any) -> list[str]:
    if not isinstance(decision, dict):
        return ["self_learning_loop_decision"]
    errs: list[str] = []
    state = decision.get("loop_state")
    if state not in _ALLOWED_LOOP_STATE:
        errs.append("self_learning_loop_loop_state")
    for key in ("next_action", "primary_reason"):
        value = decision.get(key)
        if not isinstance(value, str) or not value.strip():
            errs.append(f"self_learning_loop_decision_{key}")
    return errs


def validate_self_learning_loop_dict(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["self_learning_loop_not_object"]
    errs: list[str] = []
    if body.get("schema") != SELF_LEARNING_LOOP_CONTRACT:
        errs.append("self_learning_loop_schema")
    if body.get("schema_version") != SELF_LEARNING_LOOP_SCHEMA_VERSION:
        errs.append("self_learning_loop_schema_version")
    run_id = body.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errs.append("self_learning_loop_run_id")
    mode = body.get("mode")
    if mode not in _ALLOWED_MODES:
        errs.append("self_learning_loop_mode")
    errs.extend(_validate_signals(body.get("signals")))
    errs.extend(_validate_decision(body.get("decision")))
    return errs


def validate_self_learning_loop_path(path: Path) -> list[str]:
    if not path.is_file():
        return ["self_learning_loop_file_missing"]
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ["self_learning_loop_json"]
    return validate_self_learning_loop_dict(body)
