"""Contracts for feature 14 local vs production semantic parity gates."""

from __future__ import annotations

from typing import Any

LOCAL_PROD_PARITY_SCHEMA = "sde.scale.feature_14.local_prod_parity.v1"
LOCAL_PROD_PARITY_SCHEMA_VERSION = "1.0"
_MODES = {"ci", "preflight"}
_STATUSES = {"pass", "fail"}
_CANONICAL_REFS = {
    "local_ref": "data/local_prod_parity/local_results.json",
    "prod_ref": "data/local_prod_parity/prod_results.json",
    "diff_ref": "data/local_prod_parity/diff.json",
    "history_ref": "data/local_prod_parity/trend_history.jsonl",
}


def validate_local_prod_parity_report_dict(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["local_prod_parity_not_object"]
    errors: list[str] = []
    if body.get("schema") != LOCAL_PROD_PARITY_SCHEMA:
        errors.append("local_prod_parity_schema")
    if body.get("schema_version") != LOCAL_PROD_PARITY_SCHEMA_VERSION:
        errors.append("local_prod_parity_schema_version")
    if body.get("mode") not in _MODES:
        errors.append("local_prod_parity_mode")
    if body.get("status") not in _STATUSES:
        errors.append("local_prod_parity_status")
    run_id = body.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errors.append("local_prod_parity_run_id")
    if not isinstance(body.get("failed_gates"), list):
        errors.append("local_prod_parity_failed_gates")
    evidence = body.get("evidence")
    if not isinstance(evidence, dict):
        return [*errors, "local_prod_parity_evidence"]
    for key, expected in _CANONICAL_REFS.items():
        if evidence.get(key) != expected:
            errors.append(f"local_prod_parity_evidence_ref:{key}")
    return errors

