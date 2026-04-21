"""Contracts for online evaluation shadow/canary artifacts."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

from .policy_defaults import MANDATORY_GATE_IDS

ONLINE_EVALUATION_SHADOW_CANARY_CONTRACT = "sde.online_evaluation_shadow_canary.v1"
ONLINE_EVALUATION_SHADOW_CANARY_SCHEMA_VERSION = "1.0"
ONLINE_EVALUATION_SHADOW_CANARY_BOUNDARY_ID = "online_evaluation_shadow_canary"
ONLINE_EVALUATION_SHADOW_CANARY_ERROR_PREFIX = "online_evaluation_shadow_canary_contract:"
_CANONICAL_GATE_REASONS = {
    "gate_min_sample": "gate_min_sample_unmet",
    "gate_error_rate_delta": "gate_error_rate_delta_exceeded",
    "gate_latency_p95_delta_ms": "gate_latency_p95_delta_exceeded",
    "gate_quality_delta": "gate_quality_delta_below_threshold",
}
_FLOAT_ZERO_TOLERANCE = 1e-9


def _validate_decision_block(decision: Any) -> tuple[list[str], dict[str, Any]]:
    if not isinstance(decision, dict):
        return (["online_evaluation_shadow_canary_decision"], {})
    errs: list[str] = []
    decision_value = decision.get("decision")
    if decision_value not in ("promote", "hold"):
        errs.append("online_evaluation_shadow_canary_decision_value")
    failed_gates = decision.get("failed_gates")
    if not isinstance(failed_gates, list) or any(not isinstance(row, str) for row in failed_gates):
        errs.append("online_evaluation_shadow_canary_failed_gates")
        failed_gates = []
    elif any(row not in MANDATORY_GATE_IDS for row in failed_gates):
        errs.append("online_evaluation_shadow_canary_unknown_gate_id")
    decision_reasons = decision.get("decision_reasons")
    if not isinstance(decision_reasons, list) or any(not isinstance(row, str) or not row for row in decision_reasons):
        errs.append("online_evaluation_shadow_canary_decision_reasons")
    min_sample_met = decision.get("min_sample_met")
    if not isinstance(min_sample_met, bool):
        errs.append("online_evaluation_shadow_canary_min_sample_met")
    return (
        errs,
        {
            "decision_value": decision_value,
            "failed_gates": failed_gates,
            "decision_reasons": decision_reasons,
            "min_sample_met": min_sample_met,
        },
    )


def _validate_metrics_block(metrics: Any) -> list[str]:
    if not isinstance(metrics, dict):
        return ["online_evaluation_shadow_canary_metrics"]
    errs: list[str] = []
    required_keys = (
        "sample_size",
        "coverage",
        "baseline_latency_p50_ms",
        "baseline_latency_p95_ms",
        "candidate_latency_p50_ms",
        "candidate_latency_p95_ms",
        "baseline_error_rate",
        "candidate_error_rate",
        "error_rate_delta",
        "latency_p95_delta_ms",
        "quality_delta",
    )
    for key in required_keys:
        value = metrics.get(key)
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(float(value)):
            errs.append(f"online_evaluation_shadow_canary_metrics_{key}")
    sample_size = metrics.get("sample_size")
    if isinstance(sample_size, (int, float)) and not isinstance(sample_size, bool) and float(sample_size) < 0.0:
        errs.append("online_evaluation_shadow_canary_metrics_sample_size_range")
    for rate_key in ("coverage", "baseline_error_rate", "candidate_error_rate"):
        rate = metrics.get(rate_key)
        if isinstance(rate, (int, float)) and not isinstance(rate, bool) and (float(rate) < 0.0 or float(rate) > 1.0):
            errs.append(f"online_evaluation_shadow_canary_metrics_{rate_key}_range")
    if not errs:
        errs.extend(
            _validate_coverage_sample_semantics(
                sample_size=float(sample_size),
                coverage=float(metrics["coverage"]),
            )
        )
    return errs


def _validate_coverage_sample_semantics(*, sample_size: float, coverage: float) -> list[str]:
    expected_coverage = 0.0 if abs(sample_size) <= _FLOAT_ZERO_TOLERANCE else 1.0
    if abs(coverage - expected_coverage) > _FLOAT_ZERO_TOLERANCE:
        return ["online_evaluation_shadow_canary_metrics_coverage_mismatch"]
    return []


def _validate_evidence_block(evidence: Any) -> tuple[list[str], str | None]:
    if not isinstance(evidence, dict):
        return (["online_evaluation_shadow_canary_evidence"], None)
    errs: list[str] = []
    canonical_ref = evidence.get("online_eval_records_ref")
    if canonical_ref != "learning/online_eval_records.jsonl":
        errs.append("online_evaluation_shadow_canary_evidence_online_eval_records_ref")
    return (errs, canonical_ref)


def _validate_decision_semantics(
    *,
    decision_value: Any,
    failed_gates: Any,
    decision_reasons: Any,
    min_sample_met: Any,
) -> list[str]:
    errs: list[str] = []
    if decision_value == "promote" and failed_gates:
        errs.append("online_evaluation_shadow_canary_promote_failed_gates")
    if decision_value == "promote" and min_sample_met is not True:
        errs.append("online_evaluation_shadow_canary_promote_min_sample")
    if decision_value == "promote" and isinstance(decision_reasons, list) and decision_reasons:
        errs.append("online_evaluation_shadow_canary_promote_unexpected_decision_reasons")
    if decision_value == "hold" and not failed_gates:
        errs.append("online_evaluation_shadow_canary_hold_missing_failed_gates")
    if decision_value == "hold" and isinstance(decision_reasons, list) and not decision_reasons:
        errs.append("online_evaluation_shadow_canary_hold_missing_decision_reasons")
    if (
        decision_value == "hold"
        and isinstance(failed_gates, list)
        and isinstance(decision_reasons, list)
        and all(isinstance(row, str) for row in failed_gates)
        and all(isinstance(row, str) for row in decision_reasons)
    ):
        expected_reasons = [_CANONICAL_GATE_REASONS.get(gate_id, "") for gate_id in failed_gates]
        if "" in expected_reasons or decision_reasons != expected_reasons:
            errs.append("online_evaluation_shadow_canary_hold_reasons_mismatch")
    return errs


def validate_online_evaluation_shadow_canary_dict(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["online_evaluation_shadow_canary_not_object"]
    errs: list[str] = []
    if body.get("schema") != ONLINE_EVALUATION_SHADOW_CANARY_CONTRACT:
        errs.append("online_evaluation_shadow_canary_schema")
    if body.get("schema_version") != ONLINE_EVALUATION_SHADOW_CANARY_SCHEMA_VERSION:
        errs.append("online_evaluation_shadow_canary_schema_version")
    run_id = body.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errs.append("online_evaluation_shadow_canary_run_id")
    decision_errs, decision_values = _validate_decision_block(body.get("decision"))
    errs.extend(decision_errs)
    errs.extend(_validate_metrics_block(body.get("metrics")))
    evidence_errs, _canonical_ref = _validate_evidence_block(body.get("evidence"))
    errs.extend(evidence_errs)
    errs.extend(
        _validate_decision_semantics(
            decision_value=decision_values.get("decision_value"),
            failed_gates=decision_values.get("failed_gates"),
            decision_reasons=decision_values.get("decision_reasons"),
            min_sample_met=decision_values.get("min_sample_met"),
        )
    )
    return errs


def validate_online_evaluation_shadow_canary_path(path: Path) -> list[str]:
    if not path.is_file():
        return ["online_evaluation_shadow_canary_file_missing"]
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ["online_evaluation_shadow_canary_json"]
    return validate_online_evaluation_shadow_canary_dict(body)
