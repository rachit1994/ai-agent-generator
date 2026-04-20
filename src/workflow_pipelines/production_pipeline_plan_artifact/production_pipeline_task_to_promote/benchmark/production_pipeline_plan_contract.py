"""Structural contract for harness ``program/project_plan.json`` (§10 production pipeline slice)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Final

PRODUCTION_PIPELINE_PLAN_CONTRACT: Final = "sde.production_pipeline_plan.v1"


def _errs_plan_version(body: dict[str, Any]) -> list[str]:
    pv = body.get("plan_version", body.get("planVersion"))
    if not isinstance(pv, str) or not pv.strip():
        return ["harness_project_plan_plan_version"]
    return []


def _errs_one_step(row: Any, idx: int) -> list[str]:
    if not isinstance(row, dict):
        return [f"harness_project_plan_step_not_object:{idx}"]
    r = row
    sid = r.get("step_id", r.get("stepId"))
    if not isinstance(sid, str) or not sid.strip():
        return [f"harness_project_plan_step_id:{idx}"]
    dep = r.get("depends_on", r.get("dependsOn"))
    if dep is None:
        dep = []
    if not isinstance(dep, list) or not all(isinstance(x, str) for x in dep):
        return [f"harness_project_plan_depends_on:{idx}"]
    ph = r.get("phase")
    if not isinstance(ph, str) or not ph.strip():
        return [f"harness_project_plan_phase:{idx}"]
    return []


def _errs_steps(body: dict[str, Any]) -> list[str]:
    steps = body.get("steps")
    if not isinstance(steps, list) or len(steps) == 0:
        return ["harness_project_plan_steps"]
    errs: list[str] = []
    for idx, row in enumerate(steps):
        errs.extend(_errs_one_step(row, idx))
    return errs


def validate_harness_project_plan_dict(body: Any) -> list[str]:
    """Return stable error tokens; empty means the harness plan dict is structurally acceptable."""
    if not isinstance(body, dict):
        return ["harness_project_plan_not_object"]
    b = body
    errs: list[str] = []
    errs.extend(_errs_plan_version(b))
    errs.extend(_errs_steps(b))
    return errs


def validate_harness_project_plan_path(path: Path) -> list[str]:
    """Return stable error tokens for JSON on disk (no raise)."""
    if not path.is_file():
        return ["harness_project_plan_file_missing"]
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return ["harness_project_plan_unreadable"]
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return ["harness_project_plan_json"]
    return validate_harness_project_plan_dict(parsed)
