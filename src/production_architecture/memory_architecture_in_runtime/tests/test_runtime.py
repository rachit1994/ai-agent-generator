from __future__ import annotations

from production_architecture.memory_architecture_in_runtime import (
    build_memory_architecture_in_runtime,
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


def test_validate_memory_architecture_in_runtime_fail_closed() -> None:
    errs = validate_memory_architecture_in_runtime_dict({"schema": "bad"})
    assert "memory_architecture_in_runtime_schema" in errs
    assert "memory_architecture_in_runtime_schema_version" in errs
