"""Write deterministic learning-service artifact."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core_components.learning_service import (
    build_learning_service,
    validate_learning_service_dict,
)
from production_architecture.storage.storage.storage import ensure_dir, write_json


def _read_json_or_empty(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    body = json.loads(path.read_text(encoding="utf-8"))
    return body if isinstance(body, dict) else {}


def _read_trace_events(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            body = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(body, dict):
            rows.append(body)
    return rows


def write_learning_service_artifact(*, output_dir: Path, run_id: str, mode: str) -> dict[str, Any]:
    payload = build_learning_service(
        run_id=run_id,
        mode=mode,
        reflection_bundle=_read_json_or_empty(output_dir / "learning" / "reflection_bundle.json"),
        canary_report=_read_json_or_empty(output_dir / "learning" / "canary_report.json"),
        events=_read_trace_events(output_dir / "traces.jsonl"),
    )
    errs = validate_learning_service_dict(payload)
    if errs:
        raise ValueError(f"learning_service_contract:{','.join(errs)}")
    ensure_dir(output_dir / "learning")
    write_json(output_dir / "learning" / "learning_service.json", payload)
    return payload
