from __future__ import annotations

import json
import math

import pytest

from core_components.memory_system import (
    build_memory_system,
    execute_memory_system_runtime,
    validate_memory_system_dict,
)


def _healthy_payload() -> dict[str, object]:
    return build_memory_system(
        run_id="rid-memory-system",
        retrieval_bundle={"chunks": [{"text": "x"}]},
        quality_metrics={"contradiction_rate": 0.0, "staleness_p95_hours": 1.0},
        quarantine_rows=[],
    )


def test_build_memory_system_is_deterministic() -> None:
    one = _healthy_payload()
    two = build_memory_system(
        run_id="rid-memory-system",
        retrieval_bundle={"chunks": [{"text": "x"}]},
        quality_metrics={"contradiction_rate": 0.0, "staleness_p95_hours": 1.0},
        quarantine_rows=[],
    )
    assert one == two
    assert json.dumps(one, sort_keys=True) == json.dumps(two, sort_keys=True)
    assert validate_memory_system_dict(one) == []
    assert one["execution"]["chunks_processed"] == 1


def test_status_threshold_boundary_is_healthy_at_quality_point_eight() -> None:
    payload = build_memory_system(
        run_id="rid-threshold",
        retrieval_bundle={"chunks": [{"text": "x"}]},
        quality_metrics={"contradiction_rate": 0.2, "staleness_p95_hours": 24.0},
        quarantine_rows=[],
    )
    assert payload["status"] == "healthy"
    assert payload["metrics"]["quality_score"] == pytest.approx(0.8)
    assert validate_memory_system_dict(payload) == []


def test_staleness_above_boundary_degrades_quality_score() -> None:
    payload = build_memory_system(
        run_id="rid-stale",
        retrieval_bundle={"chunks": [{"text": "x"}]},
        quality_metrics={"contradiction_rate": 0.0, "staleness_p95_hours": 24.01},
        quarantine_rows=[],
    )
    assert payload["status"] == "degraded"
    assert payload["metrics"]["quality_score"] == pytest.approx(0.5)
    assert validate_memory_system_dict(payload) == []


def test_runtime_normalizes_non_finite_numbers_to_defaults() -> None:
    payload = build_memory_system(
        run_id="rid-non-finite",
        retrieval_bundle={"chunks": [{"text": "x"}]},
        quality_metrics={"contradiction_rate": math.nan, "staleness_p95_hours": math.inf},
        quarantine_rows=[],
    )
    assert payload["metrics"]["contradiction_rate"] == pytest.approx(1.0)
    assert payload["metrics"]["staleness_p95_hours"] == pytest.approx(999.0)
    assert payload["metrics"]["quality_score"] == pytest.approx(0.0)
    assert payload["status"] == "degraded"
    assert validate_memory_system_dict(payload) == []


def test_validate_memory_system_rejects_status_semantic_mismatch() -> None:
    payload = _healthy_payload()
    payload["status"] = "missing"
    errs = validate_memory_system_dict(payload)
    assert "memory_system_status_semantics:missing" in errs


def test_validate_memory_system_rejects_bool_for_numeric_fields() -> None:
    payload = _healthy_payload()
    metrics = payload["metrics"]
    assert isinstance(metrics, dict)
    metrics["retrieval_chunks"] = True
    metrics["quality_score"] = False
    metrics["contradiction_rate"] = True
    metrics["staleness_p95_hours"] = False
    errs = validate_memory_system_dict(payload)
    assert "memory_system_metric_type:retrieval_chunks" in errs
    assert "memory_system_quality_score_type" in errs
    assert "memory_system_contradiction_rate_type" in errs
    assert "memory_system_staleness_p95_hours_type" in errs


def test_validate_memory_system_rejects_blank_evidence_ref() -> None:
    payload = _healthy_payload()
    evidence = payload["evidence"]
    assert isinstance(evidence, dict)
    evidence["quality_metrics_ref"] = " "
    errs = validate_memory_system_dict(payload)
    assert "memory_system_evidence_missing:quality_metrics_ref" in errs


def test_build_memory_system_treats_non_string_quarantine_rows_as_present() -> None:
    payload = build_memory_system(
        run_id="rid-quarantine-shape",
        retrieval_bundle={"chunks": [{"text": "x"}]},
        quality_metrics={"contradiction_rate": 0.0, "staleness_p95_hours": 1.0},
        quarantine_rows=[{"unexpected": True}],  # type: ignore[list-item]
    )
    assert payload["metrics"]["quarantine_rows"] == 1
    assert payload["status"] == "degraded"


def test_build_memory_system_sets_zero_quality_when_no_retrieval_chunks() -> None:
    payload = build_memory_system(
        run_id="rid-no-retrieval",
        retrieval_bundle={"chunks": []},
        quality_metrics={"contradiction_rate": 0.0, "staleness_p95_hours": 1.0},
        quarantine_rows=[],
    )
    assert payload["status"] == "missing"
    assert payload["metrics"]["quality_score"] == pytest.approx(0.0)


def test_validate_memory_system_rejects_missing_status_with_nonzero_quality_score() -> None:
    payload = build_memory_system(
        run_id="rid-no-retrieval-contract",
        retrieval_bundle={"chunks": []},
        quality_metrics={"contradiction_rate": 0.0, "staleness_p95_hours": 1.0},
        quarantine_rows=[],
    )
    payload["metrics"]["quality_score"] = 0.5
    errs = validate_memory_system_dict(payload)
    assert "memory_system_status_semantics:missing_quality_score" in errs


def test_build_memory_system_fails_closed_for_out_of_range_quality_metrics() -> None:
    payload = build_memory_system(
        run_id="rid-bad-quality-metrics",
        retrieval_bundle={"chunks": [{"text": "x"}]},
        quality_metrics={"contradiction_rate": -0.1, "staleness_p95_hours": -2.0},
        quarantine_rows=[],
    )
    assert payload["status"] == "degraded"
    assert payload["metrics"]["quality_score"] == pytest.approx(0.0)
    assert payload["metrics"]["contradiction_rate"] == pytest.approx(1.0)
    assert payload["metrics"]["staleness_p95_hours"] == pytest.approx(999.0)
    assert validate_memory_system_dict(payload) == []


def test_execute_memory_system_runtime_detects_missing_quality_fields() -> None:
    execution = execute_memory_system_runtime(
        retrieval_bundle={"chunks": [{"text": "x"}]},
        quality_metrics={"contradiction_rate": 0.1},
        quarantine_rows=[{"bad": True}],  # type: ignore[list-item]
    )
    assert execution["chunks_processed"] == 1
    assert execution["quarantine_rows_processed"] == 1
    assert execution["malformed_quarantine_rows"] == 1
    assert execution["missing_quality_fields"] == ["staleness_p95_hours"]
