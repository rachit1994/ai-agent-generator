from __future__ import annotations

import importlib

import pytest


def test_describe_surface_has_expected_shape() -> None:
    module = importlib.import_module("agent_lifecycle.surface")
    payload = module.describe_surface()
    assert payload == {
        "subheading": "agent_lifecycle",
        "status": "implemented",
        "references": [
            "agent_lifecycle.runtime",
            "agent_lifecycle.contracts",
            "workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.evolution_layer",
            "guardrails_and_safety.risk_budgets_permission_matrix.risk_budgets.hard_stops_evolution",
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

