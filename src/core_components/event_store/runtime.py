"""Deterministic derivation for core event-store component health."""

from __future__ import annotations

from typing import Any

from .contracts import EVENT_STORE_COMPONENT_CONTRACT, EVENT_STORE_COMPONENT_SCHEMA_VERSION


def _clamp01(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return round(value, 4)


def build_event_store_component(
    *,
    run_id: str,
    replay_manifest: dict[str, Any],
    run_events: list[dict[str, Any]],
    trace_events: list[dict[str, Any]],
    kill_switch_state: dict[str, Any],
) -> dict[str, Any]:
    trace_rows = len(trace_events)
    event_rows = len(run_events)
    append_coverage = _clamp01(event_rows / max(1, trace_rows))
    manifest_ok = bool(replay_manifest.get("passed")) if isinstance(replay_manifest, dict) else False
    kill_switch_latched = bool(kill_switch_state.get("latched")) if isinstance(kill_switch_state, dict) else False
    status = "missing"
    if event_rows > 0 and trace_rows > 0 and append_coverage >= 1.0 and manifest_ok and not kill_switch_latched:
        status = "healthy"
    elif event_rows > 0 and manifest_ok:
        status = "degraded"
    return {
        "schema": EVENT_STORE_COMPONENT_CONTRACT,
        "schema_version": EVENT_STORE_COMPONENT_SCHEMA_VERSION,
        "run_id": run_id,
        "status": status,
        "metrics": {
            "event_rows": event_rows,
            "trace_rows": trace_rows,
            "append_coverage": append_coverage,
            "manifest_passed": manifest_ok,
            "kill_switch_latched": kill_switch_latched,
        },
        "evidence": {
            "replay_manifest_ref": "replay_manifest.json",
            "run_events_ref": "event_store/run_events.jsonl",
            "traces_ref": "traces.jsonl",
            "kill_switch_state_ref": "kill_switch_state.json",
            "component_ref": "event_store/component_runtime.json",
        },
    }
