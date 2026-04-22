from __future__ import annotations

from production_architecture.observability import (
    build_production_observability,
    execute_production_observability_runtime,
    validate_production_observability_dict,
)


def test_build_production_observability_is_deterministic() -> None:
    one = build_production_observability(
        run_id="rid-observability",
        mode="guarded_pipeline",
        trace_rows=3,
        orchestration_rows=2,
        run_log_lines=5,
    )
    two = build_production_observability(
        run_id="rid-observability",
        mode="guarded_pipeline",
        trace_rows=3,
        orchestration_rows=2,
        run_log_lines=5,
    )
    assert one == two
    assert validate_production_observability_dict(one) == []
    assert one["execution"]["signals_processed"] == 3


def test_validate_production_observability_fail_closed() -> None:
    errs = validate_production_observability_dict({"schema": "bad"})
    assert "production_observability_schema" in errs
    assert "production_observability_schema_version" in errs


def test_validate_production_observability_rejects_status_metrics_mismatch() -> None:
    payload = build_production_observability(
        run_id="rid-observability",
        mode="guarded_pipeline",
        trace_rows=1,
        orchestration_rows=1,
        run_log_lines=1,
    )
    payload["status"] = "missing"
    errs = validate_production_observability_dict(payload)
    assert "production_observability_status_metrics_mismatch" in errs


def test_validate_production_observability_rejects_missing_evidence_ref() -> None:
    payload = build_production_observability(
        run_id="rid-observability",
        mode="guarded_pipeline",
        trace_rows=1,
        orchestration_rows=1,
        run_log_lines=1,
    )
    payload["evidence"]["run_log_ref"] = ""
    errs = validate_production_observability_dict(payload)
    assert "production_observability_evidence_ref:run_log_ref" in errs


def test_validate_production_observability_rejects_non_canonical_evidence_ref() -> None:
    payload = build_production_observability(
        run_id="rid-observability",
        mode="guarded_pipeline",
        trace_rows=1,
        orchestration_rows=1,
        run_log_lines=1,
    )
    payload["evidence"]["orchestration_ref"] = "orchestration-events.jsonl"
    errs = validate_production_observability_dict(payload)
    assert "production_observability_evidence_ref_mismatch:orchestration_ref" in errs


def test_execute_production_observability_runtime_detects_missing_sources() -> None:
    execution = execute_production_observability_runtime(
        trace_rows=0,
        orchestration_rows=2,
        run_log_lines=0,
    )
    assert execution["signals_processed"] == 3
    assert execution["trace_rows_observed"] == 0
    assert execution["orchestration_rows_observed"] == 2
    assert execution["run_log_lines_observed"] == 0
    assert execution["missing_signal_sources"] == ["traces", "run_log"]
