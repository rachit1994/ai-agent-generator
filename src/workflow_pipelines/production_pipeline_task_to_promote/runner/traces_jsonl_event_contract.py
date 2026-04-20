"""Contract for one ``TraceEvent``-shaped object written to ``traces.jsonl``."""

from __future__ import annotations

from typing import Any, Final

TRACES_JSONL_EVENT_CONTRACT: Final = "sde.traces_jsonl_event.v1"

_ALLOWED_MODES: Final = frozenset({"baseline", "guarded_pipeline", "phased_pipeline"})


def _errs_trace_unknown_keys(body: dict[str, Any]) -> list[str]:
    allowed = frozenset(
        {
            "run_id",
            "task_id",
            "mode",
            "model",
            "provider",
            "stage",
            "started_at",
            "ended_at",
            "latency_ms",
            "token_input",
            "token_output",
            "estimated_cost_usd",
            "retry_count",
            "errors",
            "score",
            "metadata",
        },
    )
    extra = set(body.keys()) - allowed
    if extra:
        return ["traces_jsonl_event_unknown_keys"]
    return []


def _errs_trace_ids_mode(body: dict[str, Any]) -> list[str]:
    errs: list[str] = []
    rid = body.get("run_id")
    if not isinstance(rid, str) or not rid.strip():
        errs.append("traces_jsonl_event_run_id")
    tid = body.get("task_id")
    if not isinstance(tid, str) or not tid.strip():
        errs.append("traces_jsonl_event_task_id")
    mode = body.get("mode")
    if mode not in _ALLOWED_MODES:
        errs.append("traces_jsonl_event_mode")
    return errs


def _errs_trace_model_provider_stage(body: dict[str, Any]) -> list[str]:
    errs: list[str] = []
    for key in ("model", "provider"):
        v = body.get(key)
        if not isinstance(v, str) or not v.strip():
            errs.append(f"traces_jsonl_event_{key}")
    st = body.get("stage")
    if not isinstance(st, str) or not st.strip():
        errs.append("traces_jsonl_event_stage")
    return errs


def _errs_trace_timing_tokens(body: dict[str, Any]) -> list[str]:
    errs: list[str] = []
    sa = body.get("started_at")
    if not isinstance(sa, str) or not sa.strip():
        errs.append("traces_jsonl_event_started_at")
    ea = body.get("ended_at")
    if not isinstance(ea, str) or not ea.strip():
        errs.append("traces_jsonl_event_ended_at")
    lat = body.get("latency_ms")
    if not isinstance(lat, int) or lat < 0:
        errs.append("traces_jsonl_event_latency_ms")
    ti = body.get("token_input")
    if not isinstance(ti, int) or ti < 0:
        errs.append("traces_jsonl_event_token_input")
    to = body.get("token_output")
    if not isinstance(to, int) or to < 0:
        errs.append("traces_jsonl_event_token_output")
    cost = body.get("estimated_cost_usd")
    if not isinstance(cost, (int, float)) or cost < 0:
        errs.append("traces_jsonl_event_estimated_cost_usd")
    return errs


def _errs_trace_retry_errors_score(body: dict[str, Any]) -> list[str]:
    errs: list[str] = []
    rc = body.get("retry_count")
    if not isinstance(rc, int) or rc < 0:
        errs.append("traces_jsonl_event_retry_count")
    er = body.get("errors")
    if not isinstance(er, list):
        errs.append("traces_jsonl_event_errors")
    else:
        for idx, item in enumerate(er):
            if not isinstance(item, str):
                errs.append(f"traces_jsonl_event_errors_item:{idx}")
                break
    sc = body.get("score")
    if not isinstance(sc, dict):
        errs.append("traces_jsonl_event_score")
    else:
        if "passed" not in sc or not isinstance(sc.get("passed"), bool):
            errs.append("traces_jsonl_event_score_passed")
        rel = sc.get("reliability")
        val = sc.get("validity")
        if not isinstance(rel, (int, float)) or not isinstance(val, (int, float)):
            errs.append("traces_jsonl_event_score_metrics")
    return errs


def _errs_trace_metadata(body: dict[str, Any]) -> list[str]:
    meta = body.get("metadata")
    if meta is not None and not isinstance(meta, dict):
        return ["traces_jsonl_event_metadata"]
    return []


def validate_traces_jsonl_event_dict(body: Any) -> list[str]:
    """Return stable error tokens for one ``TraceEvent``-compatible ``traces.jsonl`` row."""
    if not isinstance(body, dict):
        return ["traces_jsonl_event_not_object"]
    b = body
    errs: list[str] = []
    errs.extend(_errs_trace_unknown_keys(b))
    errs.extend(_errs_trace_ids_mode(b))
    errs.extend(_errs_trace_model_provider_stage(b))
    errs.extend(_errs_trace_timing_tokens(b))
    errs.extend(_errs_trace_retry_errors_score(b))
    errs.extend(_errs_trace_metadata(b))
    return errs
