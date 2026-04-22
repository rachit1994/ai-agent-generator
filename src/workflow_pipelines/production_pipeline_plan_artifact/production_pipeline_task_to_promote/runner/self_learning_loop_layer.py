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
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return {}
    return body if isinstance(body, dict) else {}


def _read_trace_events(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        return []
    out: list[dict[str, Any]] = []
    for line in lines:
        if not line.strip():
            continue
        try:
            body = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(body, dict):
            out.append(body)
    return out


def _write_canonical_self_learning_candidates(
    *,
    output_dir: Path,
    run_id: str,
    events: list[dict[str, Any]],
) -> None:
    ensure_dir(output_dir / "learning")
    rows: list[str] = []
    for idx, row in enumerate(events):
        if not isinstance(row, dict):
            continue
        candidate = {
            "candidate_id": f"{run_id}-candidate-{idx + 1}",
            "run_id": run_id,
            "trace_id": str(row.get("id") or f"trace-{idx + 1}"),
            "event_hash": str(row.get("event_hash") or f"event-{idx + 1}"),
        }
        rows.append(json.dumps(candidate, sort_keys=True))
    (output_dir / "learning" / "self_learning_candidates.jsonl").write_text(
        "\n".join(rows),
        encoding="utf-8",
    )


def write_self_learning_loop_artifact(
    *,
    output_dir: Path,
    run_id: str,
    mode: str,
) -> dict[str, Any]:
    events = _read_trace_events(output_dir / "traces.jsonl")
    _write_canonical_self_learning_candidates(output_dir=output_dir, run_id=run_id, events=events)
    payload = build_self_learning_loop(
        run_id=run_id,
        mode=mode,
        events=events,
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
