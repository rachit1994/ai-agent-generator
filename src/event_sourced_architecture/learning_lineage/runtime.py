"""Deterministic learning-lineage derivation."""

from __future__ import annotations

from typing import Any

from .contracts import LEARNING_LINEAGE_CONTRACT, LEARNING_LINEAGE_SCHEMA_VERSION


def _clamp01(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return round(value, 4)


def build_learning_lineage(
    *,
    run_id: str,
    mode: str,
    replay_manifest: dict[str, Any],
    run_events: list[dict[str, Any]],
    reflection_bundle: dict[str, Any],
) -> dict[str, Any]:
    chain_root = replay_manifest.get("chain_root") if isinstance(replay_manifest, dict) else None
    has_chain_root = isinstance(chain_root, str) and bool(chain_root.strip())
    has_event_store = len(run_events) > 0
    linked_ids = reflection_bundle.get("linked_event_ids") if isinstance(reflection_bundle, dict) else []
    reflection_linked = isinstance(linked_ids, list) and len(linked_ids) > 0
    checks = {
        "manifest_has_chain_root": has_chain_root,
        "event_store_present": has_event_store,
        "reflection_linked": reflection_linked,
    }
    passed = sum(1 for ok in checks.values() if ok)
    coverage = _clamp01(passed / len(checks))
    status = "aligned" if coverage == 1.0 else ("partial" if coverage >= 0.5 else "broken")
    return {
        "schema": LEARNING_LINEAGE_CONTRACT,
        "schema_version": LEARNING_LINEAGE_SCHEMA_VERSION,
        "run_id": run_id,
        "mode": mode,
        "status": status,
        "checks": checks,
        "coverage": coverage,
        "evidence": {
            "replay_manifest_ref": "replay_manifest.json",
            "event_store_ref": "event_store/run_events.jsonl",
            "reflection_bundle_ref": "learning/reflection_bundle.json",
            "learning_lineage_ref": "learning/learning_lineage.json",
        },
    }
