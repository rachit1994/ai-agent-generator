from __future__ import annotations

from production_architecture.memory_architecture_in_runtime import (
    build_memory_architecture_in_runtime,
    execute_memory_architecture_runtime,
    validate_memory_architecture_in_runtime_dict,
)


def test_build_memory_architecture_in_runtime_is_deterministic() -> None:
    retrieval_bundle = {"chunks": [{"text": "x"}]}
    quality_metrics = {"contradiction_rate": 0.1}
    quarantine = []
    one = build_memory_architecture_in_runtime(
        run_id="rid-memory-runtime",
        retrieval_bundle=retrieval_bundle,
        quality_metrics=quality_metrics,
        quarantine_lines=quarantine,
    )
    two = build_memory_architecture_in_runtime(
        run_id="rid-memory-runtime",
        retrieval_bundle=retrieval_bundle,
        quality_metrics=quality_metrics,
        quarantine_lines=quarantine,
    )
    assert one == two
    assert validate_memory_architecture_in_runtime_dict(one) == []
    assert one["execution"]["chunks_processed"] == 1


def test_validate_memory_architecture_in_runtime_fail_closed() -> None:
    errs = validate_memory_architecture_in_runtime_dict({"schema": "bad"})
    assert "memory_architecture_in_runtime_schema" in errs
    assert "memory_architecture_in_runtime_schema_version" in errs
    assert "memory_architecture_in_runtime_evidence" in errs


def test_validate_memory_architecture_in_runtime_rejects_bad_evidence_refs() -> None:
    payload = build_memory_architecture_in_runtime(
        run_id="rid-memory-runtime",
        retrieval_bundle={"chunks": [{"text": "x"}]},
        quality_metrics={"contradiction_rate": 0.1},
        quarantine_lines=[],
    )
    payload["evidence"]["retrieval_bundle_ref"] = "memory/other.json"
    errs = validate_memory_architecture_in_runtime_dict(payload)
    assert "memory_architecture_in_runtime_evidence_ref:retrieval_bundle_ref" in errs


def test_validate_memory_architecture_in_runtime_rejects_status_semantics_mismatch() -> None:
    payload = build_memory_architecture_in_runtime(
        run_id="rid-memory-runtime",
        retrieval_bundle={"chunks": [{"text": "x"}]},
        quality_metrics={"contradiction_rate": 0.1},
        quarantine_lines=[],
    )
    payload["status"] = "missing"
    errs = validate_memory_architecture_in_runtime_dict(payload)
    assert "memory_architecture_in_runtime_status_semantics:missing" in errs


def test_execute_memory_architecture_runtime_detects_malformed_rows() -> None:
    execution = execute_memory_architecture_runtime(
        retrieval_bundle={"chunks": [{"text": "x"}, "bad-row"]},  # type: ignore[list-item]
        quality_metrics={},
        quarantine_lines=["ok", {"bad": True}],  # type: ignore[list-item]
    )
    assert execution["chunks_processed"] == 2
    assert execution["quarantine_rows_processed"] == 2
    assert execution["malformed_chunk_rows"] == 1
    assert execution["malformed_quarantine_rows"] == 1
    assert execution["missing_quality_fields"] == ["contradiction_rate"]
