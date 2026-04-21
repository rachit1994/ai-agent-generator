"""Write deterministic consolidated improvements artifact."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from implementation_roadmap.consolidated_improvements import (
    build_consolidated_improvements,
    validate_consolidated_improvements_dict,
)
from production_architecture.storage.storage.storage import ensure_dir, write_json


def _read_json_or_empty(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    body = json.loads(path.read_text(encoding="utf-8"))
    return body if isinstance(body, dict) else {}


def write_consolidated_improvements_artifact(
    *,
    output_dir: Path,
    run_id: str,
    mode: str,
) -> dict[str, Any]:
    payload = build_consolidated_improvements(
        run_id=run_id,
        mode=mode,
        summary=_read_json_or_empty(output_dir / "summary.json"),
        review=_read_json_or_empty(output_dir / "review.json"),
        readiness=_read_json_or_empty(output_dir / "program" / "production_readiness.json"),
        scalability=_read_json_or_empty(output_dir / "strategy" / "scalability_strategy.json"),
        boundaries=_read_json_or_empty(output_dir / "strategy" / "service_boundaries.json"),
        storage=_read_json_or_empty(output_dir / "storage" / "storage_architecture.json"),
        learning_metrics={
            "capability_growth_metrics": _read_json_or_empty(output_dir / "learning" / "capability_growth_metrics.json"),
            "error_reduction_metrics": _read_json_or_empty(output_dir / "learning" / "error_reduction_metrics.json"),
            "extended_binary_gates": _read_json_or_empty(output_dir / "learning" / "extended_binary_gates.json"),
            "transfer_learning_metrics": _read_json_or_empty(output_dir / "learning" / "transfer_learning_metrics.json"),
        },
    )
    errs = validate_consolidated_improvements_dict(payload)
    if errs:
        raise ValueError(f"consolidated_improvements_contract:{','.join(errs)}")
    ensure_dir(output_dir / "program")
    write_json(output_dir / "program" / "consolidated_improvements.json", payload)
    return payload

