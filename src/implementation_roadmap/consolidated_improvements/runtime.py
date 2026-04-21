"""Deterministic consolidated improvements derivation."""

from __future__ import annotations

from typing import Any

from .contracts import CONSOLIDATED_IMPROVEMENTS_CONTRACT, CONSOLIDATED_IMPROVEMENTS_SCHEMA_VERSION


def _clamp01(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return round(value, 4)


def _is_true(value: Any) -> bool:
    return value is True


def _learning_metric_ready(metric: Any) -> bool:
    return isinstance(metric, dict) and _is_true(metric.get("ok"))


def _required_artifacts_present(review: dict[str, Any]) -> bool:
    manifest = review.get("artifact_manifest")
    if not isinstance(manifest, list):
        return False
    manifest_rows = [row for row in manifest if isinstance(row, dict)]
    if not manifest_rows:
        return False
    return all(_is_true(row.get("present")) for row in manifest_rows)


def build_consolidated_improvements(
    *,
    run_id: str,
    mode: str,
    summary: dict[str, Any],
    review: dict[str, Any],
    readiness: dict[str, Any],
    scalability: dict[str, Any],
    boundaries: dict[str, Any],
    storage: dict[str, Any],
    learning_metrics: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    review_passed = str(review.get("status", "")) == "completed_review_pass"
    validation_ready = _is_true(summary.get("quality", {}).get("validation_ready"))
    required_artifacts_present = _required_artifacts_present(review)
    checks = {
        "production_readiness_program": str(readiness.get("status", "")) == "ready",
        "scalability_strategy": str(scalability.get("status", "")) == "scalable",
        "service_boundaries": str(boundaries.get("status", "")) == "bounded",
        "storage_architecture": str(storage.get("status", "")) == "consistent",
        "capability_growth_metrics": _learning_metric_ready(learning_metrics.get("capability_growth_metrics")),
        "error_reduction_metrics": _learning_metric_ready(learning_metrics.get("error_reduction_metrics")),
        "extended_binary_gates": _learning_metric_ready(learning_metrics.get("extended_binary_gates")),
        "transfer_learning_metrics": _learning_metric_ready(learning_metrics.get("transfer_learning_metrics")),
    }
    total = len(checks)
    passed = sum(1 for ok in checks.values() if ok)
    consolidation_score = _clamp01(passed / total if total else 0.0)
    status = "ready" if (review_passed and validation_ready and required_artifacts_present and passed == total) else "not_ready"
    improvements = {key: {"ok": ok, "score": 1.0 if ok else 0.0} for key, ok in checks.items()}
    return {
        "schema": CONSOLIDATED_IMPROVEMENTS_CONTRACT,
        "schema_version": CONSOLIDATED_IMPROVEMENTS_SCHEMA_VERSION,
        "run_id": run_id,
        "mode": mode,
        "status": status,
        "summary": {
            "validation_ready": validation_ready,
            "review_passed": review_passed,
            "required_artifacts_present": required_artifacts_present,
            "improvements_passed": passed,
            "improvements_total": total,
            "consolidation_score": consolidation_score,
        },
        "improvements": improvements,
        "evidence": {
            "summary_ref": "summary.json",
            "review_ref": "review.json",
            "consolidated_ref": "program/consolidated_improvements.json",
        },
    }

