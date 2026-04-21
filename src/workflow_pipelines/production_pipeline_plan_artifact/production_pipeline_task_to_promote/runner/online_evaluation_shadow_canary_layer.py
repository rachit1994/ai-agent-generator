"""Write deterministic online-evaluation shadow/canary artifact."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from evaluation_framework.online_evaluation_shadow_canary_artifact import (
    build_online_evaluation_shadow_canary,
    validate_online_evaluation_shadow_canary_dict,
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
        row = json.loads(line)
        if isinstance(row, dict):
            rows.append(row)
    return rows


def write_online_evaluation_shadow_canary_artifact(
    *,
    output_dir: Path,
    run_id: str,
) -> dict[str, Any]:
    payload = build_online_evaluation_shadow_canary(
        run_id=run_id,
        canary_report=_read_json_or_empty(output_dir / "learning" / "canary_report.json"),
        events=_read_trace_events(output_dir / "traces.jsonl"),
    )
    errs = validate_online_evaluation_shadow_canary_dict(payload)
    if errs:
        raise ValueError(f"online_evaluation_shadow_canary_contract:{','.join(errs)}")
    ensure_dir(output_dir / "learning")
    write_json(output_dir / "learning" / "online_evaluation_shadow_canary.json", payload)
    return payload
