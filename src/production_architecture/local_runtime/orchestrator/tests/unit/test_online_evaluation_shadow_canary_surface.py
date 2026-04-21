from __future__ import annotations

from evaluation_framework.online_evaluation_shadow_canary_artifact.surface import (
    describe_surface,
)


def test_describe_surface_returns_expected_shape() -> None:
    payload = describe_surface()
    assert (
        payload["subheading"]
        == "evaluation_framework/online_evaluation_shadow_canary_artifact"
    )
    assert payload["status"] == "implemented"
    refs = payload["references"]
    assert isinstance(refs, list)
    assert (
        "evaluation_framework.online_evaluation_shadow_canary_artifact.runtime" in refs
    )
