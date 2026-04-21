from __future__ import annotations

from pathlib import Path

from guardrails_and_safety.risk_budgets_permission_matrix import validate_risk_budgets_permission_matrix_path
from production_architecture.storage.storage.storage import ensure_dir
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.risk_budgets_permission_matrix_layer import (
    write_risk_budgets_permission_matrix_artifact,
)


def test_risk_budgets_permission_matrix_written_and_valid(tmp_path: Path) -> None:
    run_id = "risk-budgets-runtime"
    run_dir = tmp_path / "runs" / run_id
    ensure_dir(run_dir)
    payload = write_risk_budgets_permission_matrix_artifact(
        output_dir=run_dir,
        run_id=run_id,
        cto={
            "validation_ready": True,
            "balanced_gates": {"all_ok": True},
            "hard_stops": [{"id": "HS-01", "passed": True}],
        },
    )
    assert payload["run_id"] == run_id
    assert payload["status"] == "ready"
    assert validate_risk_budgets_permission_matrix_path(
        run_dir / "safety" / "risk_budgets_permission_matrix_runtime.json"
    ) == []
