from __future__ import annotations

import importlib

import pytest


def test_describe_surface_has_expected_shape() -> None:
    module = importlib.import_module("success_criteria.transfer_learning_metrics.surface")
    payload = module.describe_surface()
    assert payload == {
        "subheading": "success_criteria/transfer_learning_metrics",
        "status": "implemented",
        "references": [
            "success_criteria.transfer_learning_metrics.runtime",
            "success_criteria.transfer_learning_metrics.contracts",
            "workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.evolution_layer",
            "guardrails_and_safety.review_gating_evaluator_authority.review_gating.run_directory",
        ],
    }


def test_describe_surface_rejects_blank_subheading(monkeypatch: pytest.MonkeyPatch) -> None:
    module = importlib.import_module("success_criteria.transfer_learning_metrics.surface")
    monkeypatch.setattr(module, "SUBHEADING", "")
    with pytest.raises(ValueError, match="SUBHEADING"):
        module.describe_surface()
