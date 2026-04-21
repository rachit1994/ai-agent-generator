"""Write deterministic auditability artifact."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from event_sourced_architecture.auditability import build_auditability, validate_auditability_dict
from production_architecture.storage.storage.storage import ensure_dir, write_json


def _read_json_or_empty(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    body = json.loads(path.read_text(encoding="utf-8"))
    return body if isinstance(body, dict) else {}


def _read_event_rows(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    rows: list[dict[str, Any]] = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            body = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"auditability_run_events_jsonl_invalid:{path}:{line_no}") from exc
        if not isinstance(body, dict):
            raise ValueError(f"auditability_run_events_row_not_object:{path}:{line_no}")
        rows.append(body)
    return rows


def write_auditability_artifact(
    *,
    output_dir: Path,
    run_id: str,
    mode: str,
) -> dict[str, Any]:
    payload = build_auditability(
        run_id=run_id,
        mode=mode,
        replay_manifest=_read_json_or_empty(output_dir / "replay_manifest.json"),
        run_events=_read_event_rows(output_dir / "event_store" / "run_events.jsonl"),
        kill_switch_state=_read_json_or_empty(output_dir / "kill_switch_state.json"),
        review=_read_json_or_empty(output_dir / "review.json"),
    )
    errs = validate_auditability_dict(payload)
    if errs:
        raise ValueError(f"auditability_contract:{','.join(errs)}")
    ensure_dir(output_dir / "audit")
    write_json(output_dir / "audit" / "auditability.json", payload)
    return payload
