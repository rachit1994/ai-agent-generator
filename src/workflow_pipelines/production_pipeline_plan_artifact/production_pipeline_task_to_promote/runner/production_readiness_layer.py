"""Write production-readiness artifact from computed run outputs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from guardrails_and_safety.risk_budgets_permission_matrix.gates_manifest.manifest import all_required_execution_paths, manifest_entries
from implementation_roadmap.production_readiness_program import (
    build_production_readiness_program,
    validate_production_readiness_program_dict,
)
from production_architecture.storage.storage.storage import ensure_dir, write_json


def write_production_readiness_artifact(
    *,
    output_dir: Path,
    run_id: str,
    mode: str,
    cto: dict[str, Any],
) -> dict[str, Any]:
    summary = json.loads((output_dir / "summary.json").read_text(encoding="utf-8"))
    review = json.loads((output_dir / "review.json").read_text(encoding="utf-8"))
    required = all_required_execution_paths(mode, output_dir)
    entries = manifest_entries(output_dir, required)
    payload = build_production_readiness_program(
        run_id=run_id,
        mode=mode,
        summary=summary if isinstance(summary, dict) else {},
        review=review if isinstance(review, dict) else {},
        hard_stops=cto.get("hard_stops") if isinstance(cto.get("hard_stops"), list) else [],
        artifact_paths=entries,
    )
    errs = validate_production_readiness_program_dict(payload)
    if errs:
        raise ValueError(f"production_readiness_program_contract:{','.join(errs)}")
    ensure_dir(output_dir / "program")
    write_json(output_dir / "program" / "production_readiness.json", payload)
    return payload

