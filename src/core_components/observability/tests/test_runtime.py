from __future__ import annotations

from core_components.observability import (
    build_observability_component,
    execute_observability_runtime,
    validate_observability_component_dict,
)


def test_build_observability_component_is_deterministic() -> None:
    production_observability = {"status": "healthy"}
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
    assert one["execution"]["signals_processed"] == 4


def test_validate_observability_component_fail_closed() -> None:
    errs = validate_observability_component_dict({"schema": "bad"})
    assert "observability_component_schema" in errs
    assert "observability_component_schema_version" in errs


def test_validate_observability_component_rejects_inconsistent_status_and_metrics() -> None:
    payload = build_observability_component(
        run_id="rid-observability",
        production_observability={"status": "healthy"},
        has_run_log=True,
        has_traces=True,
        has_orchestration_log=True,
    )
    payload["status"] = "ready"
    payload["metrics"]["all_checks_passed"] = False
    errs = validate_observability_component_dict(payload)
    assert "observability_component_status_consistency" in errs
    assert "observability_component_metric_consistency:all_checks_passed" in errs


def test_build_observability_component_requires_healthy_production_observability() -> None:
    payload = build_observability_component(
        run_id="rid-observability",
        production_observability={"status": "degraded"},
        has_run_log=True,
        has_traces=True,
        has_orchestration_log=True,
    )
    assert payload["metrics"]["has_production_observability"] is False
    assert payload["status"] == "degraded"


def test_validate_observability_component_rejects_non_canonical_evidence_ref() -> None:
    payload = build_observability_component(
        run_id="rid-observability",
        production_observability={"status": "healthy"},
        has_run_log=True,
        has_traces=True,
        has_orchestration_log=True,
    )
    payload["evidence"]["traces_ref"] = "trace.jsonl"
    errs = validate_observability_component_dict(payload)
    assert "observability_component_evidence_ref_mismatch:traces_ref" in errs


def test_execute_observability_runtime_detects_missing_sources() -> None:
    execution = execute_observability_runtime(
        production_observability={"status": "degraded"},
        has_run_log=False,
        has_traces=True,
        has_orchestration_log=False,
    )
    assert execution["signals_processed"] == 4
    assert execution["missing_signal_sources"] == [
        "production_observability",
        "run_log",
        "orchestration_log",
    ]
