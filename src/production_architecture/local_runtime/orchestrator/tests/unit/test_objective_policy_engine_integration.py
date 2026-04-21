from __future__ import annotations

import json
from pathlib import Path

from core_components.objective_policy_engine import validate_objective_policy_engine_path
from production_architecture.storage.storage.storage import ensure_dir, write_json
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.objective_policy_engine_layer import (
    write_objective_policy_engine_artifact,
)


def test_write_objective_policy_engine_artifact_and_validate(tmp_path: Path) -> None:
    run_id = "run-objective-policy"
    output_dir = tmp_path / "runs" / run_id
    ensure_dir(output_dir / "program")
    write_json(
        output_dir / "summary.json",
        {"balanced_gates": {"reliability": 95, "delivery": 94, "governance": 96, "composite": 95}},
    )
    write_json(output_dir / "review.json", {"status": "completed_review_pass"})
    cto = {"hard_stops": [{"id": "HS01", "passed": True}]}
    payload = write_objective_policy_engine_artifact(
        output_dir=output_dir, run_id=run_id, mode="guarded_pipeline", cto=cto
    )
    assert payload["run_id"] == run_id
    policy_path = output_dir / "strategy" / "objective_policy_engine.json"
    assert validate_objective_policy_engine_path(policy_path) == []
    body = json.loads(policy_path.read_text(encoding="utf-8"))
    assert body["policy"]["decision"] in {"allow", "defer", "deny"}
