from __future__ import annotations

from workflow_pipelines.benchmark_orchestration_jsonl.surface import describe_surface


def test_describe_surface_returns_expected_shape() -> None:
    payload = describe_surface()
    assert payload["subheading"] == "workflow_pipelines/benchmark_orchestration_jsonl"
    assert payload["status"] == "implemented"
    refs = payload["references"]
    assert isinstance(refs, list)
    assert "workflow_pipelines.benchmark_orchestration_jsonl.runtime" in refs
