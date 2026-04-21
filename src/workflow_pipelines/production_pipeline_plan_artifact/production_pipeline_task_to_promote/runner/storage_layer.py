"""Write deterministic storage architecture artifact."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from production_architecture.storage import (
    build_storage_architecture,
    validate_storage_architecture_dict,
)
from production_architecture.storage.storage.storage import ensure_dir, write_json


def _read_json_or_empty(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    body = json.loads(path.read_text(encoding="utf-8"))
    return body if isinstance(body, dict) else {}


def _read_jsonl_or_empty(path: Path) -> list[dict[str, Any]]:
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


def write_storage_architecture_artifact(
    *,
    output_dir: Path,
    run_id: str,
    mode: str,
) -> dict[str, Any]:
    review = _read_json_or_empty(output_dir / "review.json")
    artifact_manifest = review.get("artifact_manifest")
    if not isinstance(artifact_manifest, list):
        artifact_manifest = []
    payload = build_storage_architecture(
        run_id=run_id,
        mode=mode,
        artifact_manifest=artifact_manifest,
        event_envelopes=_read_jsonl_or_empty(output_dir / "event_store" / "run_events.jsonl"),
        retrieval_bundle=_read_json_or_empty(output_dir / "memory" / "retrieval_bundle.json"),
        quality_metrics=_read_json_or_empty(output_dir / "memory" / "quality_metrics.json"),
    )
    errs = validate_storage_architecture_dict(payload)
    if errs:
        raise ValueError(f"storage_architecture_contract:{','.join(errs)}")
    ensure_dir(output_dir / "storage")
    write_json(output_dir / "storage" / "storage_architecture.json", payload)
    return payload

