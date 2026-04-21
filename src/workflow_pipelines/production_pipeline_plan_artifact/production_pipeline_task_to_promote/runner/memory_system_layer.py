"""Write deterministic memory-system artifact."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core_components.memory_system import build_memory_system, validate_memory_system_dict
from production_architecture.storage.storage.storage import ensure_dir, write_json

_MEMORY_SYSTEM_PATH = Path("memory") / "memory_system.json"


def _read_json_object_or_empty(path: Path, *, label: str) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"memory_system_input_json:{label}") from exc
    if not isinstance(body, dict):
        raise ValueError(f"memory_system_input_not_object:{label}")
    return body


def _read_lines(path: Path) -> list[str]:
    if not path.is_file():
        return []
    return path.read_text(encoding="utf-8").splitlines()


def write_memory_system_artifact(*, output_dir: Path, run_id: str) -> dict[str, Any]:
    payload = build_memory_system(
        run_id=run_id,
        retrieval_bundle=_read_json_object_or_empty(
            output_dir / "memory" / "retrieval_bundle.json", label="retrieval_bundle"
        ),
        quality_metrics=_read_json_object_or_empty(
            output_dir / "memory" / "quality_metrics.json", label="quality_metrics"
        ),
        quarantine_rows=_read_lines(output_dir / "memory" / "quarantine.jsonl"),
    )
    errs = validate_memory_system_dict(payload)
    if errs:
        raise ValueError(f"memory_system_contract:{','.join(errs)}")
    ensure_dir(output_dir / "memory")
    write_json(output_dir / _MEMORY_SYSTEM_PATH, payload)
    return payload
