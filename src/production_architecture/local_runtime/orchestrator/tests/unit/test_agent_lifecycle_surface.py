from __future__ import annotations

import importlib

import pytest


def test_describe_surface_has_expected_shape() -> None:
    module = importlib.import_module("agent_lifecycle.surface")
    payload = module.describe_surface()
    assert payload == {
        "subheading": "agent_lifecycle",
        "status": "scaffold",
        "references": [
            "agent_lifecycle.autonomy_levels_trust_progression.surface",
            "agent_lifecycle.demotion_logic.surface",
            "agent_lifecycle.lifecycle_stages_graph.surface",
            "agent_lifecycle.promotion_rules.surface",
            "agent_lifecycle.recertification_decay.surface",
            "agent_lifecycle.stagnation_detection.surface",
        ],
    }


def test_describe_surface_rejects_blank_subheading(monkeypatch: pytest.MonkeyPatch) -> None:
    module = importlib.import_module("agent_lifecycle.surface")
    monkeypatch.setattr(module, "SUBHEADING", "")
    with pytest.raises(ValueError, match="SUBHEADING"):
        module.describe_surface()


def test_describe_surface_rejects_blank_status(monkeypatch: pytest.MonkeyPatch) -> None:
    module = importlib.import_module("agent_lifecycle.surface")
    monkeypatch.setattr(module, "IMPLEMENTATION_STATUS", " ")
    with pytest.raises(ValueError, match="IMPLEMENTATION_STATUS"):
        module.describe_surface()


def test_describe_surface_fails_closed_on_malformed_references(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = importlib.import_module("agent_lifecycle.surface")
    monkeypatch.setattr(module, "REFERENCE_MODULES", ["valid.path", ""])
    payload = module.describe_surface()
    assert payload["references"] == []

