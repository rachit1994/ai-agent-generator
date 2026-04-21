from __future__ import annotations

from core_components.observability import (
    build_observability_component,
    validate_observability_component_dict,
)


def test_build_observability_component_is_deterministic() -> None:
    production_observability = {"status": "ready"}
    one = build_observability_component(
        run_id="rid-observability",
        production_observability=production_observability,
        has_run_log=True,
        has_traces=True,
        has_orchestration_log=True,
    )
    two = build_observability_component(
        run_id="rid-observability",
        production_observability=production_observability,
        has_run_log=True,
        has_traces=True,
        has_orchestration_log=True,
    )
    assert one == two
    assert one["status"] == "ready"
    assert validate_observability_component_dict(one) == []


def test_validate_observability_component_fail_closed() -> None:
    errs = validate_observability_component_dict({"schema": "bad"})
    assert "observability_component_schema" in errs
    assert "observability_component_schema_version" in errs
