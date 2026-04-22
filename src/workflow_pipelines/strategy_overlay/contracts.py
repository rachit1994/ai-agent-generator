"""Contracts for strategy overlay artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

STRATEGY_OVERLAY_RUNTIME_CONTRACT = "sde.strategy_overlay_runtime.v1"
STRATEGY_OVERLAY_RUNTIME_SCHEMA_VERSION = "1.0"
_ALLOWED_MODES = {"baseline", "guarded_pipeline", "phased_pipeline"}
_ALLOWED_STRATEGIES = {"stabilize", "accelerate", "hold"}
_CANONICAL_EVIDENCE_REFS = {
    "proposal_ref": "strategy/proposal.json",
    "overlay_ref": "strategy/overlay.json",
    "traces_ref": "traces.jsonl",
}


def validate_strategy_overlay_runtime_dict(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["strategy_overlay_runtime_not_object"]
    errs: list[str] = []
    if body.get("schema") != STRATEGY_OVERLAY_RUNTIME_CONTRACT:
        errs.append("strategy_overlay_runtime_schema")
    if body.get("schema_version") != STRATEGY_OVERLAY_RUNTIME_SCHEMA_VERSION:
        errs.append("strategy_overlay_runtime_schema_version")
    run_id = body.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errs.append("strategy_overlay_runtime_run_id")
    mode = body.get("mode")
    if mode not in _ALLOWED_MODES:
        errs.append("strategy_overlay_runtime_mode")
    strategy_name = body.get("strategy_name")
    if strategy_name not in _ALLOWED_STRATEGIES:
        errs.append("strategy_overlay_runtime_strategy_name")
    confidence = body.get("confidence")
    if isinstance(confidence, bool) or not isinstance(confidence, (int, float)):
        errs.append("strategy_overlay_runtime_confidence_type")
    elif float(confidence) < 0.0 or float(confidence) > 1.0:
        errs.append("strategy_overlay_runtime_confidence_range")
    gates = body.get("gates")
    if not isinstance(gates, dict):
        errs.append("strategy_overlay_runtime_gates")
    else:
        for key in ("promotion_required", "autonomy_applied", "finalize_passed"):
            if not isinstance(gates.get(key), bool):
                errs.append(f"strategy_overlay_runtime_gate_type:{key}")
    evidence = body.get("evidence")
    if not isinstance(evidence, dict):
        errs.append("strategy_overlay_runtime_evidence")
    else:
        for key, expected in _CANONICAL_EVIDENCE_REFS.items():
            value = evidence.get(key)
            if not isinstance(value, str) or not value.strip():
                errs.append(f"strategy_overlay_runtime_evidence_ref:{key}")
                continue
            normalized = value.strip()
            if normalized.startswith("/") or ".." in normalized.split("/") or normalized != expected:
                errs.append(f"strategy_overlay_runtime_evidence_ref:{key}")
    return errs


def validate_strategy_overlay_runtime_path(path: Path) -> list[str]:
    if not path.is_file():
        return ["strategy_overlay_runtime_file_missing"]
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ["strategy_overlay_runtime_json"]
    return validate_strategy_overlay_runtime_dict(body)
