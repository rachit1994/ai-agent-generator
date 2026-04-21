"""Deterministic retry/repeat-profile runtime derivation."""

from __future__ import annotations

from typing import Any

from .contracts import (
    RETRY_REPEAT_PROFILE_RUNTIME_CONTRACT,
    RETRY_REPEAT_PROFILE_RUNTIME_SCHEMA_VERSION,
)


def build_retry_repeat_profile_runtime(
    *,
    run_id: str,
    repeat: int,
    attempts: list[dict[str, Any]],
    all_runs_no_pipeline_error: bool,
    validation_ready_all: bool,
) -> dict[str, Any]:
    if repeat <= 1:
        status = "single"
    elif all_runs_no_pipeline_error and validation_ready_all:
        status = "repeat_ok"
    else:
        status = "repeat_degraded"
    return {
        "schema": RETRY_REPEAT_PROFILE_RUNTIME_CONTRACT,
        "schema_version": RETRY_REPEAT_PROFILE_RUNTIME_SCHEMA_VERSION,
        "run_id": run_id,
        "repeat": repeat,
        "status": status,
        "metrics": {
            "attempt_count": len(attempts),
            "all_runs_no_pipeline_error": all_runs_no_pipeline_error,
            "validation_ready_all": validation_ready_all,
        },
        "evidence": {
            "run_manifest_ref": "run-manifest.json",
            "runtime_ref": "program/retry_repeat_profile_runtime.json",
        },
    }
