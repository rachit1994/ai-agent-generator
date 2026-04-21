"""Deterministic auditability artifact derivation."""

from __future__ import annotations

from typing import Any

from .contracts import AUDITABILITY_CONTRACT, AUDITABILITY_SCHEMA_VERSION


def build_auditability(
    *,
    run_id: str,
    mode: str,
    replay_manifest: dict[str, Any],
    run_events: list[dict[str, Any]],
    kill_switch_state: dict[str, Any],
    review: dict[str, Any],
) -> dict[str, Any]:
    chain_root_raw = replay_manifest.get("chain_root")
    chain_root = chain_root_raw.strip() if isinstance(chain_root_raw, str) and chain_root_raw.strip() else "missing"
    latest_hash = chain_root
    for row in run_events:
        payload = row.get("payload")
        if not isinstance(payload, dict):
            continue
        digest = payload.get("sha256")
        if isinstance(digest, str) and digest.strip():
            latest_hash = digest.strip()
    event_count = len(run_events)
    hash_chain_valid = chain_root != "missing" and event_count > 0 and latest_hash == chain_root
    latched = bool(kill_switch_state.get("latched"))
    review_ok = review.get("status") in {"completed_review_pass", "completed_review_warn"}
    periodic_check_supported = True
    last_check_passed = hash_chain_valid and not latched
    checks_performed = 1 if replay_manifest else 0
    status = "degraded"
    if hash_chain_valid and review_ok and last_check_passed:
        status = "verifiable"
    elif event_count == 0 or chain_root == "missing":
        status = "inconsistent"
    return {
        "schema": AUDITABILITY_CONTRACT,
        "schema_version": AUDITABILITY_SCHEMA_VERSION,
        "run_id": run_id,
        "mode": mode,
        "status": status,
        "hash_chain": {
            "chain_root": chain_root,
            "latest_hash": latest_hash,
            "event_count": event_count,
            "hash_chain_valid": hash_chain_valid,
        },
        "integrity_operations": {
            "periodic_check_supported": periodic_check_supported,
            "last_check_passed": last_check_passed,
            "checks_performed": checks_performed,
        },
        "evidence": {
            "replay_manifest_ref": "replay_manifest.json",
            "event_store_ref": "event_store/run_events.jsonl",
            "kill_switch_ref": "kill_switch_state.json",
            "review_ref": "review.json",
            "auditability_ref": "audit/auditability.json",
        },
    }
