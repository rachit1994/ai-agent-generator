"""Deterministic auditability artifact derivation."""

from __future__ import annotations

from typing import Any

from .contracts import AUDITABILITY_CONTRACT, AUDITABILITY_SCHEMA_VERSION


def _event_hash(row: Any) -> str | None:
    if not isinstance(row, dict):
        return None
    payload = row.get("payload")
    if not isinstance(payload, dict):
        return None
    digest = payload.get("sha256")
    if not isinstance(digest, str) or not digest.strip():
        return None
    return digest.strip()


def execute_auditability_runtime(*, replay_manifest: dict[str, Any], run_events: list[dict[str, Any]]) -> dict[str, Any]:
    chain_root_raw = replay_manifest.get("chain_root")
    chain_root = chain_root_raw.strip() if isinstance(chain_root_raw, str) and chain_root_raw.strip() else "missing"
    event_hashes = [digest for row in run_events if (digest := _event_hash(row)) is not None]
    malformed_event_rows = len(run_events) - len(event_hashes)
    latest_hash = event_hashes[-1] if event_hashes else chain_root
    chain_mismatch = bool(event_hashes) and chain_root != "missing" and latest_hash != chain_root
    return {
        "events_processed": len(run_events),
        "hashed_event_count": len(event_hashes),
        "malformed_event_rows": malformed_event_rows,
        "chain_mismatch": chain_mismatch,
        "latest_hash": latest_hash,
    }


def build_auditability(
    *,
    run_id: str,
    mode: str,
    replay_manifest: dict[str, Any],
    run_events: list[dict[str, Any]],
    kill_switch_state: dict[str, Any],
    review: dict[str, Any],
) -> dict[str, Any]:
    execution = execute_auditability_runtime(replay_manifest=replay_manifest, run_events=run_events)
    chain_root_raw = replay_manifest.get("chain_root")
    chain_root = chain_root_raw.strip() if isinstance(chain_root_raw, str) and chain_root_raw.strip() else "missing"
    latest_hash = execution["latest_hash"]
    event_count = len(run_events)
    hash_chain_valid = (
        chain_root != "missing"
        and event_count > 0
        and execution["chain_mismatch"] is False
        and execution["malformed_event_rows"] == 0
    )
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
        "execution": execution,
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
