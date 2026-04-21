from __future__ import annotations

from service_boundaries import build_service_boundaries, validate_service_boundaries_dict


def test_build_service_boundaries_is_deterministic() -> None:
    manifest = [
        {"path": "traces.jsonl", "present": True},
        {"path": "orchestration.jsonl", "present": True},
        {"path": "summary.json", "present": True},
        {"path": "review.json", "present": True},
    ]
    one = build_service_boundaries(run_id="rid-sb", mode="guarded_pipeline", artifact_manifest=manifest)
    two = build_service_boundaries(run_id="rid-sb", mode="guarded_pipeline", artifact_manifest=manifest)
    assert one == two
    assert validate_service_boundaries_dict(one) == []


def test_validate_service_boundaries_fail_closed() -> None:
    errs = validate_service_boundaries_dict({"schema": "bad"})
    assert "service_boundaries_schema" in errs
    assert "service_boundaries_schema_version" in errs


def test_validate_service_boundaries_rejects_status_semantics_mismatch() -> None:
    payload = build_service_boundaries(
        run_id="rid-sb",
        mode="guarded_pipeline",
        artifact_manifest=[
            {"path": "traces.jsonl", "present": True},
            {"path": "orchestration.jsonl", "present": True},
            {"path": "summary.json", "present": True},
            {"path": "review.json", "present": True},
        ],
    )
    payload["status"] = "bounded"
    payload["violations"] = [{"service": "event_store", "missing_path": "event_store/run_events.jsonl"}]
    errs = validate_service_boundaries_dict(payload)
    assert "service_boundaries_status_semantics" in errs


def test_validate_service_boundaries_rejects_service_coverage_mismatch() -> None:
    payload = build_service_boundaries(
        run_id="rid-sb",
        mode="guarded_pipeline",
        artifact_manifest=[
            {"path": "traces.jsonl", "present": True},
            {"path": "orchestration.jsonl", "present": True},
            {"path": "summary.json", "present": True},
            {"path": "review.json", "present": True},
        ],
    )
    payload["services"]["orchestrator"]["coverage"] = 0.0
    errs = validate_service_boundaries_dict(payload)
    assert "service_boundaries_coverage_mismatch:orchestrator" in errs

