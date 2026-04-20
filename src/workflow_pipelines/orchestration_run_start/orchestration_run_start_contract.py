"""Contract for the first-line ``run_start`` object in ``orchestration.jsonl``."""

from __future__ import annotations

from typing import Any, Final

ORCHESTRATION_RUN_START_CONTRACT: Final = "sde.orchestration_run_start.v1"

_ALLOWED_MODES: Final = frozenset({"baseline", "guarded_pipeline", "phased_pipeline"})
_ALLOWED_KEYS: Final = frozenset({"run_id", "type", "mode", "provider", "model"})


def _errs_run_id(body: dict[str, Any]) -> list[str]:
    rid = body.get("run_id")
    if not isinstance(rid, str) or not rid.strip():
        return ["orchestration_run_start_run_id"]
    return []


def _errs_type(body: dict[str, Any]) -> list[str]:
    if body.get("type") != "run_start":
        return ["orchestration_run_start_type"]
    return []


def _errs_mode(body: dict[str, Any]) -> list[str]:
    mode = body.get("mode")
    if mode not in _ALLOWED_MODES:
        return ["orchestration_run_start_mode"]
    return []


def _errs_provider_model(body: dict[str, Any]) -> list[str]:
    errs: list[str] = []
    prov = body.get("provider")
    if not isinstance(prov, str) or not prov.strip():
        errs.append("orchestration_run_start_provider")
    model = body.get("model")
    if not isinstance(model, str) or not model.strip():
        errs.append("orchestration_run_start_model")
    return errs


def validate_orchestration_run_start_dict(body: Any) -> list[str]:
    """Return stable error tokens for ``append_orchestration_run_start`` payload shape."""
    if not isinstance(body, dict):
        return ["orchestration_run_start_not_object"]
    b = body
    errs: list[str] = []
    errs.extend(_errs_run_id(b))
    errs.extend(_errs_type(b))
    errs.extend(_errs_mode(b))
    errs.extend(_errs_provider_model(b))
    for key in b:
        if key not in _ALLOWED_KEYS:
            errs.append(f"orchestration_run_start_unknown_key:{key}")
    return errs
