"""Write deterministic core event-store component artifact."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core_components.event_store import (
    build_event_store_component,
    validate_event_store_component_dict,
)
from production_architecture.storage.storage.storage import ensure_dir, write_json


def _read_json_or_empty(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    body = json.loads(path.read_text(encoding="utf-8"))
    return body if isinstance(body, dict) else {}


def _read_jsonl_rows(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(row, dict):
            rows.append(row)
    return rows


def write_event_store_component_artifact(*, output_dir: Path, run_id: str) -> dict[str, Any]:
    payload = build_event_store_component(
        run_id=run_id,
        replay_manifest=_read_json_or_empty(output_dir / "replay_manifest.json"),
        run_events=_read_jsonl_rows(output_dir / "event_store" / "run_events.jsonl"),
        trace_events=_read_jsonl_rows(output_dir / "traces.jsonl"),
        kill_switch_state=_read_json_or_empty(output_dir / "kill_switch_state.json"),
    )
    errs = validate_event_store_component_dict(payload)
    if errs:
        raise ValueError(f"event_store_component_contract:{','.join(errs)}")
    ensure_dir(output_dir / "event_store")
    write_json(output_dir / "event_store" / "component_runtime.json", payload)
    return payload
