"""Contract for single-task ``run-manifest.json`` (deterministic run anchor for replay / validate)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Final

RUN_MANIFEST_CONTRACT: Final = "sde.run_manifest.v1"

_ALLOWED_MODES: Final = frozenset({"baseline", "guarded_pipeline", "phased_pipeline"})
_ALLOWED_KEYS: Final = frozenset(
    {"schema", "run_id", "mode", "task", "project_step_id", "project_session_dir"}
)


def validate_run_manifest_dict(body: Any) -> list[str]:
    """Return stable error tokens for ``execute_single_task`` / ``replay_rerun`` manifest shape."""
    if not isinstance(body, dict):
        return ["run_manifest_not_object"]
    b = body
    errs: list[str] = []
    sch = b.get("schema")
    if sch != RUN_MANIFEST_CONTRACT:
        errs.append("run_manifest_schema")
    rid = b.get("run_id")
    if not isinstance(rid, str) or not rid.strip():
        errs.append("run_manifest_run_id")
    mode = b.get("mode")
    if mode not in _ALLOWED_MODES:
        errs.append("run_manifest_mode")
    task = b.get("task")
    if not isinstance(task, str) or not task.strip():
        errs.append("run_manifest_task")
    if "project_step_id" in b:
        ps = b.get("project_step_id")
        if not isinstance(ps, str) or not ps.strip():
            errs.append("run_manifest_project_step_id")
    if "project_session_dir" in b:
        pd = b.get("project_session_dir")
        if not isinstance(pd, str) or not pd.strip():
            errs.append("run_manifest_project_session_dir")
    has_step = "project_step_id" in b
    has_session = "project_session_dir" in b
    if has_step != has_session:
        errs.append("run_manifest_project_linkage")
    for key in b:
        if key not in _ALLOWED_KEYS:
            errs.append(f"run_manifest_unknown_key:{key}")
    return errs


def validate_run_manifest_path(path: Path) -> list[str]:
    if not path.is_file():
        return ["run_manifest_file_missing"]
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return ["run_manifest_unreadable"]
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return ["run_manifest_json"]
    return validate_run_manifest_dict(parsed)
