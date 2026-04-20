"""Contract for ``run_end`` lines appended to ``orchestration.jsonl`` on success."""

from __future__ import annotations

from typing import Any, Final

ORCHESTRATION_RUN_END_CONTRACT: Final = "sde.orchestration_run_end.v1"

_ALLOWED_KEYS: Final = frozenset({"run_id", "type", "artifacts", "output_refusal", "checks"})


def _errs_run_end_unknown_keys(body: dict[str, Any]) -> list[str]:
    errs: list[str] = []
    for key in body:
        if key not in _ALLOWED_KEYS:
            errs.append(f"orchestration_run_end_unknown_key:{key}")
    return errs


def _errs_run_end_run_id_type(body: dict[str, Any]) -> list[str]:
    rid = body.get("run_id")
    if not isinstance(rid, str) or not rid.strip():
        return ["orchestration_run_end_run_id"]
    if body.get("type") != "run_end":
        return ["orchestration_run_end_type"]
    return []


def _errs_run_end_artifacts(body: dict[str, Any]) -> list[str]:
    art = body.get("artifacts")
    if not isinstance(art, dict):
        return ["orchestration_run_end_artifacts"]
    errs: list[str] = []
    for k, v in art.items():
        if not isinstance(k, str) or not k.strip():
            errs.append("orchestration_run_end_artifacts_key")
            break
        if not isinstance(v, str) or not v.strip():
            errs.append("orchestration_run_end_artifacts_value")
            break
    return errs


def _errs_run_end_optional_refs(body: dict[str, Any]) -> list[str]:
    errs: list[str] = []
    ref = body.get("output_refusal")
    if ref is not None and not isinstance(ref, dict):
        errs.append("orchestration_run_end_output_refusal")
    ch = body.get("checks")
    if ch is not None and not isinstance(ch, list):
        errs.append("orchestration_run_end_checks")
    elif isinstance(ch, list):
        for idx, item in enumerate(ch):
            if not isinstance(item, dict):
                errs.append(f"orchestration_run_end_checks_item:{idx}")
                continue
            name = item.get("name")
            if not isinstance(name, str) or not name.strip():
                errs.append(f"orchestration_run_end_checks_name:{idx}")
            passed = item.get("passed")
            if not isinstance(passed, bool):
                errs.append(f"orchestration_run_end_checks_passed:{idx}")
    return errs


def validate_orchestration_run_end_dict(body: Any) -> list[str]:
    """Return stable error tokens for a ``run_end`` orchestration line."""
    if not isinstance(body, dict):
        return ["orchestration_run_end_not_object"]
    b = body
    errs: list[str] = []
    errs.extend(_errs_run_end_unknown_keys(b))
    errs.extend(_errs_run_end_run_id_type(b))
    errs.extend(_errs_run_end_artifacts(b))
    errs.extend(_errs_run_end_optional_refs(b))
    return errs
