"""Deterministic local storage architecture derivation."""

from __future__ import annotations

from typing import Any

from .contracts import STORAGE_ARCHITECTURE_CONTRACT, STORAGE_ARCHITECTURE_SCHEMA_VERSION


def build_storage_architecture(
    *,
    run_id: str,
    mode: str,
    artifact_manifest: list[dict[str, Any]],
    event_envelopes: list[dict[str, Any]],
    retrieval_bundle: dict[str, Any],
    quality_metrics: dict[str, Any],
) -> dict[str, Any]:
    present_paths = {
        str(row.get("path"))
        for row in artifact_manifest
        if isinstance(row, dict) and bool(row.get("present")) and isinstance(row.get("path"), str)
    }
    required = sorted(
        [
            "event_store/run_events.jsonl",
            "replay_manifest.json",
            "memory/retrieval_bundle.json",
            "memory/quality_metrics.json",
            "summary.json",
            "review.json",
        ]
    )
    present = sum(1 for path in required if path in present_paths)
    coverage = round((present / len(required)) if required else 0.0, 4)
    chunks = retrieval_bundle.get("chunks") if isinstance(retrieval_bundle, dict) else []
    if not isinstance(chunks, list):
        chunks = []
    confidences = [
        float(row.get("confidence"))
        for row in chunks
        if isinstance(row, dict)
        and isinstance(row.get("confidence"), (int, float))
        and not isinstance(row.get("confidence"), bool)
    ]
    avg_confidence = round((sum(confidences) / len(confidences)) if confidences else 0.0, 4)
    contradiction_rate = 0.0
    if isinstance(quality_metrics, dict):
        raw = quality_metrics.get("contradiction_rate")
        if isinstance(raw, (int, float)) and not isinstance(raw, bool):
            contradiction_rate = round(float(raw), 4)
    latest = event_envelopes[-1] if event_envelopes else {}
    payload = latest.get("payload") if isinstance(latest, dict) and isinstance(latest.get("payload"), dict) else {}
    trace_digest_matches = isinstance(payload.get("sha256"), str) and bool(payload.get("sha256"))
    run_alignment_ok = isinstance(latest, dict) and str(latest.get("run_id", "")).strip() == run_id
    status = "consistent"
    if coverage < 1.0 or not trace_digest_matches:
        status = "degraded"
    if not run_alignment_ok:
        status = "inconsistent"
    return {
        "schema": STORAGE_ARCHITECTURE_CONTRACT,
        "schema_version": STORAGE_ARCHITECTURE_SCHEMA_VERSION,
        "run_id": run_id,
        "mode": mode,
        "status": status,
        "event_store": {
            "run_events_ref": "event_store/run_events.jsonl",
            "envelope_count": len(event_envelopes),
            "latest_event_id": payload.get("event_id", ""),
            "latest_payload_type": payload.get("type", ""),
            "latest_payload_sha256": payload.get("sha256", ""),
        },
        "projections": {
            "artifact_manifest_ref": "review.json",
            "required_paths_count": len(required),
            "present_paths_count": present,
            "coverage": coverage,
        },
        "vector_memory": {
            "retrieval_bundle_ref": "memory/retrieval_bundle.json",
            "chunks_count": len(chunks),
            "avg_confidence": avg_confidence,
            "quality_ref": "memory/quality_metrics.json",
            "contradiction_rate": contradiction_rate,
        },
        "consistency": {
            "trace_digest_ref": "replay_manifest.json",
            "trace_digest_matches_event_payload": trace_digest_matches,
            "run_id_alignment_ok": run_alignment_ok,
        },
        "evidence": {
            "summary_ref": "summary.json",
            "review_ref": "review.json",
            "storage_ref": "storage/storage_architecture.json",
        },
    }

