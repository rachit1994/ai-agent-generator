"""Minimal summary.json when a run fails before full CTO artifacts."""

from __future__ import annotations

from pathlib import Path

from sde_pipeline.config import DEFAULT_CONFIG, config_snapshot
from sde_foundations.storage import write_json


def write_failure_summary(
    output_dir: Path,
    run_id: str,
    mode: str,
    exc: BaseException,
    *,
    partial: bool,
) -> None:
    write_json(
        output_dir / "summary.json",
        {
            "runId": run_id,
            "mode": mode,
            "runStatus": "failed",
            "partial": partial,
            "error": {"type": type(exc).__name__, "message": str(exc)},
            "provider": DEFAULT_CONFIG.provider,
            "model": DEFAULT_CONFIG.implementation_model,
        },
    )
    write_json(output_dir / "config-snapshot.json", config_snapshot())
