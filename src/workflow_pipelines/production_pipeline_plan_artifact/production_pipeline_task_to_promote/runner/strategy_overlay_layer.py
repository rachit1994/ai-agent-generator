"""Write deterministic strategy overlay runtime artifact."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from production_architecture.storage.storage.storage import ensure_dir, write_json
from workflow_pipelines.strategy_overlay import (
    build_strategy_overlay_runtime,
    validate_strategy_overlay_runtime_dict,
)


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


def write_strategy_overlay_runtime_artifact(
    *,
    output_dir: Path,
    run_id: str,
    mode: str,
) -> dict[str, Any]:
    payload = build_strategy_overlay_runtime(
        run_id=run_id,
        mode=mode,
        proposal=_read_json_or_empty(output_dir / "strategy" / "proposal.json"),
        events=_read_trace_events(output_dir / "traces.jsonl"),
    )
    errs = validate_strategy_overlay_runtime_dict(payload)
    if errs:
        raise ValueError(f"strategy_overlay_runtime_contract:{','.join(errs)}")
    ensure_dir(output_dir / "strategy")
    write_json(output_dir / "strategy" / "overlay.json", payload)
    return payload
