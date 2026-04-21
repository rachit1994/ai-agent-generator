"""Deterministic replay fail-closed derivation."""

from __future__ import annotations

from typing import Any

from .contracts import REPLAY_FAIL_CLOSED_CONTRACT, REPLAY_FAIL_CLOSED_SCHEMA_VERSION


def build_replay_fail_closed(
    *,
    run_id: str,
    replay_manifest: dict[str, Any],
    trace_rows: list[dict[str, Any]],
    event_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    chain_root = replay_manifest.get("chain_root") if isinstance(replay_manifest, dict) else None
    sources = replay_manifest.get("sources") if isinstance(replay_manifest, dict) else []
    source_hash = None
    if isinstance(sources, list) and sources and isinstance(sources[0], dict):
        source_hash = sources[0].get("sha256")
    checks = {
        "replay_manifest_present": bool(replay_manifest),
        "trace_rows_present": len(trace_rows) > 0,
        "event_rows_present": len(event_rows) > 0,
        "chain_root_present": isinstance(chain_root, str) and bool(chain_root.strip()),
        "chain_root_matches_trace_hash": isinstance(chain_root, str)
        and isinstance(source_hash, str)
        and chain_root == source_hash,
    }
    status = "pass" if all(checks.values()) else "fail"
    return {
        "schema": REPLAY_FAIL_CLOSED_CONTRACT,
        "schema_version": REPLAY_FAIL_CLOSED_SCHEMA_VERSION,
        "run_id": run_id,
        "status": status,
        "checks": checks,
        "evidence": {
            "replay_manifest_ref": "replay_manifest.json",
            "traces_ref": "traces.jsonl",
            "run_events_ref": "event_store/run_events.jsonl",
            "replay_fail_closed_ref": "replay/fail_closed.json",
        },
    }
