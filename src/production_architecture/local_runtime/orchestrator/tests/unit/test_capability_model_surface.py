from __future__ import annotations

import importlib

import pytest


def test_describe_surface_has_expected_shape() -> None:
    module = importlib.import_module("capability_model.surface")
    payload = module.describe_surface()
    assert payload == {
        "subheading": "capability_model",
        "status": "implemented",
        "references": [
            "capability_model.runtime",
            "capability_model.contracts",
            "workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.memory_artifact_layer",
            "workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.evolution_layer",
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

