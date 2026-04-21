from __future__ import annotations

from core_components.orchestrator import (
    build_orchestrator_component,
    validate_orchestrator_component_dict,
)


def test_build_orchestrator_component_is_deterministic() -> None:
    one = build_orchestrator_component(
        run_id="rid-orch",
        run_manifest={"schema": "sde.run_manifest.v1"},
        run_manifest_runtime={"schema": "sde.run_manifest_runtime.v1"},
        has_traces=True,
        has_orchestration_log=True,
    )
    two = build_orchestrator_component(
        run_id="rid-orch",
        run_manifest={"schema": "sde.run_manifest.v1"},
        run_manifest_runtime={"schema": "sde.run_manifest_runtime.v1"},
        has_traces=True,
        has_orchestration_log=True,
    )
    assert one == two
    assert one["status"] == "ready"
    assert validate_orchestrator_component_dict(one) == []


def test_validate_orchestrator_component_fail_closed() -> None:
    errs = validate_orchestrator_component_dict({"schema": "bad"})
    assert "orchestrator_component_schema" in errs
    assert "orchestrator_component_schema_version" in errs
