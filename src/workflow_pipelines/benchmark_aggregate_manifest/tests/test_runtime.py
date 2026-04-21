from __future__ import annotations

from workflow_pipelines.benchmark_aggregate_manifest import (
    build_benchmark_aggregate_manifest_runtime,
    validate_benchmark_aggregate_manifest_runtime_dict,
)


def test_build_benchmark_aggregate_manifest_runtime_deterministic() -> None:
    manifest = {"run_id": "bench-1"}
    checkpoint = {"run_id": "bench-1", "finished": True}
    one = build_benchmark_aggregate_manifest_runtime(manifest=manifest, checkpoint=checkpoint)
    two = build_benchmark_aggregate_manifest_runtime(manifest=manifest, checkpoint=checkpoint)
    assert one == two
    assert one["status"] == "finished"
    assert validate_benchmark_aggregate_manifest_runtime_dict(one) == []


def test_validate_benchmark_aggregate_manifest_runtime_fail_closed() -> None:
    errs = validate_benchmark_aggregate_manifest_runtime_dict({"schema": "bad"})
    assert "benchmark_aggregate_manifest_runtime_schema" in errs
    assert "benchmark_aggregate_manifest_runtime_schema_version" in errs
