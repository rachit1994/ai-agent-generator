"""Write deterministic topology and repository layout artifact."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from implementation_roadmap.topology_and_repository_layout import (
    build_topology_and_repository_layout,
    validate_topology_and_repository_layout_dict,
)
from production_architecture.storage.storage.storage import ensure_dir, write_json


def _read_json_or_empty(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    body = json.loads(path.read_text(encoding="utf-8"))
    return body if isinstance(body, dict) else {}


def write_topology_and_repository_layout_artifact(
    *,
    output_dir: Path,
    run_id: str,
    mode: str,
) -> dict[str, Any]:
    review = _read_json_or_empty(output_dir / "review.json")
    artifact_manifest = review.get("artifact_manifest")
    if not isinstance(artifact_manifest, list):
        artifact_manifest = []
    payload = build_topology_and_repository_layout(
        run_id=run_id,
        mode=mode,
        artifact_manifest=artifact_manifest,
    )
    errs = validate_topology_and_repository_layout_dict(payload)
    if errs:
        raise ValueError(f"topology_and_repository_layout_contract:{','.join(errs)}")
    ensure_dir(output_dir / "program")
    write_json(output_dir / "program" / "topology_and_repository_layout.json", payload)
    return payload

