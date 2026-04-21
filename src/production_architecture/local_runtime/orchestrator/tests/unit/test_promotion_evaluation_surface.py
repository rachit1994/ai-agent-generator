from __future__ import annotations

from evaluation_framework.promotion_evaluation.surface import describe_surface


def test_describe_surface_returns_expected_shape() -> None:
    payload = describe_surface()
    assert payload["subheading"] == "evaluation_framework/promotion_evaluation"
    assert payload["status"] == "implemented"
    refs = payload["references"]
    assert isinstance(refs, list)
    assert "evaluation_framework.promotion_evaluation.runtime" in refs
