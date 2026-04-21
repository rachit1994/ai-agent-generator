from __future__ import annotations

import importlib

import pytest


def test_describe_surface_has_expected_shape() -> None:
    module = importlib.import_module("core_components.role_agents.surface")
    payload = module.describe_surface()
    assert payload == {
        "subheading": "core_components/role_agents",
        "status": "implemented",
        "references": [
            "core_components.role_agents.runtime",
            "core_components.role_agents.contracts",
            "workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.role_agents_layer",
            "guardrails_and_safety.review_gating_evaluator_authority.review_gating.run_directory",
        ],
    }


def test_describe_surface_rejects_blank_subheading(monkeypatch: pytest.MonkeyPatch) -> None:
    module = importlib.import_module("core_components.role_agents.surface")
    monkeypatch.setattr(module, "SUBHEADING", "   ")
    with pytest.raises(ValueError, match="SUBHEADING"):
        module.describe_surface()


def test_describe_surface_rejects_blank_status(monkeypatch: pytest.MonkeyPatch) -> None:
    module = importlib.import_module("core_components.role_agents.surface")
    monkeypatch.setattr(module, "IMPLEMENTATION_STATUS", "")
    with pytest.raises(ValueError, match="IMPLEMENTATION_STATUS"):
        module.describe_surface()


def test_describe_surface_fails_closed_on_malformed_references(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = importlib.import_module("core_components.role_agents.surface")
    monkeypatch.setattr(module, "REFERENCE_MODULES", ["valid.path", ""])
    payload = module.describe_surface()
    assert payload["references"] == []

