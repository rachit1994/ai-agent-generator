"""Write deterministic full build order progression artifact."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from production_architecture.storage.storage.storage import ensure_dir, write_json
from scalability_strategy.full_build_order_progression import (
    build_full_build_order_progression,
    validate_full_build_order_progression_dict,
)


def _read_orchestration_events(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    out: list[dict[str, Any]] = []
    for index, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"full_build_order_progression_orchestration_jsonl:line_{index}:invalid_json"
            ) from exc
        if not isinstance(row, dict):
            raise ValueError(
                f"full_build_order_progression_orchestration_jsonl:line_{index}:non_object"
            )
        out.append(row)
    return out


def write_full_build_order_progression_artifact(
    *,
    output_dir: Path,
    run_id: str,
    mode: str,
) -> dict[str, Any]:
    payload = build_full_build_order_progression(
        run_id=run_id,
        mode=mode,
        orchestration_events=_read_orchestration_events(output_dir / "orchestration.jsonl"),
    )
    errs = validate_full_build_order_progression_dict(payload)
    if errs:
        raise ValueError(f"full_build_order_progression_contract:{','.join(errs)}")
    ensure_dir(output_dir / "strategy")
    write_json(output_dir / "strategy" / "full_build_order_progression.json", payload)
    return payload

