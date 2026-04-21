"""Write deterministic production-pipeline-plan-artifact summary."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from production_architecture.storage.storage.storage import ensure_dir, write_json
from workflow_pipelines.production_pipeline_plan_artifact import (
    build_production_pipeline_plan_artifact,
    validate_production_pipeline_plan_artifact_dict,
)


def _read_json_or_empty(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    body = json.loads(path.read_text(encoding="utf-8"))
    return body if isinstance(body, dict) else {}


def write_production_pipeline_plan_artifact(
    *,
    output_dir: Path,
    run_id: str,
    mode: str,
) -> dict[str, Any]:
    program_dir = output_dir / "program"
    manifest = {
        "project_plan": (program_dir / "project_plan.json").is_file(),
        "progress": (program_dir / "progress.json").is_file(),
        "work_batch": (program_dir / "work_batch.json").is_file(),
        "discovery": (program_dir / "discovery.json").is_file(),
        "verification_bundle": (program_dir / "verification_bundle.json").is_file(),
    }
    payload = build_production_pipeline_plan_artifact(
        run_id=run_id,
        mode=mode,
        program_manifest=manifest,
        project_plan=_read_json_or_empty(program_dir / "project_plan.json"),
    )
    errs = validate_production_pipeline_plan_artifact_dict(payload)
    if errs:
        raise ValueError(f"production_pipeline_plan_artifact_contract:{','.join(errs)}")
    ensure_dir(program_dir)
    write_json(program_dir / "production_pipeline_plan_artifact.json", payload)
    return payload
