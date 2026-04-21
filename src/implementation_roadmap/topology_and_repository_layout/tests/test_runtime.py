from __future__ import annotations

from implementation_roadmap.topology_and_repository_layout import (
    build_topology_and_repository_layout,
    validate_topology_and_repository_layout_dict,
)


def test_build_topology_and_repository_layout_is_deterministic() -> None:
    manifest = [
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
    ]
    one = build_topology_and_repository_layout(
        run_id="rid-topology", mode="guarded_pipeline", artifact_manifest=manifest
    )
    two = build_topology_and_repository_layout(
        run_id="rid-topology", mode="guarded_pipeline", artifact_manifest=manifest
    )
    assert one == two
    assert validate_topology_and_repository_layout_dict(one) == []


def test_validate_topology_and_repository_layout_fail_closed() -> None:
    errs = validate_topology_and_repository_layout_dict({"schema": "bad"})
    assert "topology_and_repository_layout_schema" in errs
    assert "topology_and_repository_layout_schema_version" in errs

