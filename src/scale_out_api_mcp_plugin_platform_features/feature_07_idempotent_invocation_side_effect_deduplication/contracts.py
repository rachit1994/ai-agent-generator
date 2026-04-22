from __future__ import annotations

from typing import Any

IDEMPOTENCY_SCHEMA = "sde.scale.feature_07.idempotency.v1"
IDEMPOTENCY_SCHEMA_VERSION = "1.0"
_MODES = {"ci", "preflight"}
_STATUSES = {"pass", "fail"}
_CANONICAL_REFS = {
    "api_ref": "data/idempotency/api_state.json",
    "ledger_ref": "data/idempotency/ledger_state.json",
    "effects_ref": "data/idempotency/side_effects_state.json",
    "history_ref": "data/idempotency/trend_history.jsonl",
}


def validate_idempotency_report_dict(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["idempotency_not_object"]
    errors: list[str] = []
    if body.get("schema") != IDEMPOTENCY_SCHEMA:
        errors.append("idempotency_schema")
    if body.get("schema_version") != IDEMPOTENCY_SCHEMA_VERSION:
        errors.append("idempotency_schema_version")
    if body.get("mode") not in _MODES:
        errors.append("idempotency_mode")
    if body.get("status") not in _STATUSES:
        errors.append("idempotency_status")
    run_id = body.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errors.append("idempotency_run_id")
    if not isinstance(body.get("failed_gates"), list):
        errors.append("idempotency_failed_gates")
    evidence = body.get("evidence")
    if not isinstance(evidence, dict):
        return [*errors, "idempotency_evidence"]
    for key, expected in _CANONICAL_REFS.items():
        if evidence.get(key) != expected:
            errors.append(f"idempotency_evidence_ref:{key}")
    return errors
