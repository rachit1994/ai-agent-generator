"""Write deterministic safety-controller runtime artifact."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from core_components.safety_controller import build_safety_controller, validate_safety_controller_dict
from production_architecture.storage.storage.storage import ensure_dir, write_json


def write_safety_controller_artifact(
    *,
    output_dir: Path,
    run_id: str,
    cto: dict[str, Any],
) -> dict[str, Any]:
    payload = build_safety_controller(run_id=run_id, cto=cto if isinstance(cto, dict) else {})
    errs = validate_safety_controller_dict(payload)
    if errs:
        raise ValueError(f"safety_controller_contract:{','.join(errs)}")
    ensure_dir(output_dir / "safety")
    write_json(output_dir / "safety" / "controller_runtime.json", payload)
    return payload
