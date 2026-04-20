"""Session-level verification aggregate and project definition-of-done (Phase 3)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from time_and_budget.time_util import iso_now

from .project_plan import plan_step_ids

VERIFICATION_AGGREGATE_FILENAME = "verification_aggregate.json"


def write_verification_aggregate(session_dir: Path, plan: dict[str, Any]) -> dict[str, Any]:
    """Scan ``verification/<step_id>.json`` for every plan step; write ``verification_aggregate.json``."""
    by_step: dict[str, Any] = {}
    missing: list[str] = []
    plan_ids = plan_step_ids(plan)
    all_passed = True
    for sid in plan_ids:
        p = session_dir / "verification" / f"{sid}.json"
        if not p.is_file():
            by_step[sid] = {"present": False, "passed": None}
            missing.append(sid)
            all_passed = False
            continue
        try:
            body = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError, TypeError):
            by_step[sid] = {"present": True, "passed": False, "error": "invalid_json"}
            all_passed = False
            continue
        passed = bool(body.get("passed"))
        by_step[sid] = {
            "present": True,
            "passed": passed,
            "captured_at": body.get("captured_at"),
            "schema_version": body.get("schema_version"),
        }
        if not passed:
            all_passed = False

    out: dict[str, Any] = {
        "schema_version": "1.0",
        "generated_at": iso_now(),
        "plan_step_ids": plan_ids,
        "steps": by_step,
        "all_steps_verification_passed": all_passed and len(plan_ids) > 0,
        "missing_step_bundles": missing,
    }
    dest = session_dir / VERIFICATION_AGGREGATE_FILENAME
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(out, indent=2), encoding="utf-8")
    return out


def write_project_definition_of_done(
    session_dir: Path,
    plan: dict[str, Any],
    *,
    completed_step_ids: list[str],
    driver_status: str,
    aggregate: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Write ``definition_of_done.json`` for the **session** (orchestrator truth, not per-run ``review.json``)."""
    agg = aggregate if aggregate is not None else _read_verification_aggregate(session_dir)
    if agg is None:
        agg = write_verification_aggregate(session_dir, plan)

    plan_ids = plan_step_ids(plan)
    completed_set = {str(x) for x in completed_step_ids if isinstance(x, str)}
    graph_complete = bool(plan_ids) and completed_set == set(plan_ids)
    ver_all = bool(agg.get("all_steps_verification_passed"))
    missing = agg.get("missing_step_bundles") or []
    ver_evidence_ok = ver_all and len(missing) == 0

    checks: list[dict[str, Any]] = [
        {
            "id": "plan_graph_complete",
            "description": "Every plan step_id completed in progress",
            "required": True,
            "passed": graph_complete,
            "evidence_ref": "progress.json",
        },
        {
            "id": "aggregate_verification",
            "description": "Orchestrator verification bundle per step, all passed",
            "required": True,
            "passed": ver_evidence_ok,
            "evidence_ref": VERIFICATION_AGGREGATE_FILENAME,
        },
    ]
    all_req = all(c["passed"] for c in checks if c.get("required"))
    session_dod_pass = all_req and driver_status == "completed_review_pass"

    body: dict[str, Any] = {
        "schema_version": "1.0",
        "kind": "project_session",
        "driver_status": driver_status,
        "captured_at": iso_now(),
        "checks": checks,
        "all_required_passed": session_dod_pass,
        "plan_step_ids": plan_ids,
        "completed_step_ids": sorted(completed_set),
    }
    (session_dir / "definition_of_done.json").write_text(json.dumps(body, indent=2), encoding="utf-8")
    return body


def _read_verification_aggregate(session_dir: Path) -> dict[str, Any] | None:
    p = session_dir / VERIFICATION_AGGREGATE_FILENAME
    if not p.is_file():
        return None
    try:
        raw = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, TypeError):
        return None
    return raw if isinstance(raw, dict) else None
