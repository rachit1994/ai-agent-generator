"""Contracts for transfer learning metrics artifacts."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

TRANSFER_LEARNING_METRICS_CONTRACT = "sde.transfer_learning_metrics.v1"
TRANSFER_LEARNING_METRICS_SCHEMA_VERSION = "1.0"
_NET_TRANSFER_TOLERANCE = 1e-6


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _validate_metrics(metrics: Any) -> tuple[list[str], dict[str, float]]:
    if not isinstance(metrics, dict):
        return ["transfer_learning_metrics_metrics"], {}
    errs: list[str] = []
    required = (
        "transfer_gain_rate",
        "negative_transfer_rate",
        "retained_success_rate",
        "net_transfer_points",
        "transfer_efficiency_score",
    )
    numeric_values: dict[str, float] = {}
    for key in required:
        value = metrics.get(key)
        if not _is_number(value):
            errs.append(f"transfer_learning_metrics_metric_type:{key}")
            continue
        numeric = float(value)
        if not math.isfinite(numeric):
            errs.append(f"transfer_learning_metrics_metric_non_finite:{key}")
            continue
        numeric_values[key] = numeric
        if key.endswith("_rate") or key.endswith("_score"):
            if numeric < 0.0 or numeric > 1.0:
                errs.append(f"transfer_learning_metrics_metric_range:{key}")
    return errs, numeric_values


def _validate_net_transfer_coherence(numeric_values: dict[str, float], errs: list[str]) -> None:
    required_keys = {"transfer_gain_rate", "negative_transfer_rate", "net_transfer_points"}
    if not required_keys.issubset(numeric_values):
        return
    expected = round(
        (numeric_values["transfer_gain_rate"] - numeric_values["negative_transfer_rate"]) * 100.0,
        4,
    )
    if abs(numeric_values["net_transfer_points"] - expected) > _NET_TRANSFER_TOLERANCE:
        errs.append("transfer_learning_metrics_net_transfer_points_mismatch")


def _validate_transfer_efficiency_coherence(numeric_values: dict[str, float], errs: list[str]) -> None:
    required_keys = {
        "transfer_gain_rate",
        "negative_transfer_rate",
        "retained_success_rate",
        "transfer_efficiency_score",
    }
    if not required_keys.issubset(numeric_values):
        return
    expected = round(
        0.5 * numeric_values["transfer_gain_rate"]
        + 0.3 * numeric_values["retained_success_rate"]
        + 0.2 * (1.0 - numeric_values["negative_transfer_rate"]),
        4,
    )
    if abs(numeric_values["transfer_efficiency_score"] - expected) > _NET_TRANSFER_TOLERANCE:
        errs.append("transfer_learning_metrics_transfer_efficiency_score_mismatch")


def _validate_evidence(evidence: Any) -> list[str]:
    if not isinstance(evidence, dict):
        return ["transfer_learning_metrics_evidence"]
    errs: list[str] = []
    if evidence.get("traces_ref") != "traces.jsonl":
        errs.append("transfer_learning_metrics_evidence_traces_ref")
    if evidence.get("skill_nodes_ref") != "capability/skill_nodes.json":
        errs.append("transfer_learning_metrics_evidence_skill_nodes_ref")
    return errs


def validate_transfer_learning_metrics_dict(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["transfer_learning_metrics_not_object"]
    errs: list[str] = []
    if body.get("schema") != TRANSFER_LEARNING_METRICS_CONTRACT:
        errs.append("transfer_learning_metrics_schema")
    if body.get("schema_version") != TRANSFER_LEARNING_METRICS_SCHEMA_VERSION:
        errs.append("transfer_learning_metrics_schema_version")
    run_id = body.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errs.append("transfer_learning_metrics_run_id")
    metric_errs, numeric_values = _validate_metrics(body.get("metrics"))
    errs.extend(metric_errs)
    if numeric_values:
        _validate_net_transfer_coherence(numeric_values, errs)
        _validate_transfer_efficiency_coherence(numeric_values, errs)
    errs.extend(_validate_evidence(body.get("evidence")))
    return errs


def validate_transfer_learning_metrics_path(path: Path) -> list[str]:
    if not path.is_file():
        return ["transfer_learning_metrics_file_missing"]
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ["transfer_learning_metrics_json"]
    return validate_transfer_learning_metrics_dict(body)

