"""Contracts for feature 15 local/prod config overlay invariants."""

from __future__ import annotations

from typing import Any

CONFIG_OVERLAY_SCHEMA = "sde.scale.feature_15.config_overlay.v1"
CONFIG_OVERLAY_SCHEMA_VERSION = "1.0"
_MODES = {"ci", "preflight"}
_STATUSES = {"pass", "fail"}
_CANONICAL_REFS = {
    "base_ref": "data/config_overlay/base_config.json",
    "overlay_ref": "data/config_overlay/overlay_config.json",
    "resolved_ref": "data/config_overlay/resolved_config.json",
    "history_ref": "data/config_overlay/trend_history.jsonl",
}


def validate_config_overlay_report_dict(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["config_overlay_not_object"]
    errors: list[str] = []
    if body.get("schema") != CONFIG_OVERLAY_SCHEMA:
        errors.append("config_overlay_schema")
    if body.get("schema_version") != CONFIG_OVERLAY_SCHEMA_VERSION:
        errors.append("config_overlay_schema_version")
    if body.get("mode") not in _MODES:
        errors.append("config_overlay_mode")
    if body.get("status") not in _STATUSES:
        errors.append("config_overlay_status")
    run_id = body.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errors.append("config_overlay_run_id")
    if not isinstance(body.get("failed_gates"), list):
        errors.append("config_overlay_failed_gates")
    evidence = body.get("evidence")
    if not isinstance(evidence, dict):
        return [*errors, "config_overlay_evidence"]
    for key, expected in _CANONICAL_REFS.items():
        if evidence.get(key) != expected:
            errors.append(f"config_overlay_evidence_ref:{key}")
    return errors

