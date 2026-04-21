"""Contracts for hard release gates artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

HARD_RELEASE_GATES_CONTRACT = "sde.hard_release_gates.v1"
HARD_RELEASE_GATES_SCHEMA_VERSION = "1.0"
_ALLOWED_MODES = {"baseline", "guarded_pipeline", "phased_pipeline"}


def _validate_top_level_fields(body: dict[str, Any]) -> list[str]:
    errs: list[str] = []
    if body.get("schema") != HARD_RELEASE_GATES_CONTRACT:
        errs.append("hard_release_gates_schema")
    if body.get("schema_version") != HARD_RELEASE_GATES_SCHEMA_VERSION:
        errs.append("hard_release_gates_schema_version")
    run_id = body.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errs.append("hard_release_gates_run_id")
    mode = body.get("mode")
    if mode not in _ALLOWED_MODES:
        errs.append("hard_release_gates_mode")
    for key in ("overall_pass", "validation_ready"):
        if not isinstance(body.get(key), bool):
            errs.append(f"hard_release_gates_{key}")
    return errs


def _validate_gates(gates: Any) -> list[str]:
    if not isinstance(gates, dict):
        return ["hard_release_gates_gates"]
    errs: list[str] = []
    for key in ("reliability_gate", "delivery_gate", "governance_gate", "composite_gate"):
        value = gates.get(key)
        if not isinstance(value, bool):
            errs.append(f"hard_release_gates_gate_type:{key}")
    return errs


def _validate_failed_hard_stop_ids(failed_hard_stop_ids: Any) -> list[str]:
    if not isinstance(failed_hard_stop_ids, list):
        return ["hard_release_gates_failed_hard_stop_ids"]
    errs: list[str] = []
    for idx, row in enumerate(failed_hard_stop_ids):
        if not isinstance(row, str) or not row.strip():
            errs.append(f"hard_release_gates_failed_hard_stop_id:{idx}")
    return errs


def _validate_scores(scores: Any) -> list[str]:
    if not isinstance(scores, dict):
        return ["hard_release_gates_scores"]
    errs: list[str] = []
    for key in ("reliability", "delivery", "governance", "composite"):
        value = scores.get(key)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            errs.append(f"hard_release_gates_score_type:{key}")
            continue
        numeric = float(value)
        if numeric < 0.0 or numeric > 100.0:
            errs.append(f"hard_release_gates_score_range:{key}")
    return errs


def validate_hard_release_gates_dict(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["hard_release_gates_not_object"]
    errs = _validate_top_level_fields(body)
    errs.extend(_validate_gates(body.get("gates")))
    errs.extend(_validate_failed_hard_stop_ids(body.get("failed_hard_stop_ids")))
    errs.extend(_validate_scores(body.get("scores")))
    return errs


def validate_hard_release_gates_path(path: Path) -> list[str]:
    if not path.is_file():
        return ["hard_release_gates_file_missing"]
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ["hard_release_gates_json"]
    return validate_hard_release_gates_dict(body)
