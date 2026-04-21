from __future__ import annotations

from production_architecture.observability import (
    build_production_observability,
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


def test_validate_production_observability_fail_closed() -> None:
    errs = validate_production_observability_dict({"schema": "bad"})
    assert "production_observability_schema" in errs
    assert "production_observability_schema_version" in errs
