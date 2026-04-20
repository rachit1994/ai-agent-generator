"""Minimal summary.json when a run fails before full CTO artifacts."""

from __future__ import annotations

from pathlib import Path

from workflow_pipelines.production_pipeline_task_to_promote.config import DEFAULT_CONFIG, config_snapshot
from storage.storage import write_json

from workflow_pipelines.production_pipeline_task_to_promote.benchmark.failure_pipeline_contract import (
    validate_failure_summary_dict,
)


def write_failure_summary(
    output_dir: Path,
    run_id: str,
    mode: str,
    exc: BaseException,
    *,
    partial: bool,
) -> None:
    summary_body = {
        "runId": run_id,
        "mode": mode,
        "runStatus": "failed",
        "partial": partial,
        "error": {"type": type(exc).__name__, "message": str(exc)},
        "provider": DEFAULT_CONFIG.provider,
        "model": DEFAULT_CONFIG.implementation_model,
    }
    sum_errs = validate_failure_summary_dict(summary_body)
    if sum_errs:
        raise ValueError(f"failure_pipeline_contract:{','.join(sum_errs)}")
    write_json(output_dir / "summary.json", summary_body)
    write_json(output_dir / "config-snapshot.json", config_snapshot())
