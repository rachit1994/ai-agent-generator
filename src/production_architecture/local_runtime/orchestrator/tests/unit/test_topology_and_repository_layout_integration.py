from __future__ import annotations

import json
from pathlib import Path

from implementation_roadmap.topology_and_repository_layout import (
    validate_topology_and_repository_layout_path,
)
from production_architecture.storage.storage.storage import ensure_dir, write_json
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.topology_and_repository_layout_layer import (
    write_topology_and_repository_layout_artifact,
)


def test_write_topology_and_repository_layout_artifact_and_validate(tmp_path: Path) -> None:
    run_id = "run-topology-layout"
    output_dir = tmp_path / "runs" / run_id
    ensure_dir(output_dir)
    write_json(
        output_dir / "review.json",
        {
            "status": "completed_review_pass",
            "artifact_manifest": [
                {"path": "program/production_readiness.json", "present": True},
                {"path": "program/consolidated_improvements.json", "present": True},
                {"path": "program/implementation_roadmap.json", "present": True},
                {"path": "strategy/scalability_strategy.json", "present": True},
                {"path": "strategy/service_boundaries.json", "present": True},
                {"path": "event_store/component_runtime.json", "present": True},
                {"path": "orchestrator/component_runtime.json", "present": True},
                {"path": "iam/identity_authz_plane.json", "present": True},
                {"path": "learning/learning_service.json", "present": True},
                {"path": "memory/memory_system.json", "present": True},
                {"path": "strategy/career_strategy_layer.json", "present": True},
                {"path": "strategy/objective_policy_engine.json", "present": True},
                {"path": "practice/practice_engine.json", "present": True},
                {"path": "learning/self_learning_loop.json", "present": True},
                {"path": "safety/controller_runtime.json", "present": True},
                {"path": "evaluation/service_runtime.json", "present": True},
                {"path": "observability/component_runtime.json", "present": True},
                {"path": "learning/transfer_learning_metrics.json", "present": True},
                {"path": "learning/error_reduction_metrics.json", "present": True},
                {"path": "traces.jsonl", "present": True},
                {"path": "traces/event_row_runtime.json", "present": True},
                {"path": "orchestration.jsonl", "present": True},
                {"path": "orchestration/run_start_runtime.json", "present": True},
                {"path": "orchestration/stage_event_runtime.json", "present": True},
                {"path": "orchestration/run_error_runtime.json", "present": True},
                {"path": "orchestration/run_end_runtime.json", "present": True},
                {"path": "run-manifest.json", "present": True},
                {"path": "program/run_manifest_runtime.json", "present": True},
                {"path": "program/retry_repeat_profile_runtime.json", "present": True},
            ],
        },
    )
    payload = write_topology_and_repository_layout_artifact(
        output_dir=output_dir, run_id=run_id, mode="guarded_pipeline"
    )
    assert payload["run_id"] == run_id
    assert (
        validate_topology_and_repository_layout_path(
            output_dir / "program" / "topology_and_repository_layout.json"
        )
        == []
    )
    body = json.loads(
        (output_dir / "program" / "topology_and_repository_layout.json").read_text(encoding="utf-8")
    )
    assert body["run_id"] == run_id

