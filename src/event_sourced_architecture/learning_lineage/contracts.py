"""Contracts for learning-lineage artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

LEARNING_LINEAGE_CONTRACT = "sde.learning_lineage.v1"
LEARNING_LINEAGE_SCHEMA_VERSION = "1.0"
_ALLOWED_MODES = {"baseline", "guarded_pipeline", "phased_pipeline"}
_ALLOWED_STATUS = {"aligned", "partial", "broken"}


def validate_learning_lineage_dict(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["learning_lineage_not_object"]
    errs: list[str] = []
    if body.get("schema") != LEARNING_LINEAGE_CONTRACT:
        errs.append("learning_lineage_schema")
    if body.get("schema_version") != LEARNING_LINEAGE_SCHEMA_VERSION:
        errs.append("learning_lineage_schema_version")
    run_id = body.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errs.append("learning_lineage_run_id")
    mode = body.get("mode")
    if mode not in _ALLOWED_MODES:
        errs.append("learning_lineage_mode")
    status = body.get("status")
    if status not in _ALLOWED_STATUS:
        errs.append("learning_lineage_status")
    checks = body.get("checks")
    if not isinstance(checks, dict):
        errs.append("learning_lineage_checks")
    else:
        for key in ("manifest_has_chain_root", "event_store_present", "reflection_linked"):
            if not isinstance(checks.get(key), bool):
                errs.append(f"learning_lineage_check_type:{key}")
    coverage = body.get("coverage")
    if isinstance(coverage, bool) or not isinstance(coverage, (int, float)):
        errs.append("learning_lineage_coverage_type")
    elif float(coverage) < 0.0 or float(coverage) > 1.0:
        errs.append("learning_lineage_coverage_range")
    return errs


def validate_learning_lineage_path(path: Path) -> list[str]:
    if not path.is_file():
        return ["learning_lineage_file_missing"]
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ["learning_lineage_json"]
    return validate_learning_lineage_dict(body)
