from __future__ import annotations

from workflow_pipelines.orchestration_stage_event.surface import describe_surface


def test_describe_surface_returns_expected_shape() -> None:
    payload = describe_surface()
    assert payload["subheading"] == "workflow_pipelines/orchestration_stage_event"
    assert payload["status"] == "implemented"
    refs = payload["references"]
    assert isinstance(refs, list)
    assert "workflow_pipelines.orchestration_stage_event.runtime" in refs
