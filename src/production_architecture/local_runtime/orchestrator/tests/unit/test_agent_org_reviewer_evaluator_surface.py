from __future__ import annotations

import importlib

import pytest


def test_describe_surface_has_expected_shape() -> None:
    module = importlib.import_module("agent_organization.reviewer_evaluator_agents.surface")
    payload = module.describe_surface()
    assert payload == {
        "subheading": "agent_organization/reviewer_evaluator_agents",
        "status": "scaffold",
        "references": [
            "guardrails_and_safety.rollback_rules_policy_bundle.policy_bundle_rollback",
            "guardrails_and_safety.review_gating_evaluator_authority.review_gating.review",
            "guardrails_and_safety.review_gating_evaluator_authority.review_gating.run_directory",
            "guardrails_and_safety.review_gating_evaluator_authority.safeguards.safeguards",
        ],
    }


def test_describe_surface_rejects_blank_subheading(monkeypatch: pytest.MonkeyPatch) -> None:
    module = importlib.import_module("agent_organization.reviewer_evaluator_agents.surface")
    monkeypatch.setattr(module, "SUBHEADING", "")
    with pytest.raises(ValueError, match="SUBHEADING"):
        module.describe_surface()


def test_describe_surface_rejects_blank_status(monkeypatch: pytest.MonkeyPatch) -> None:
    module = importlib.import_module("agent_organization.reviewer_evaluator_agents.surface")
    monkeypatch.setattr(module, "IMPLEMENTATION_STATUS", " ")
    with pytest.raises(ValueError, match="IMPLEMENTATION_STATUS"):
        module.describe_surface()


def test_describe_surface_fails_closed_on_malformed_references(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = importlib.import_module("agent_organization.reviewer_evaluator_agents.surface")
    monkeypatch.setattr(module, "REFERENCE_MODULES", ["valid.path", ""])
    payload = module.describe_surface()
    assert payload["references"] == []

