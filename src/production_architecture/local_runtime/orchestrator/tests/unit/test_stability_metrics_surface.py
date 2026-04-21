from __future__ import annotations

from success_criteria.stability_metrics.surface import describe_surface


def test_describe_surface_returns_expected_shape() -> None:
    payload = describe_surface()
    assert payload["subheading"] == "success_criteria/stability_metrics"
    assert payload["status"] == "implemented"
    refs = payload["references"]
    assert isinstance(refs, list)
    assert "success_criteria.stability_metrics.runtime" in refs
