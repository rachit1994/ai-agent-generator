"""Write deterministic rollback-rules policy-bundle evidence artifact."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from guardrails_and_safety.rollback_rules_policy_bundle import (
    build_rollback_rules_policy_bundle,
    validate_rollback_rules_policy_bundle_dict,
)
from production_architecture.storage.storage.storage import ensure_dir, write_json


def _read_json_or_empty(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    body = json.loads(path.read_text(encoding="utf-8"))
    return body if isinstance(body, dict) else {}


def write_rollback_rules_policy_bundle_artifact(
    *,
    output_dir: Path,
    run_id: str,
) -> dict[str, Any]:
    payload = build_rollback_rules_policy_bundle(
        run_id=run_id,
        rollback_record=_read_json_or_empty(output_dir / "program" / "policy_bundle_rollback.json"),
    )
    errs = validate_rollback_rules_policy_bundle_dict(payload)
    if errs:
        raise ValueError(f"rollback_rules_policy_bundle_contract:{','.join(errs)}")
    ensure_dir(output_dir / "program")
    write_json(output_dir / "program" / "rollback_rules_policy_bundle.json", payload)
    return payload
