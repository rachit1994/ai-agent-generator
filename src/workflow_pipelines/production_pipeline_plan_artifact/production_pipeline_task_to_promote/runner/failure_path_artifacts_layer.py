"""Write deterministic failure-path-artifacts runtime payload."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from production_architecture.storage.storage.storage import ensure_dir, write_json
from workflow_pipelines.failure_path_artifacts import (
    build_failure_path_artifacts,
    validate_failure_path_artifacts_dict,
)


def _read_json_or_empty(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return body if isinstance(body, dict) else {}


def write_failure_path_artifacts(
    *,
    output_dir: Path,
    run_id: str,
) -> dict[str, Any]:
    payload = build_failure_path_artifacts(
        run_id=run_id,
        summary=_read_json_or_empty(output_dir / "summary.json"),
        replay_manifest=_read_json_or_empty(output_dir / "replay_manifest.json"),
    )
    errs = validate_failure_path_artifacts_dict(payload)
    if errs:
        raise ValueError(f"failure_path_artifacts_contract:{','.join(errs)}")
    ensure_dir(output_dir / "replay")
    write_json(output_dir / "replay" / "failure_path_artifacts.json", payload)
    return payload
