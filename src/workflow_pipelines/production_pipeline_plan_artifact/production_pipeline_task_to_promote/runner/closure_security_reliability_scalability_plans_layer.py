"""Write deterministic closure/security/reliability/scalability plans artifact."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from implementation_roadmap.closure_security_reliability_scalability_plans import (
    build_closure_security_reliability_scalability_plans,
    validate_closure_security_reliability_scalability_plans_dict,
)
from production_architecture.storage.storage.storage import ensure_dir, write_json


def _read_json_or_empty(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    body = json.loads(path.read_text(encoding="utf-8"))
    return body if isinstance(body, dict) else {}


def write_closure_security_reliability_scalability_plans_artifact(
    *,
    output_dir: Path,
    run_id: str,
    mode: str,
    policy_bundle_valid: bool,
) -> dict[str, Any]:
    payload = build_closure_security_reliability_scalability_plans(
        run_id=run_id,
        mode=mode,
        summary=_read_json_or_empty(output_dir / "summary.json"),
        review=_read_json_or_empty(output_dir / "review.json"),
        readiness=_read_json_or_empty(output_dir / "program" / "production_readiness.json"),
        scalability=_read_json_or_empty(output_dir / "strategy" / "scalability_strategy.json"),
        boundaries=_read_json_or_empty(output_dir / "strategy" / "service_boundaries.json"),
        storage=_read_json_or_empty(output_dir / "storage" / "storage_architecture.json"),
        policy_bundle_valid=policy_bundle_valid,
    )
    errs = validate_closure_security_reliability_scalability_plans_dict(payload)
    if errs:
        raise ValueError(f"closure_security_reliability_scalability_plans_contract:{','.join(errs)}")
    ensure_dir(output_dir / "program")
    write_json(output_dir / "program" / "closure_security_reliability_scalability_plans.json", payload)
    return payload

