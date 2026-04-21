"""Write deterministic event-store semantics artifact."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from event_sourced_architecture.event_store import (
    build_event_store_semantics,
    validate_event_store_semantics_dict,
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
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            body = json.loads(line)
        except json.JSONDecodeError:
            raise ValueError(f"event_store_semantics_jsonl_invalid:{path}:{line_no}")
        if not isinstance(body, dict):
            raise ValueError(f"event_store_semantics_jsonl_row_not_object:{path}:{line_no}")
        rows.append(body)
    return rows


def write_event_store_semantics_artifact(*, output_dir: Path, run_id: str) -> dict[str, Any]:
    payload = build_event_store_semantics(
        run_id=run_id,
        replay_manifest=_read_json_or_empty(output_dir / "replay_manifest.json"),
        run_events=_read_jsonl_rows(output_dir / "event_store" / "run_events.jsonl"),
        trace_events=_read_jsonl_rows(output_dir / "traces.jsonl"),
    )
    errs = validate_event_store_semantics_dict(payload)
    if errs:
        raise ValueError(f"event_store_semantics_contract:{','.join(errs)}")
    ensure_dir(output_dir / "event_store")
    write_json(output_dir / "event_store" / "semantics.json", payload)
    return payload
