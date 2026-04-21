"""Write deterministic promotion-evaluation artifact."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from evaluation_framework.promotion_evaluation import (
    build_promotion_evaluation,
    validate_promotion_evaluation_dict,
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
        try:
            body = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(body, dict):
            rows.append(body)
    return rows


def write_promotion_evaluation_artifact(*, output_dir: Path, run_id: str) -> dict[str, Any]:
    payload = build_promotion_evaluation(
        run_id=run_id,
        promotion_package=_read_json_or_empty(output_dir / "lifecycle" / "promotion_package.json"),
        review=_read_json_or_empty(output_dir / "review.json"),
        events=_read_trace_events(output_dir / "traces.jsonl"),
    )
    errs = validate_promotion_evaluation_dict(payload)
    if errs:
        raise ValueError(f"promotion_evaluation_contract:{','.join(errs)}")
    ensure_dir(output_dir / "learning")
    write_json(output_dir / "learning" / "promotion_evaluation.json", payload)
    return payload
