from __future__ import annotations

from production_architecture.storage import (
    build_storage_architecture,
    validate_storage_architecture_dict,
)


def test_build_storage_architecture_is_deterministic() -> None:
    manifest = [
        {"path": "summary.json", "present": True},
        {"path": "review.json", "present": True},
        {"path": "event_store/run_events.jsonl", "present": True},
        {"path": "replay_manifest.json", "present": True},
        {"path": "memory/retrieval_bundle.json", "present": True},
        {"path": "memory/quality_metrics.json", "present": True},
    ]
    envelopes = [{"run_id": "rid-storage", "payload": {"event_id": "evt-1", "type": "x", "sha256": "abc"}}]
    retrieval = {"chunks": [{"confidence": 0.5}]}
    quality = {"contradiction_rate": 0.0}
    one = build_storage_architecture(
        run_id="rid-storage",
        mode="guarded_pipeline",
        artifact_manifest=manifest,
        event_envelopes=envelopes,
        retrieval_bundle=retrieval,
        quality_metrics=quality,
    )
    two = build_storage_architecture(
        run_id="rid-storage",
        mode="guarded_pipeline",
        artifact_manifest=manifest,
        event_envelopes=envelopes,
        retrieval_bundle=retrieval,
        quality_metrics=quality,
    )
    assert one == two
    assert validate_storage_architecture_dict(one) == []


def test_validate_storage_architecture_fail_closed() -> None:
    errs = validate_storage_architecture_dict({"schema": "bad"})
    assert "storage_architecture_schema" in errs
    assert "storage_architecture_schema_version" in errs

