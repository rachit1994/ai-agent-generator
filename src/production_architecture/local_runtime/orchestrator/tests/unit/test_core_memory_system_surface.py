from __future__ import annotations

import importlib

import pytest


def test_describe_surface_has_expected_shape() -> None:
    module = importlib.import_module("core_components.memory_system.surface")
    payload = module.describe_surface()
    assert payload == {
        "subheading": "core_components/memory_system",
        "status": "scaffold",
        "references": [
            "guardrails_and_safety.risk_budgets_permission_matrix.risk_budgets.hard_stops_memory",
            "production_architecture.local_runtime.orchestrator.tests.unit.test_memory_hard_stops",
            "workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.memory_artifact_layer",
        ],
    }


def test_describe_surface_rejects_blank_subheading(monkeypatch: pytest.MonkeyPatch) -> None:
    module = importlib.import_module("core_components.memory_system.surface")
    monkeypatch.setattr(module, "SUBHEADING", "")
    with pytest.raises(ValueError, match="SUBHEADING"):
        module.describe_surface()


def test_describe_surface_rejects_blank_status(monkeypatch: pytest.MonkeyPatch) -> None:
    module = importlib.import_module("core_components.memory_system.surface")
    monkeypatch.setattr(module, "IMPLEMENTATION_STATUS", "   ")
    with pytest.raises(ValueError, match="IMPLEMENTATION_STATUS"):
        module.describe_surface()


def test_describe_surface_fails_closed_on_duplicate_reference(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = importlib.import_module("core_components.memory_system.surface")
    monkeypatch.setattr(module, "REFERENCE_MODULES", ["a.b.c", "a.b.c"])
    payload = module.describe_surface()
    assert payload["references"] == []

