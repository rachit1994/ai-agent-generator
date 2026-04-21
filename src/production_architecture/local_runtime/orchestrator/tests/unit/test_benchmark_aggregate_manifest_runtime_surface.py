from __future__ import annotations

from workflow_pipelines.benchmark_aggregate_manifest.surface import describe_surface


def test_describe_surface_returns_expected_shape() -> None:
    payload = describe_surface()
    assert payload["subheading"] == "workflow_pipelines/benchmark_aggregate_manifest"
    assert payload["status"] == "implemented"
    refs = payload["references"]
    assert isinstance(refs, list)
    assert "workflow_pipelines.benchmark_aggregate_manifest.runtime" in refs
