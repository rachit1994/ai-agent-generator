"""Stage 1 observability JSON export (OSV-STORY-01 B4: doc_review / revise metrics)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from time_and_budget.time_util import iso_now

from .project_status import describe_project_session

STAGE1_OBSERVABILITY_EXPORT_SCHEMA_VERSION = "1.0"
STAGE1_OBSERVABILITY_EXPORT_KIND = "project_stage1_observability"
DEFAULT_RELATIVE_EXPORT_PATH = "intake/stage1_observability_export.json"


def build_project_stage1_observability_export(
    session_dir: Path,
    *,
    repo_root: Path | None = None,
    progress_file: Path | None = None,
    max_concurrent_agents: int = 1,
    max_status_json_bytes: int | None = None,
    max_status_jsonl_full_scan_bytes: int | None = None,
    max_status_jsonl_tail_bytes: int | None = None,
    max_status_listed_step_ids: int | None = None,
) -> dict[str, Any]:
    """Return a versioned dict suitable for JSON export (no disk writes)."""
    root = session_dir.resolve()
    snap = describe_project_session(
        root,
        repo_root=repo_root,
        progress_file=progress_file,
        max_concurrent_agents=max_concurrent_agents,
        max_status_json_bytes=max_status_json_bytes,
        max_status_jsonl_full_scan_bytes=max_status_jsonl_full_scan_bytes,
        max_status_jsonl_tail_bytes=max_status_jsonl_tail_bytes,
        max_status_listed_step_ids=max_status_listed_step_ids,
    )
    revise = snap.get("revise_metrics")
    glance = snap.get("status_at_a_glance")
    return {
        "schema_version": STAGE1_OBSERVABILITY_EXPORT_SCHEMA_VERSION,
        "kind": STAGE1_OBSERVABILITY_EXPORT_KIND,
        "captured_at": iso_now(),
        "session_dir": str(root),
        "revise_metrics": revise if isinstance(revise, dict) else {},
        "status_at_a_glance": glance if isinstance(glance, dict) else {},
    }


def stage1_observability_export_schema_errors(body: Any) -> list[str]:
    """Return human-stable error codes; empty list means the export matches the v1 contract."""
    if not isinstance(body, dict):
        return ["root_not_object"]
    reasons: list[str] = []
    if body.get("schema_version") != STAGE1_OBSERVABILITY_EXPORT_SCHEMA_VERSION:
        reasons.append("schema_version_invalid")
    if body.get("kind") != STAGE1_OBSERVABILITY_EXPORT_KIND:
        reasons.append("kind_invalid")
    cap = body.get("captured_at")
    if not isinstance(cap, str) or not cap.strip():
        reasons.append("captured_at_invalid")
    sd = body.get("session_dir")
    if not isinstance(sd, str) or not sd.strip():
        reasons.append("session_dir_invalid")
    if not isinstance(body.get("revise_metrics"), dict):
        reasons.append("revise_metrics_invalid")
    if not isinstance(body.get("status_at_a_glance"), dict):
        reasons.append("status_at_a_glance_invalid")
    return reasons


def write_project_stage1_observability_export(
    session_dir: Path,
    *,
    output_path: Path | None = None,
    repo_root: Path | None = None,
    progress_file: Path | None = None,
    max_concurrent_agents: int = 1,
    max_status_json_bytes: int | None = None,
    max_status_jsonl_full_scan_bytes: int | None = None,
    max_status_jsonl_tail_bytes: int | None = None,
    max_status_listed_step_ids: int | None = None,
) -> dict[str, Any]:
    """Write ``intake/stage1_observability_export.json`` (or ``output_path``) with a stable schema."""
    root = session_dir.resolve()
    body = build_project_stage1_observability_export(
        root,
        repo_root=repo_root,
        progress_file=progress_file,
        max_concurrent_agents=max_concurrent_agents,
        max_status_json_bytes=max_status_json_bytes,
        max_status_jsonl_full_scan_bytes=max_status_jsonl_full_scan_bytes,
        max_status_jsonl_tail_bytes=max_status_jsonl_tail_bytes,
        max_status_listed_step_ids=max_status_listed_step_ids,
    )
    errs = stage1_observability_export_schema_errors(body)
    if errs:
        return {
            "ok": False,
            "error": "export_body_failed_schema",
            "details": errs,
            "session_dir": str(root),
        }
    dest = output_path if output_path is not None else root / DEFAULT_RELATIVE_EXPORT_PATH
    dest = dest.resolve()
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(body, indent=2), encoding="utf-8")
    return {
        "ok": True,
        "path": str(dest),
        "session_dir": str(root),
        "schema_version": body["schema_version"],
    }
