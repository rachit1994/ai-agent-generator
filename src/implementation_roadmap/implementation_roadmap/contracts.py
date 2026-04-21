"""Contracts for implementation-roadmap artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

IMPLEMENTATION_ROADMAP_CONTRACT = "sde.implementation_roadmap.v1"
IMPLEMENTATION_ROADMAP_SCHEMA_VERSION = "1.0"


def validate_implementation_roadmap_dict(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["implementation_roadmap_not_object"]
    errs: list[str] = []
    if body.get("schema") != IMPLEMENTATION_ROADMAP_CONTRACT:
        errs.append("implementation_roadmap_schema")
    if body.get("schema_version") != IMPLEMENTATION_ROADMAP_SCHEMA_VERSION:
        errs.append("implementation_roadmap_schema_version")
    run_id = body.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errs.append("implementation_roadmap_run_id")
    mode = body.get("mode")
    if mode not in ("guarded_pipeline", "phased_pipeline", "baseline"):
        errs.append("implementation_roadmap_mode")
    status = body.get("status")
    if status not in ("on_track", "at_risk"):
        errs.append("implementation_roadmap_status")
    milestones = body.get("milestones")
    if not isinstance(milestones, dict):
        errs.append("implementation_roadmap_milestones")
    else:
        for key in (
            "production_readiness_present",
            "topology_layout_present",
            "consolidated_improvements_present",
            "closure_plan_present",
        ):
            if not isinstance(milestones.get(key), bool):
                errs.append(f"implementation_roadmap_milestone_type:{key}")
    return errs


def validate_implementation_roadmap_path(path: Path) -> list[str]:
    if not path.is_file():
        return ["implementation_roadmap_file_missing"]
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ["implementation_roadmap_json"]
    return validate_implementation_roadmap_dict(body)
