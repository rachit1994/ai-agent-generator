"""Write deterministic replay fail-closed artifact."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from event_sourced_architecture.replay_fail_closed import (
    build_replay_fail_closed,
    validate_replay_fail_closed_dict,
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
            body = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(body, dict):
            rows.append(body)
    return rows


def write_replay_fail_closed_artifact(*, output_dir: Path, run_id: str) -> dict[str, Any]:
    payload = build_replay_fail_closed(
        run_id=run_id,
        replay_manifest=_read_json_or_empty(output_dir / "replay_manifest.json"),
        trace_rows=_read_jsonl_rows(output_dir / "traces.jsonl"),
        event_rows=_read_jsonl_rows(output_dir / "event_store" / "run_events.jsonl"),
    )
    errs = validate_replay_fail_closed_dict(payload)
    if errs:
        raise ValueError(f"replay_fail_closed_contract:{','.join(errs)}")
    ensure_dir(output_dir / "replay")
    write_json(output_dir / "replay" / "fail_closed.json", payload)
    return payload
