"""Write deterministic core-orchestrator runtime artifact."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core_components.orchestrator import build_orchestrator_component, validate_orchestrator_component_dict
from production_architecture.storage.storage.storage import ensure_dir, write_json


def _read_json_or_empty(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    body = json.loads(path.read_text(encoding="utf-8"))
    return body if isinstance(body, dict) else {}


def write_orchestrator_component_artifact(*, output_dir: Path, run_id: str) -> dict[str, Any]:
    payload = build_orchestrator_component(
        run_id=run_id,
        run_manifest=_read_json_or_empty(output_dir / "run-manifest.json"),
        run_manifest_runtime=_read_json_or_empty(output_dir / "program" / "run_manifest_runtime.json"),
        has_traces=(output_dir / "traces.jsonl").is_file(),
        has_orchestration_log=(output_dir / "orchestration.jsonl").is_file(),
    )
    errs = validate_orchestrator_component_dict(payload)
    if errs:
        raise ValueError(f"orchestrator_component_contract:{','.join(errs)}")
    ensure_dir(output_dir / "orchestrator")
    write_json(output_dir / "orchestrator" / "component_runtime.json", payload)
    return payload
