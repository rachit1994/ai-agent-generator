"""Write deterministic retry/repeat-profile runtime artifact."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from production_architecture.storage.storage.storage import ensure_dir, write_json
from workflow_pipelines.retry_repeat_profile import (
    build_retry_repeat_profile_runtime,
    validate_retry_repeat_profile_runtime_dict,
)


def write_retry_repeat_profile_runtime_artifact(
    *,
    output_dir: Path,
    run_id: str,
    repeat: int,
    attempts: list[dict[str, Any]],
    all_runs_no_pipeline_error: bool,
    validation_ready_all: bool,
) -> dict[str, Any]:
    payload = build_retry_repeat_profile_runtime(
        run_id=run_id,
        repeat=repeat,
        attempts=attempts,
        all_runs_no_pipeline_error=all_runs_no_pipeline_error,
        validation_ready_all=validation_ready_all,
    )
    errs = validate_retry_repeat_profile_runtime_dict(payload)
    if errs:
        raise ValueError(f"retry_repeat_profile_runtime_contract:{','.join(errs)}")
    ensure_dir(output_dir / "program")
    write_json(output_dir / "program" / "retry_repeat_profile_runtime.json", payload)
    return payload
