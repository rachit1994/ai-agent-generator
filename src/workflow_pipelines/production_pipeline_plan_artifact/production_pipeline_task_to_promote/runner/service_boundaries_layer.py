"""Write deterministic service-boundaries artifact."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from production_architecture.storage.storage.storage import ensure_dir, write_json
from service_boundaries import build_service_boundaries, validate_service_boundaries_dict


def write_service_boundaries_artifact(
    *,
    output_dir: Path,
    run_id: str,
    mode: str,
) -> dict[str, Any]:
    review = json.loads((output_dir / "review.json").read_text(encoding="utf-8"))
    artifact_manifest = review.get("artifact_manifest")
    if not isinstance(artifact_manifest, list):
        artifact_manifest = []
    payload = build_service_boundaries(run_id=run_id, mode=mode, artifact_manifest=artifact_manifest)
    errs = validate_service_boundaries_dict(payload)
    if errs:
        raise ValueError(f"service_boundaries_contract:{','.join(errs)}")
    ensure_dir(output_dir / "strategy")
    write_json(output_dir / "strategy" / "service_boundaries.json", payload)
    return payload

