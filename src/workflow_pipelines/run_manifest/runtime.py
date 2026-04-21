"""Deterministic run-manifest runtime derivation."""

from __future__ import annotations

from typing import Any

from .contracts import RUN_MANIFEST_RUNTIME_CONTRACT, RUN_MANIFEST_RUNTIME_SCHEMA_VERSION


def build_run_manifest_runtime(*, run_manifest: dict[str, Any]) -> dict[str, Any]:
    run_id = str(run_manifest.get("run_id") or "").strip()
    has_project_step_id = isinstance(run_manifest.get("project_step_id"), str) and bool(
        str(run_manifest.get("project_step_id")).strip()
    )
    has_project_session_dir = isinstance(run_manifest.get("project_session_dir"), str) and bool(
        str(run_manifest.get("project_session_dir")).strip()
    )
    project_linkage_valid = has_project_step_id == has_project_session_dir
    status = "linked" if (has_project_step_id and has_project_session_dir and project_linkage_valid) else "standalone"
    return {
        "schema": RUN_MANIFEST_RUNTIME_CONTRACT,
        "schema_version": RUN_MANIFEST_RUNTIME_SCHEMA_VERSION,
        "run_id": run_id,
        "status": status,
        "links": {
            "has_project_step_id": has_project_step_id,
            "has_project_session_dir": has_project_session_dir,
            "project_linkage_valid": project_linkage_valid,
        },
        "evidence": {
            "run_manifest_ref": "run-manifest.json",
            "run_manifest_runtime_ref": "program/run_manifest_runtime.json",
        },
    }
