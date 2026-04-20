from __future__ import annotations

import importlib

import pytest


def test_describe_surface_has_expected_shape() -> None:
    module = importlib.import_module("human_professional_evolution_model.surface")
    payload = module.describe_surface()
    assert payload == {
        "subheading": "human_professional_evolution_model",
        "status": "scaffold",
        "references": [
            "human_professional_evolution_model.career_progression_model.surface",
            "human_professional_evolution_model.deliberate_practice.surface",
            "human_professional_evolution_model.feedback_loops.surface",
            "human_professional_evolution_model.human_growth_loop.surface",
            "human_professional_evolution_model.human_to_agent_behavior_mapping.surface",
            "human_professional_evolution_model.institutional_memory.surface",
            "human_professional_evolution_model.mentorship_operating_model.surface",
            "human_professional_evolution_model.performance_review_cycle.surface",
        ],
    }


def test_describe_surface_rejects_blank_subheading(monkeypatch: pytest.MonkeyPatch) -> None:
    module = importlib.import_module("human_professional_evolution_model.surface")
    monkeypatch.setattr(module, "SUBHEADING", "")
    with pytest.raises(ValueError, match="SUBHEADING"):
        module.describe_surface()


def test_describe_surface_rejects_blank_status(monkeypatch: pytest.MonkeyPatch) -> None:
    module = importlib.import_module("human_professional_evolution_model.surface")
    monkeypatch.setattr(module, "IMPLEMENTATION_STATUS", " ")
    with pytest.raises(ValueError, match="IMPLEMENTATION_STATUS"):
        module.describe_surface()


def test_describe_surface_fails_closed_on_malformed_references(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = importlib.import_module("human_professional_evolution_model.surface")
    monkeypatch.setattr(module, "REFERENCE_MODULES", ["valid.path", ""])
    payload = module.describe_surface()
    assert payload["references"] == []

