from __future__ import annotations

import json
from pathlib import Path

from evaluation_framework.online_evaluation_shadow_canary_artifact import (
    GATE_ID_ERROR_RATE_DELTA,
    GATE_ID_LATENCY_P95_DELTA_MS,
    GATE_ID_MIN_SAMPLE,
    GATE_ID_QUALITY_DELTA,
    MANDATORY_GATE_IDS,
    MIN_SAMPLE_SIZE,
    OnlineEvalRecord,
    TrafficSplitConfig,
    build_online_evaluation_shadow_canary,
    parse_online_eval_records_jsonl,
    validate_online_evaluation_shadow_canary_dict,
    validate_traffic_split_config,
)


def test_build_online_evaluation_shadow_canary_is_deterministic() -> None:
    records = [
        OnlineEvalRecord(
            request_id=f"r-{idx}",
            cohort="shadow" if idx % 2 else "canary",
            baseline_latency_ms=100.0,
            candidate_latency_ms=102.0,
            baseline_outcome=True,
            candidate_outcome=True,
            baseline_quality=0.8,
            candidate_quality=0.82,
        )
        for idx in range(MIN_SAMPLE_SIZE)
    ]
    one = build_online_evaluation_shadow_canary(
        run_id="rid-online-shadow",
        online_eval_records=records,
    )
    two = build_online_evaluation_shadow_canary(
        run_id="rid-online-shadow",
        online_eval_records=records,
    )
    assert one == two
    assert validate_online_evaluation_shadow_canary_dict(one) == []
    assert one["decision"]["decision"] == "promote"


def test_build_online_evaluation_shadow_canary_enforces_min_sample_hold() -> None:
    payload = build_online_evaluation_shadow_canary(
        run_id="rid-online-shadow",
        online_eval_records=[],
    )
    assert payload["decision"]["decision"] == "hold"
    assert payload["decision"]["failed_gates"] == [GATE_ID_MIN_SAMPLE]


def test_validate_online_evaluation_shadow_canary_fail_closed() -> None:
    errs = validate_online_evaluation_shadow_canary_dict({"schema": "bad"})
    assert "online_evaluation_shadow_canary_schema" in errs
    assert "online_evaluation_shadow_canary_schema_version" in errs


def test_validate_unknown_gate_is_rejected() -> None:
    payload = {
        "schema": "sde.online_evaluation_shadow_canary.v1",
        "schema_version": "1.0",
        "run_id": "rid",
        "decision": {
            "decision": "hold",
            "failed_gates": ["not_a_real_gate"],
            "decision_reasons": ["gate_unknown"],
            "min_sample_met": False,
        },
        "metrics": {
            "sample_size": 1,
            "coverage": 1.0,
            "baseline_latency_p50_ms": 1.0,
            "baseline_latency_p95_ms": 1.0,
            "candidate_latency_p50_ms": 1.0,
            "candidate_latency_p95_ms": 1.0,
            "baseline_error_rate": 0.0,
            "candidate_error_rate": 0.0,
            "error_rate_delta": 0.0,
            "latency_p95_delta_ms": 0.0,
            "quality_delta": 0.0,
        },
        "evidence": {"online_eval_records_ref": "learning/online_eval_records.jsonl"},
    }
    errs = validate_online_evaluation_shadow_canary_dict(payload)
    assert "online_evaluation_shadow_canary_unknown_gate_id" in errs
    assert set(MANDATORY_GATE_IDS)


def test_validate_online_eval_rejects_hold_without_decision_reasons() -> None:
    payload = {
        "schema": "sde.online_evaluation_shadow_canary.v1",
        "schema_version": "1.0",
        "run_id": "rid",
        "decision": {
            "decision": "hold",
            "failed_gates": [GATE_ID_MIN_SAMPLE],
            "decision_reasons": [],
            "min_sample_met": False,
        },
        "metrics": {
            "sample_size": 0,
            "coverage": 0.0,
            "baseline_latency_p50_ms": 0.0,
            "baseline_latency_p95_ms": 0.0,
            "candidate_latency_p50_ms": 0.0,
            "candidate_latency_p95_ms": 0.0,
            "baseline_error_rate": 0.0,
            "candidate_error_rate": 0.0,
            "error_rate_delta": 0.0,
            "latency_p95_delta_ms": 0.0,
            "quality_delta": 0.0,
        },
        "evidence": {"online_eval_records_ref": "learning/online_eval_records.jsonl"},
    }
    errs = validate_online_evaluation_shadow_canary_dict(payload)
    assert "online_evaluation_shadow_canary_hold_missing_decision_reasons" in errs


def test_validate_online_eval_rejects_hold_with_reason_gate_mismatch() -> None:
    payload = {
        "schema": "sde.online_evaluation_shadow_canary.v1",
        "schema_version": "1.0",
        "run_id": "rid",
        "decision": {
            "decision": "hold",
            "failed_gates": [GATE_ID_MIN_SAMPLE, GATE_ID_QUALITY_DELTA],
            "decision_reasons": ["gate_quality_delta_below_threshold", "gate_min_sample_unmet"],
            "min_sample_met": False,
        },
        "metrics": {
            "sample_size": 0,
            "coverage": 0.0,
            "baseline_latency_p50_ms": 0.0,
            "baseline_latency_p95_ms": 0.0,
            "candidate_latency_p50_ms": 0.0,
            "candidate_latency_p95_ms": 0.0,
            "baseline_error_rate": 0.0,
            "candidate_error_rate": 0.0,
            "error_rate_delta": 0.0,
            "latency_p95_delta_ms": 0.0,
            "quality_delta": -0.1,
        },
        "evidence": {"online_eval_records_ref": "learning/online_eval_records.jsonl"},
    }
    errs = validate_online_evaluation_shadow_canary_dict(payload)
    assert "online_evaluation_shadow_canary_hold_reasons_mismatch" in errs


def test_validate_online_eval_rejects_promote_with_decision_reasons() -> None:
    payload = {
        "schema": "sde.online_evaluation_shadow_canary.v1",
        "schema_version": "1.0",
        "run_id": "rid",
        "decision": {
            "decision": "promote",
            "failed_gates": [],
            "decision_reasons": ["unexpected_reason"],
            "min_sample_met": True,
        },
        "metrics": {
            "sample_size": 5,
            "coverage": 1.0,
            "baseline_latency_p50_ms": 10.0,
            "baseline_latency_p95_ms": 12.0,
            "candidate_latency_p50_ms": 10.5,
            "candidate_latency_p95_ms": 12.5,
            "baseline_error_rate": 0.0,
            "candidate_error_rate": 0.0,
            "error_rate_delta": 0.0,
            "latency_p95_delta_ms": 0.5,
            "quality_delta": 0.01,
        },
        "evidence": {"online_eval_records_ref": "learning/online_eval_records.jsonl"},
    }
    errs = validate_online_evaluation_shadow_canary_dict(payload)
    assert "online_evaluation_shadow_canary_promote_unexpected_decision_reasons" in errs


def test_validate_online_eval_rejects_coverage_sample_mismatch() -> None:
    payload = {
        "schema": "sde.online_evaluation_shadow_canary.v1",
        "schema_version": "1.0",
        "run_id": "rid",
        "decision": {
            "decision": "hold",
            "failed_gates": [GATE_ID_MIN_SAMPLE],
            "decision_reasons": ["gate_min_sample_unmet"],
            "min_sample_met": False,
        },
        "metrics": {
            "sample_size": 0,
            "coverage": 1.0,
            "baseline_latency_p50_ms": 0.0,
            "baseline_latency_p95_ms": 0.0,
            "candidate_latency_p50_ms": 0.0,
            "candidate_latency_p95_ms": 0.0,
            "baseline_error_rate": 0.0,
            "candidate_error_rate": 0.0,
            "error_rate_delta": 0.0,
            "latency_p95_delta_ms": 0.0,
            "quality_delta": 0.0,
        },
        "evidence": {"online_eval_records_ref": "learning/online_eval_records.jsonl"},
    }
    errs = validate_online_evaluation_shadow_canary_dict(payload)
    assert "online_evaluation_shadow_canary_metrics_coverage_mismatch" in errs


def test_parse_online_eval_records_rejects_duplicate_request_id(tmp_path: Path) -> None:
    path = tmp_path / "records.jsonl"
    row = {
        "request_id": "req-1",
        "cohort": "shadow",
        "baseline_latency_ms": 10.0,
        "candidate_latency_ms": 11.0,
        "baseline_outcome": True,
        "candidate_outcome": True,
        "baseline_quality": 0.6,
        "candidate_quality": 0.7,
    }
    path.write_text("\n".join((json.dumps(row), json.dumps(row))), encoding="utf-8")
    try:
        parse_online_eval_records_jsonl(path)
    except ValueError as exc:
        assert str(exc).startswith("online_eval_records_duplicate_request_id:")
    else:
        raise AssertionError("expected duplicate request_id failure")


def test_parse_online_eval_records_rejects_malformed_jsonl(tmp_path: Path) -> None:
    path = tmp_path / "records.jsonl"
    path.write_text("{bad json", encoding="utf-8")
    try:
        parse_online_eval_records_jsonl(path)
    except ValueError as exc:
        assert str(exc) == "online_eval_records_jsonl:1"
    else:
        raise AssertionError("expected malformed jsonl failure")


def test_parse_online_eval_records_rejects_nan_numeric(tmp_path: Path) -> None:
    path = tmp_path / "records.jsonl"
    path.write_text(
        json.dumps(
            {
                "request_id": "req-nan",
                "cohort": "canary",
                "baseline_latency_ms": 10.0,
                "candidate_latency_ms": float("nan"),
                "baseline_outcome": True,
                "candidate_outcome": True,
                "baseline_quality": 0.6,
                "candidate_quality": 0.7,
            }
        ),
        encoding="utf-8",
    )
    try:
        parse_online_eval_records_jsonl(path)
    except ValueError as exc:
        assert str(exc) == "online_eval_records_numeric:candidate_latency_ms:1"
    else:
        raise AssertionError("expected NaN rejection")


def test_policy_gate_ids_are_stable_and_exact() -> None:
    assert MANDATORY_GATE_IDS == (
        GATE_ID_MIN_SAMPLE,
        GATE_ID_ERROR_RATE_DELTA,
        GATE_ID_LATENCY_P95_DELTA_MS,
        GATE_ID_QUALITY_DELTA,
    )


def test_traffic_split_config_rejects_invalid_sum() -> None:
    try:
        validate_traffic_split_config(TrafficSplitConfig(shadow_ratio=0.6, canary_ratio=0.6))
    except ValueError as exc:
        assert str(exc) == "online_eval_traffic_split_ratio_sum"
    else:
        raise AssertionError("expected invalid traffic split sum failure")
