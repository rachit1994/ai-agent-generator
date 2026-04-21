from __future__ import annotations

from core_components.memory_system import build_memory_system, validate_memory_system_dict


def _valid_payload() -> dict[str, object]:
    return build_memory_system(
        run_id="rid-contracts",
        retrieval_bundle={"chunks": [{"text": "x"}]},
        quality_metrics={"contradiction_rate": 0.0, "staleness_p95_hours": 1.0},
        quarantine_rows=[],
    )


def test_validate_memory_system_rejects_non_object_payload() -> None:
    assert validate_memory_system_dict([]) == ["memory_system_not_object"]


def test_validate_memory_system_rejects_bad_top_level_contract_fields() -> None:
    payload = _valid_payload()
    payload["schema"] = "bad"
    payload["schema_version"] = "2.0"
    payload["run_id"] = " "
    payload["status"] = "unknown"
    errs = validate_memory_system_dict(payload)
    assert "memory_system_schema" in errs
    assert "memory_system_schema_version" in errs
    assert "memory_system_run_id" in errs
    assert "memory_system_status" in errs


def test_validate_memory_system_rejects_out_of_range_metrics() -> None:
    payload = _valid_payload()
    metrics = payload["metrics"]
    assert isinstance(metrics, dict)
    metrics["quality_score"] = 1.1
    metrics["contradiction_rate"] = -0.01
    errs = validate_memory_system_dict(payload)
    assert "memory_system_quality_score_range" in errs
    assert "memory_system_contradiction_rate_range" in errs


def test_validate_memory_system_rejects_healthy_with_quarantine_rows() -> None:
    payload = _valid_payload()
    metrics = payload["metrics"]
    assert isinstance(metrics, dict)
    metrics["quarantine_rows"] = 2
    errs = validate_memory_system_dict(payload)
    assert "memory_system_status_semantics:healthy" in errs


def test_validate_memory_system_rejects_missing_with_nonzero_chunks() -> None:
    payload = _valid_payload()
    payload["status"] = "missing"
    errs = validate_memory_system_dict(payload)
    assert "memory_system_status_semantics:missing" in errs


def test_validate_memory_system_rejects_missing_evidence_key() -> None:
    payload = _valid_payload()
    evidence = payload["evidence"]
    assert isinstance(evidence, dict)
    del evidence["quarantine_ref"]
    errs = validate_memory_system_dict(payload)
    assert "memory_system_evidence_missing:quarantine_ref" in errs
