"""Write deterministic core observability-component runtime artifact."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core_components.observability import (
    build_observability_component,
    validate_observability_component_dict,
)
from production_architecture.storage.storage.storage import ensure_dir, write_json


def _read_json_or_empty(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    body = json.loads(path.read_text(encoding="utf-8"))
    return body if isinstance(body, dict) else {}


def write_observability_component_artifact(*, output_dir: Path, run_id: str) -> dict[str, Any]:
    payload = build_observability_component(
        run_id=run_id,
        production_observability=_read_json_or_empty(
            output_dir / "observability" / "production_observability.json"
        ),
        has_run_log=(output_dir / "run.log").is_file(),
        has_traces=(output_dir / "traces.jsonl").is_file(),
        has_orchestration_log=(output_dir / "orchestration.jsonl").is_file(),
    )
    errs = validate_observability_component_dict(payload)
    if errs:
        raise ValueError(f"observability_component_contract:{','.join(errs)}")
    ensure_dir(output_dir / "observability")
    write_json(output_dir / "observability" / "component_runtime.json", payload)
    return payload
