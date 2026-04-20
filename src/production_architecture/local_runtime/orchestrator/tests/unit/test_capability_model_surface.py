from __future__ import annotations

import importlib

import pytest


def test_describe_surface_has_expected_shape() -> None:
    module = importlib.import_module("capability_model.surface")
    payload = module.describe_surface()
    assert payload == {
        "subheading": "capability_model",
        "status": "scaffold",
        "references": [
            "capability_model.capability_graph.surface",
            "capability_model.dependency_aware_promotion_eligibility.surface",
            "capability_model.scoring_confidence_decay.surface",
            "capability_model.transfer_learning_measurement.surface",
        ],
    }


def test_describe_surface_rejects_blank_subheading(monkeypatch: pytest.MonkeyPatch) -> None:
    module = importlib.import_module("capability_model.surface")
    monkeypatch.setattr(module, "SUBHEADING", "")
    with pytest.raises(ValueError, match="SUBHEADING"):
        module.describe_surface()


def test_describe_surface_rejects_blank_status(monkeypatch: pytest.MonkeyPatch) -> None:
    module = importlib.import_module("capability_model.surface")
    monkeypatch.setattr(module, "IMPLEMENTATION_STATUS", " ")
    with pytest.raises(ValueError, match="IMPLEMENTATION_STATUS"):
        module.describe_surface()


def test_describe_surface_fails_closed_on_malformed_references(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = importlib.import_module("capability_model.surface")
    monkeypatch.setattr(module, "REFERENCE_MODULES", ["valid.path", ""])
    payload = module.describe_surface()
    assert payload["references"] == []

