"""Write deterministic production orchestration artifact."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from production_architecture.orchestration import (
    build_production_orchestration,
    validate_production_orchestration_dict,
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


def write_production_orchestration_artifact(*, output_dir: Path, run_id: str) -> dict[str, Any]:
    payload = build_production_orchestration(
        run_id=run_id,
        lease_table=_read_json_or_empty(output_dir / "coordination" / "lease_table.json"),
        shard_map=_read_json_or_empty(output_dir / "orchestration" / "shard_map.json"),
    )
    errs = validate_production_orchestration_dict(payload)
    if errs:
        raise ValueError(f"production_orchestration_contract:{','.join(errs)}")
    ensure_dir(output_dir / "orchestration")
    write_json(output_dir / "orchestration" / "production_orchestration.json", payload)
    return payload
