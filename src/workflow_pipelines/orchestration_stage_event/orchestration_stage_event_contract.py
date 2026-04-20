"""Contract for ``stage_event`` lines appended to ``orchestration.jsonl``."""

from __future__ import annotations

from typing import Any, Final

ORCHESTRATION_STAGE_EVENT_CONTRACT: Final = "sde.orchestration_stage_event.v1"
_ALLOWED_KEYS: Final = frozenset(
    {
        "run_id",
        "type",
        "stage",
        "retry_count",
        "errors",
        "agent",
        "model",
        "model_error",
        "attempt",
        "raw_response_excerpt",
        "started_at",
        "ended_at",
        "latency_ms",
    }
)


def _errs_stage_event_run_id(body: dict[str, Any]) -> list[str]:
    rid = body.get("run_id")
    if not isinstance(rid, str) or not rid.strip():
        return ["orchestration_stage_event_run_id"]
    return []


def _errs_stage_event_type(body: dict[str, Any]) -> list[str]:
    if body.get("type") != "stage_event":
        return ["orchestration_stage_event_type"]
    return []


def _errs_stage_event_stage(body: dict[str, Any]) -> list[str]:
    st = body.get("stage")
    if not isinstance(st, str) or not st.strip():
        return ["orchestration_stage_event_stage"]
    return []


def _errs_stage_event_retry_errors(body: dict[str, Any]) -> list[str]:
    errs: list[str] = []
    rc = body.get("retry_count")
    if not isinstance(rc, int) or isinstance(rc, bool) or rc < 0:
        errs.append("orchestration_stage_event_retry_count")
    er = body.get("errors")
    if er is None:
        errs.append("orchestration_stage_event_errors")
    elif not isinstance(er, list):
        errs.append("orchestration_stage_event_errors")
    else:
        for idx, item in enumerate(er):
            if not isinstance(item, str):
                errs.append(f"orchestration_stage_event_errors_item:{idx}")
                break
    return errs


def _errs_stage_event_timing(body: dict[str, Any]) -> list[str]:
    errs: list[str] = []
    sa = body.get("started_at")
    if not isinstance(sa, str) or not sa.strip():
        errs.append("orchestration_stage_event_started_at")
    ea = body.get("ended_at")
    if not isinstance(ea, str) or not ea.strip():
        errs.append("orchestration_stage_event_ended_at")
    lat = body.get("latency_ms")
    if not isinstance(lat, int) or isinstance(lat, bool) or lat < 0:
        errs.append("orchestration_stage_event_latency_ms")
    return errs


def _errs_stage_event_flat_metadata(body: dict[str, Any]) -> list[str]:
    errs: list[str] = []
    att = body.get("attempt")
    if att is not None and (not isinstance(att, int) or isinstance(att, bool)):
        errs.append("orchestration_stage_event_attempt")
    me = body.get("model_error")
    if me is not None and not isinstance(me, str):
        errs.append("orchestration_stage_event_model_error")
    return errs


def validate_orchestration_stage_event_line_dict(body: Any) -> list[str]:
    """Return stable error tokens for one flattened ``stage_event`` orchestration line."""
    if not isinstance(body, dict):
        return ["orchestration_stage_event_not_object"]
    b = body
    errs: list[str] = []
    errs.extend(_errs_stage_event_run_id(b))
    errs.extend(_errs_stage_event_type(b))
    errs.extend(_errs_stage_event_stage(b))
    errs.extend(_errs_stage_event_retry_errors(b))
    errs.extend(_errs_stage_event_timing(b))
    errs.extend(_errs_stage_event_flat_metadata(b))
    for key in b:
        if key not in _ALLOWED_KEYS:
            errs.append(f"orchestration_stage_event_unknown_key:{key}")
    return errs
