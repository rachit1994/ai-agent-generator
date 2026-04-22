"""Write deterministic objective policy engine artifact."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core_components.objective_policy_engine import (
    build_objective_policy_engine,
    validate_objective_policy_engine_dict,
)
from guardrails_and_safety.rollback_rules_policy_bundle.policy_bundle_rollback import (
    validate_policy_bundle_rollback,
)
from production_architecture.storage.storage.storage import ensure_dir, write_json


def _read_json_or_empty(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return body if isinstance(body, dict) else {}


def write_objective_policy_engine_artifact(
    *,
    output_dir: Path,
    run_id: str,
    mode: str,
    cto: dict[str, Any],
) -> dict[str, Any]:
    payload = build_objective_policy_engine(
        run_id=run_id,
        mode=mode,
        summary=_read_json_or_empty(output_dir / "summary.json"),
        review=_read_json_or_empty(output_dir / "review.json"),
        cto=cto if isinstance(cto, dict) else {},
        policy_bundle_rollback_errors=validate_policy_bundle_rollback(output_dir),
    )
    errs = validate_objective_policy_engine_dict(payload)
    if errs:
        raise ValueError(f"objective_policy_engine_contract:{','.join(errs)}")
    ensure_dir(output_dir / "strategy")
    write_json(output_dir / "strategy" / "objective_policy_engine.json", payload)
    return payload
