"""Contracts for closure/security/reliability/scalability plans artifact."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

CLOSURE_SECURITY_RELIABILITY_SCALABILITY_PLANS_CONTRACT = (
    "sde.closure_security_reliability_scalability_plans.v1"
)
CLOSURE_SECURITY_RELIABILITY_SCALABILITY_PLANS_SCHEMA_VERSION = "1.0"
_ALLOWED_MODES = {"baseline", "guarded_pipeline", "phased_pipeline"}
_CANONICAL_EVIDENCE_REFS = {
    "summary_ref": "summary.json",
    "review_ref": "review.json",
    "readiness_ref": "program/production_readiness.json",
    "closure_plan_ref": "program/closure_security_reliability_scalability_plans.json",
}


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


def _validate_summary(summary: Any, ready_count: int) -> list[str]:
    if not isinstance(summary, dict):
        return ["closure_security_reliability_scalability_plans_summary"]
    errs: list[str] = []
    plans_ready = summary.get("plans_ready")
    if isinstance(plans_ready, bool) or not isinstance(plans_ready, int) or plans_ready != ready_count:
        errs.append("closure_security_reliability_scalability_plans_summary_plans_ready_mismatch")
    plans_total = summary.get("plans_total")
    if isinstance(plans_total, bool) or not isinstance(plans_total, int) or plans_total != 4:
        errs.append("closure_security_reliability_scalability_plans_summary_plans_total_mismatch")
    overall_score = summary.get("overall_score")
    if isinstance(overall_score, bool) or not isinstance(overall_score, (int, float)):
        errs.append("closure_security_reliability_scalability_plans_summary_overall_score_type")
    else:
        numeric = float(overall_score)
        expected = round(ready_count / 4.0, 4)
        if not math.isfinite(numeric) or abs(numeric - expected) > 1e-4:
            errs.append("closure_security_reliability_scalability_plans_summary_overall_score_mismatch")
    return errs


def _validate_evidence(evidence: Any) -> list[str]:
    if not isinstance(evidence, dict):
        return ["closure_security_reliability_scalability_plans_evidence"]
    errs: list[str] = []
    for key, expected in _CANONICAL_EVIDENCE_REFS.items():
        value = evidence.get(key)
        if not isinstance(value, str) or not value.strip():
            errs.append(f"closure_security_reliability_scalability_plans_evidence_ref:{key}")
            continue
        normalized = value.strip()
        if normalized.startswith("/") or ".." in normalized.split("/") or normalized != expected:
            errs.append(f"closure_security_reliability_scalability_plans_evidence_ref:{key}")
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
    if mode not in _ALLOWED_MODES:
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
    if not errs:
        ready_count = sum(1 for key in ("closure", "security", "reliability", "scalability") if plans[key]["ok"] is True)
        expected_status = "ready" if ready_count == 4 else "not_ready"
        if status != expected_status:
            errs.append("closure_security_reliability_scalability_plans_status_mismatch")
        errs.extend(_validate_summary(body.get("summary"), ready_count))
        errs.extend(_validate_evidence(body.get("evidence")))
    return errs


def validate_closure_security_reliability_scalability_plans_path(path: Path) -> list[str]:
    if not path.is_file():
        return ["closure_security_reliability_scalability_plans_file_missing"]
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ["closure_security_reliability_scalability_plans_json"]
    return validate_closure_security_reliability_scalability_plans_dict(body)

