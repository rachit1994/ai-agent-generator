"""JSON schema validation for SDE project sessions (meta-orchestrator)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .project_workspace import plan_workspace_path_errors


PLAN_SCHEMA_VERSION = "1.0"
PROGRESS_SCHEMA_VERSION = "1.0"


def _is_str_list(x: Any) -> bool:
    return isinstance(x, list) and all(isinstance(i, str) for i in x)


def validate_project_plan(body: dict[str, Any]) -> list[str]:
    errs: list[str] = []
    if body.get("schema_version") != PLAN_SCHEMA_VERSION:
        errs.append("project_plan_bad_schema_version")
    steps = body.get("steps")
    if not isinstance(steps, list) or len(steps) == 0:
        errs.append("project_plan_steps_missing")
        return errs
    seen: set[str] = set()
    for i, row in enumerate(steps):
        if not isinstance(row, dict):
            errs.append(f"project_plan_step_not_object:{i}")
            continue
        sid = row.get("step_id")
        if not isinstance(sid, str) or not sid.strip():
            errs.append(f"project_plan_step_id_missing:{i}")
        elif sid in seen:
            errs.append(f"project_plan_duplicate_step_id:{sid}")
        else:
            seen.add(sid)
        if not isinstance(row.get("title"), str) or not str(row.get("title")).strip():
            errs.append(f"project_plan_title_missing:{sid}")
        desc = row.get("description")
        if not isinstance(desc, str) or not desc.strip():
            errs.append(f"project_plan_description_missing:{sid}")
        dep = row.get("depends_on", [])
        if dep is None:
            dep = []
        if not _is_str_list(dep):
            errs.append(f"project_plan_depends_on_bad:{sid}")
        pscope = row.get("path_scope", [])
        if pscope is None:
            pscope = []
        if not _is_str_list(pscope):
            errs.append(f"project_plan_path_scope_bad:{sid}")
        ver = row.get("verification")
        if ver is not None:
            if not isinstance(ver, dict):
                errs.append(f"project_plan_verification_not_object:{sid}")
            else:
                cmds = ver.get("commands")
                if cmds is not None:
                    if not isinstance(cmds, list):
                        errs.append(f"project_plan_verification_commands_bad:{sid}")
                    else:
                        for j, c in enumerate(cmds):
                            if not isinstance(c, dict) or not isinstance(c.get("cmd"), str):
                                errs.append(f"project_plan_verification_cmd_bad:{sid}:{j}")
    ws = body.get("workspace")
    if ws is not None and not isinstance(ws, dict):
        errs.append("project_plan_workspace_not_object")
    elif isinstance(ws, dict):
        br = ws.get("branch")
        if br is not None and (not isinstance(br, str) or not br.strip()):
            errs.append("project_plan_workspace_branch_bad")
        ap = ws.get("allowed_path_prefixes")
        if ap is not None:
            if not isinstance(ap, list) or not all(isinstance(x, str) and x.strip() for x in ap):
                errs.append("project_plan_workspace_allowed_path_prefixes_bad")
            elif len(ap) == 0:
                errs.append("project_plan_workspace_allowed_path_prefixes_empty")
        lt = ws.get("lease_ttl_sec")
        if lt is not None and (not isinstance(lt, int) or lt < 60):
            errs.append("project_plan_workspace_lease_ttl_sec_bad")
        errs.extend(plan_workspace_path_errors(body))
    return errs


def default_progress(session_id: str) -> dict[str, Any]:
    return {
        "schema_version": PROGRESS_SCHEMA_VERSION,
        "session_id": session_id,
        "completed_step_ids": [],
        "failed_step_id": None,
        "pending_step_ids": [],
        "blocked_reason": None,
        "last_run_id": None,
        "last_output_dir": None,
    }


def validate_progress(body: dict[str, Any]) -> list[str]:
    errs: list[str] = []
    if body.get("schema_version") != PROGRESS_SCHEMA_VERSION:
        errs.append("progress_bad_schema_version")
    for key in ("completed_step_ids", "pending_step_ids"):
        if not _is_str_list(body.get(key, [])):
            errs.append(f"progress_{key}_bad")
    return errs


def read_json_dict(path: Path) -> dict[str, Any]:
    raw = path.read_text(encoding="utf-8")
    body = json.loads(raw)
    if not isinstance(body, dict):
        raise ValueError("json_not_object")
    return body
