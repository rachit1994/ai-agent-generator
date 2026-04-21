"""Write deterministic run-manifest runtime artifact."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from production_architecture.storage.storage.storage import ensure_dir, write_json
from workflow_pipelines.run_manifest import (
    build_run_manifest_runtime,
    validate_run_manifest_runtime_dict,
)


def _read_json_or_empty(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    body = json.loads(path.read_text(encoding="utf-8"))
    return body if isinstance(body, dict) else {}


def write_run_manifest_runtime_artifact(*, output_dir: Path) -> dict[str, Any]:
    payload = build_run_manifest_runtime(run_manifest=_read_json_or_empty(output_dir / "run-manifest.json"))
    errs = validate_run_manifest_runtime_dict(payload)
    if errs:
        raise ValueError(f"run_manifest_runtime_contract:{','.join(errs)}")
    ensure_dir(output_dir / "program")
    write_json(output_dir / "program" / "run_manifest_runtime.json", payload)
    return payload
