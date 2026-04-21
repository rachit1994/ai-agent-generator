"""Contracts for closure/security/reliability/scalability plans artifact."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

CLOSURE_SECURITY_RELIABILITY_SCALABILITY_PLANS_CONTRACT = (
    "sde.closure_security_reliability_scalability_plans.v1"
)
CLOSURE_SECURITY_RELIABILITY_SCALABILITY_PLANS_SCHEMA_VERSION = "1.0"


def _validate_plan_entry(plan_name: str, entry: Any) -> list[str]:
    if not isinstance(entry, dict):
        return [f"closure_security_reliability_scalability_plans_plan_type:{plan_name}"]
    errs: list[str] = []
    ok = entry.get("ok")
    if not isinstance(ok, bool):
        errs.append(f"closure_security_reliability_scalability_plans_plan_ok_type:{plan_name}")
    pstatus = entry.get("status")
    if pstatus not in ("ready", "blocked"):
        errs.append(f"closure_security_reliability_scalability_plans_plan_status:{plan_name}")
    if isinstance(ok, bool) and pstatus in ("ready", "blocked"):
        expected_status = "ready" if ok else "blocked"
        if pstatus != expected_status:
            errs.append(
                f"closure_security_reliability_scalability_plans_plan_status_mismatch:{plan_name}"
            )
    return errs


def validate_closure_security_reliability_scalability_plans_dict(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["closure_security_reliability_scalability_plans_not_object"]
    errs: list[str] = []
    if body.get("schema") != CLOSURE_SECURITY_RELIABILITY_SCALABILITY_PLANS_CONTRACT:
        errs.append("closure_security_reliability_scalability_plans_schema")
    if body.get("schema_version") != CLOSURE_SECURITY_RELIABILITY_SCALABILITY_PLANS_SCHEMA_VERSION:
        errs.append("closure_security_reliability_scalability_plans_schema_version")
    run_id = body.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errs.append("closure_security_reliability_scalability_plans_run_id")
    mode = body.get("mode")
    if not isinstance(mode, str) or not mode.strip():
        errs.append("closure_security_reliability_scalability_plans_mode")
    status = body.get("status")
    if status not in ("ready", "not_ready"):
        errs.append("closure_security_reliability_scalability_plans_status")
    plans = body.get("plans")
    if not isinstance(plans, dict):
        errs.append("closure_security_reliability_scalability_plans_plans")
        return errs
    for key in ("closure", "security", "reliability", "scalability"):
        errs.extend(_validate_plan_entry(plan_name=key, entry=plans.get(key)))
    return errs


def validate_closure_security_reliability_scalability_plans_path(path: Path) -> list[str]:
    if not path.is_file():
        return ["closure_security_reliability_scalability_plans_file_missing"]
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ["closure_security_reliability_scalability_plans_json"]
    return validate_closure_security_reliability_scalability_plans_dict(body)

