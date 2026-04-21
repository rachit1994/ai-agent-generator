"""Write deterministic practice engine artifact."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core_components.practice_engine import build_practice_engine, validate_practice_engine_dict
from production_architecture.storage.storage.storage import ensure_dir, write_json


def _read_json_or_empty(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    body = json.loads(path.read_text(encoding="utf-8"))
    return body if isinstance(body, dict) else {}


def write_practice_engine_artifact(
    *,
    output_dir: Path,
    run_id: str,
) -> dict[str, Any]:
    payload = build_practice_engine(
        run_id=run_id,
        task_spec=_read_json_or_empty(output_dir / "practice" / "task_spec.json"),
        evaluation_result=_read_json_or_empty(output_dir / "practice" / "evaluation_result.json"),
        reflection_bundle=_read_json_or_empty(output_dir / "learning" / "reflection_bundle.json"),
        review=_read_json_or_empty(output_dir / "review.json"),
    )
    errs = validate_practice_engine_dict(payload)
    if errs:
        raise ValueError(f"practice_engine_contract:{','.join(errs)}")
    ensure_dir(output_dir / "practice")
    write_json(output_dir / "practice" / "practice_engine.json", payload)
    return payload

