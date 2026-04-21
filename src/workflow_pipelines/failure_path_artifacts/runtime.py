"""Deterministic failure-path-artifacts runtime derivation."""

from __future__ import annotations

from typing import Any

from .contracts import FAILURE_PATH_ARTIFACTS_CONTRACT, FAILURE_PATH_ARTIFACTS_SCHEMA_VERSION
from .failure_pipeline_contract import validate_failure_summary_dict, validate_replay_manifest_dict


def build_failure_path_artifacts(
    *,
    run_id: str,
    summary: dict[str, Any],
    replay_manifest: dict[str, Any],
) -> dict[str, Any]:
    summary_present = bool(summary)
    replay_present = bool(replay_manifest)
    summary_valid = summary_present and not validate_failure_summary_dict(summary)
    replay_valid = replay_present and not validate_replay_manifest_dict(replay_manifest)
    status = "ok"
    run_status = summary.get("runStatus")
    partial = bool(summary.get("partial"))
    if run_status == "failed":
        status = "partial_failure" if partial else "failed"
    return {
        "schema": FAILURE_PATH_ARTIFACTS_CONTRACT,
        "schema_version": FAILURE_PATH_ARTIFACTS_SCHEMA_VERSION,
        "run_id": run_id,
        "status": status,
        "checks": {
            "summary_present": summary_present,
            "summary_contract_valid": bool(summary_valid),
            "replay_manifest_present": replay_present,
            "replay_manifest_contract_valid": bool(replay_valid),
        },
        "evidence": {
            "summary_ref": "summary.json",
            "replay_manifest_ref": "replay_manifest.json",
            "failure_path_artifacts_ref": "replay/failure_path_artifacts.json",
        },
    }
