"""Write deterministic self-learning-loop artifact."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core_components.self_learning_loop import (
    build_self_learning_loop,
    validate_self_learning_loop_dict,
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
    out: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        body = json.loads(line)
        if isinstance(body, dict):
            out.append(body)
    return out


def write_self_learning_loop_artifact(
    *,
    output_dir: Path,
    run_id: str,
    mode: str,
) -> dict[str, Any]:
    payload = build_self_learning_loop(
        run_id=run_id,
        mode=mode,
        events=_read_trace_events(output_dir / "traces.jsonl"),
        practice_engine=_read_json_or_empty(output_dir / "practice" / "practice_engine.json"),
        transfer_learning_metrics=_read_json_or_empty(
            output_dir / "learning" / "transfer_learning_metrics.json"
        ),
        capability_growth_metrics=_read_json_or_empty(
            output_dir / "learning" / "capability_growth_metrics.json"
        ),
        skill_nodes=_read_json_or_empty(output_dir / "capability" / "skill_nodes.json"),
    )
    errs = validate_self_learning_loop_dict(payload)
    if errs:
        raise ValueError(f"self_learning_loop_contract:{','.join(errs)}")
    ensure_dir(output_dir / "learning")
    write_json(output_dir / "learning" / "self_learning_loop.json", payload)
    return payload
