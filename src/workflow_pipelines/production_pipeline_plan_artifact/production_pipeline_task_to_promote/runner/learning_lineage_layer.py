"""Write deterministic learning-lineage artifact."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from event_sourced_architecture.learning_lineage import (
    build_learning_lineage,
    validate_learning_lineage_dict,
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
        row = json.loads(line)
        if isinstance(row, dict):
            rows.append(row)
    return rows


def write_learning_lineage_artifact(
    *,
    output_dir: Path,
    run_id: str,
    mode: str,
) -> dict[str, Any]:
    payload = build_learning_lineage(
        run_id=run_id,
        mode=mode,
        replay_manifest=_read_json_or_empty(output_dir / "replay_manifest.json"),
        run_events=_read_jsonl_rows(output_dir / "event_store" / "run_events.jsonl"),
        reflection_bundle=_read_json_or_empty(output_dir / "learning" / "reflection_bundle.json"),
    )
    errs = validate_learning_lineage_dict(payload)
    if errs:
        raise ValueError(f"learning_lineage_contract:{','.join(errs)}")
    ensure_dir(output_dir / "learning")
    write_json(output_dir / "learning" / "learning_lineage.json", payload)
    return payload
