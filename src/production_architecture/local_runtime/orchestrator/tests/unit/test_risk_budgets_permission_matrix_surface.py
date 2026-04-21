from __future__ import annotations

from guardrails_and_safety.risk_budgets_permission_matrix.surface import describe_surface


def test_describe_surface_returns_expected_shape() -> None:
    payload = describe_surface()
    assert payload["subheading"] == "guardrails_and_safety/risk_budgets_permission_matrix"
    assert payload["status"] == "implemented"
    refs = payload["references"]
    assert isinstance(refs, list)
    assert "guardrails_and_safety.risk_budgets_permission_matrix.runtime" in refs
