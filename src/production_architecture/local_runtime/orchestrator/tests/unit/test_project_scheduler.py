from __future__ import annotations

from orchestrator.api.project_scheduler import select_steps_for_tick


def _plan_with_scopes(scope_a: object, scope_b: object) -> dict[str, object]:
    return {
        "schema_version": "1.0",
        "steps": [
            {
                "step_id": "a",
                "depends_on": [],
                "path_scope": scope_a,
            },
            {
                "step_id": "b",
                "depends_on": [],
                "path_scope": scope_b,
            },
        ],
    }


def test_select_steps_for_tick_fails_closed_on_non_int_concurrency() -> None:
    plan = _plan_with_scopes(["src/**"], ["docs/**"])
    assert select_steps_for_tick(plan, set(), max_concurrent_agents=True) == []
    assert select_steps_for_tick(plan, set(), max_concurrent_agents=1) == ["a"]


def test_select_steps_for_tick_treats_malformed_path_scope_as_conflicting() -> None:
    malformed = _plan_with_scopes("src/**", ["docs/**"])
    assert select_steps_for_tick(malformed, set(), max_concurrent_agents=2) == ["a"]

    malformed_items = _plan_with_scopes(["src/**", ""], ["docs/**"])
    assert select_steps_for_tick(malformed_items, set(), max_concurrent_agents=2) == ["a"]
