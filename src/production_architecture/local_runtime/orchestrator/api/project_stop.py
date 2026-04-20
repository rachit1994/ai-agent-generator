"""Project session stop policy: exit codes + stop_report.json (Phase 4)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from guardrails_and_safety.risk_budgets_permission_matrix.time_and_budget.time_util import iso_now

STOP_REPORT_FILENAME = "stop_report.json"

# CLI / CI: 0 = green session, 1 = expected stop (block or budget), 2 = invalid or internal
EXIT_SESSION_OK = 0
EXIT_SESSION_BLOCKED_OR_BUDGET = 1
EXIT_SESSION_INVALID = 2


def exit_code_ci_meaning(code: int) -> str:
    if code == EXIT_SESSION_OK:
        return "session_completed_verified"
    if code == EXIT_SESSION_BLOCKED_OR_BUDGET:
        return "session_stopped_blocked_or_budget_exhausted"
    return "session_invalid_or_internal_error"


def write_stop_report(
    session_dir: Path,
    *,
    exit_code: int,
    stopped_reason: str,
    driver_status: str,
    max_steps: int,
    steps_used: int,
    block_detail: str | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Append-only contract for automation: one ``stop_report.json`` overwritten per terminal outcome."""
    body: dict[str, Any] = {
        "schema_version": "1.0",
        "captured_at": iso_now(),
        "exit_code": exit_code,
        "stopped_reason": stopped_reason,
        "driver_status": driver_status,
        "budget": {"max_steps": max_steps, "steps_used": steps_used},
        "block_detail": block_detail,
        "ci": {
            "exit_code_meaning": exit_code_ci_meaning(exit_code),
            "exit_codes": {
                "0": "completed_review_pass — plan graph done and aggregate verification passed",
                "1": "blocked_human | exhausted_budget | dependency_cycle — safe stop, inspect driver_state + progress",
                "2": "missing/invalid plan or unexpected driver end — not a verified session outcome",
            },
        },
    }
    if extra:
        body["extra"] = extra
    dest = session_dir / STOP_REPORT_FILENAME
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(body, indent=2), encoding="utf-8")
    return body
