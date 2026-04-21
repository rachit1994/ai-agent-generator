"""Deterministic event-store semantics derivation."""

from __future__ import annotations

from typing import Any

from .contracts import EVENT_STORE_SEMANTICS_CONTRACT, EVENT_STORE_SEMANTICS_SCHEMA_VERSION


def _clamp01(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return round(value, 4)


def build_event_store_semantics(
    *,
    run_id: str,
    replay_manifest: dict[str, Any],
    run_events: list[dict[str, Any]],
    trace_events: list[dict[str, Any]],
) -> dict[str, Any]:
    trace_count = len(trace_events)
    event_count = len(run_events)
    coverage = _clamp01(event_count / max(1, trace_count))
    chain_root = replay_manifest.get("chain_root") if isinstance(replay_manifest, dict) else None
    source_sha = None
    if isinstance(replay_manifest, dict):
        sources = replay_manifest.get("sources")
        if isinstance(sources, list) and sources and isinstance(sources[0], dict):
            source_sha = sources[0].get("sha256")
    root_matches = isinstance(chain_root, str) and isinstance(source_sha, str) and chain_root == source_sha
    status = "broken"
    if event_count > 0 and trace_count > 0 and coverage >= 1.0 and root_matches:
        status = "aligned"
    elif event_count > 0 and coverage > 0.0:
        status = "partial"
    return {
        "schema": EVENT_STORE_SEMANTICS_CONTRACT,
        "schema_version": EVENT_STORE_SEMANTICS_SCHEMA_VERSION,
        "run_id": run_id,
        "status": status,
        "metrics": {
            "event_count": event_count,
            "trace_count": trace_count,
            "coverage": coverage,
            "chain_root_matches_source": root_matches,
        },
        "evidence": {
            "replay_manifest_ref": "replay_manifest.json",
            "run_events_ref": "event_store/run_events.jsonl",
            "traces_ref": "traces.jsonl",
            "semantics_ref": "event_store/semantics.json",
        },
    }
