"""Contracts for replay fail-closed artifact."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REPLAY_FAIL_CLOSED_CONTRACT = "sde.replay_fail_closed.v1"
REPLAY_FAIL_CLOSED_SCHEMA_VERSION = "1.0"


def validate_replay_fail_closed_dict(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["replay_fail_closed_not_object"]
    errs: list[str] = []
    if body.get("schema") != REPLAY_FAIL_CLOSED_CONTRACT:
        errs.append("replay_fail_closed_schema")
    if body.get("schema_version") != REPLAY_FAIL_CLOSED_SCHEMA_VERSION:
        errs.append("replay_fail_closed_schema_version")
    run_id = body.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errs.append("replay_fail_closed_run_id")
    status = body.get("status")
    if status not in ("pass", "fail"):
        errs.append("replay_fail_closed_status")
    checks = body.get("checks")
    if not isinstance(checks, dict):
        errs.append("replay_fail_closed_checks")
    else:
        for key in (
            "replay_manifest_present",
            "trace_rows_present",
            "event_rows_present",
            "chain_root_present",
            "chain_root_matches_trace_hash",
        ):
            if not isinstance(checks.get(key), bool):
                errs.append(f"replay_fail_closed_check_type:{key}")
    return errs


def validate_replay_fail_closed_path(path: Path) -> list[str]:
    if not path.is_file():
        return ["replay_fail_closed_file_missing"]
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ["replay_fail_closed_json"]
    return validate_replay_fail_closed_dict(body)
