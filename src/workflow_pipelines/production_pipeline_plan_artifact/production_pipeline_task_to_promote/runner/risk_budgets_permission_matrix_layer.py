"""Write deterministic risk-budgets permission-matrix runtime artifact."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from guardrails_and_safety.risk_budgets_permission_matrix import (
    build_risk_budgets_permission_matrix,
    validate_risk_budgets_permission_matrix_dict,
)
from production_architecture.storage.storage.storage import ensure_dir, write_json


def write_risk_budgets_permission_matrix_artifact(
    *,
    output_dir: Path,
    run_id: str,
    cto: dict[str, Any],
) -> dict[str, Any]:
    payload = build_risk_budgets_permission_matrix(run_id=run_id, cto=cto if isinstance(cto, dict) else {})
    errs = validate_risk_budgets_permission_matrix_dict(payload)
    if errs:
        raise ValueError(f"risk_budgets_permission_matrix_contract:{','.join(errs)}")
    ensure_dir(output_dir / "safety")
    write_json(output_dir / "safety" / "risk_budgets_permission_matrix_runtime.json", payload)
    return payload
