"""Write deterministic implementation-roadmap artifact."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from implementation_roadmap.implementation_roadmap import (
    build_implementation_roadmap,
    validate_implementation_roadmap_dict,
)
from production_architecture.storage.storage.storage import ensure_dir, write_json


def _read_json_or_empty(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    body = json.loads(path.read_text(encoding="utf-8"))
    return body if isinstance(body, dict) else {}


def write_implementation_roadmap_artifact(*, output_dir: Path, run_id: str, mode: str) -> dict[str, Any]:
    payload = build_implementation_roadmap(
        run_id=run_id,
        mode=mode,
        summary=_read_json_or_empty(output_dir / "summary.json"),
        review=_read_json_or_empty(output_dir / "review.json"),
        production_readiness=_read_json_or_empty(output_dir / "program" / "production_readiness.json"),
        topology_layout=_read_json_or_empty(output_dir / "program" / "topology_and_repository_layout.json"),
        consolidated_improvements=_read_json_or_empty(output_dir / "program" / "consolidated_improvements.json"),
        closure_plan=_read_json_or_empty(
            output_dir / "program" / "closure_security_reliability_scalability_plans.json"
        ),
    )
    errs = validate_implementation_roadmap_dict(payload)
    if errs:
        raise ValueError(f"implementation_roadmap_contract:{','.join(errs)}")
    ensure_dir(output_dir / "program")
    write_json(output_dir / "program" / "implementation_roadmap.json", payload)
    return payload
