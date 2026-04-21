"""Contracts for run-manifest runtime artifact."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

RUN_MANIFEST_RUNTIME_CONTRACT = "sde.run_manifest_runtime.v1"
RUN_MANIFEST_RUNTIME_SCHEMA_VERSION = "1.0"


def validate_run_manifest_runtime_dict(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["run_manifest_runtime_not_object"]
    errs: list[str] = []
    if body.get("schema") != RUN_MANIFEST_RUNTIME_CONTRACT:
        errs.append("run_manifest_runtime_schema")
    if body.get("schema_version") != RUN_MANIFEST_RUNTIME_SCHEMA_VERSION:
        errs.append("run_manifest_runtime_schema_version")
    run_id = body.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errs.append("run_manifest_runtime_run_id")
    status = body.get("status")
    if status not in ("linked", "standalone"):
        errs.append("run_manifest_runtime_status")
    links = body.get("links")
    if not isinstance(links, dict):
        errs.append("run_manifest_runtime_links")
    else:
        for key in ("has_project_step_id", "has_project_session_dir", "project_linkage_valid"):
            if not isinstance(links.get(key), bool):
                errs.append(f"run_manifest_runtime_link_type:{key}")
    return errs


def validate_run_manifest_runtime_path(path: Path) -> list[str]:
    if not path.is_file():
        return ["run_manifest_runtime_file_missing"]
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ["run_manifest_runtime_json"]
    return validate_run_manifest_runtime_dict(body)
