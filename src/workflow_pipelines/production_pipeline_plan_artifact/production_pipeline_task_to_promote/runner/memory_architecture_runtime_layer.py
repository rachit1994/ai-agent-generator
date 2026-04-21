"""Write deterministic runtime memory-architecture artifact."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from production_architecture.memory_architecture_in_runtime import (
    build_memory_architecture_in_runtime,
    validate_memory_architecture_in_runtime_dict,
)
from production_architecture.storage.storage.storage import ensure_dir, write_json


def _read_json_or_empty(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    body = json.loads(path.read_text(encoding="utf-8"))
    return body if isinstance(body, dict) else {}


def _read_lines(path: Path) -> list[str]:
    if not path.is_file():
        return []
    return [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_memory_architecture_in_runtime_artifact(
    *,
    output_dir: Path,
    run_id: str,
) -> dict[str, Any]:
    payload = build_memory_architecture_in_runtime(
        run_id=run_id,
        retrieval_bundle=_read_json_or_empty(output_dir / "memory" / "retrieval_bundle.json"),
        quality_metrics=_read_json_or_empty(output_dir / "memory" / "quality_metrics.json"),
        quarantine_lines=_read_lines(output_dir / "memory" / "quarantine.jsonl"),
    )
    errs = validate_memory_architecture_in_runtime_dict(payload)
    if errs:
        raise ValueError(f"memory_architecture_in_runtime_contract:{','.join(errs)}")
    ensure_dir(output_dir / "memory")
    write_json(output_dir / "memory" / "runtime_memory_architecture.json", payload)
    return payload
