from __future__ import annotations

import json

import pytest

from workflow_pipelines.strategy_overlay.execution_modes.modes.phased_pipeline import run_phased_pipeline
from workflow_pipelines.strategy_overlay.execution_modes.modes.phased_pipeline.decompose import flatten_plan, fallback_single_todo_plan
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.config import DEFAULT_CONFIG


def test_flatten_plan_orders_todos() -> None:
    plan = {
        "schema_version": "1.0",
        "phases": [
            {
                "phase_id": "p1",
                "title": "One",
                "todos": [{"todo_id": "a", "title": "ta", "acceptance_criteria": ""}],
            },
            {
                "phase_id": "p2",
                "title": "Two",
                "todos": [{"todo_id": "b", "title": "tb", "acceptance_criteria": "done"}],
            },
        ],
    }
    flat = flatten_plan(plan)
    assert [t[2]["todo_id"] for t in flat] == ["a", "b"]


def test_run_phased_pipeline_runs_guarded_per_todo(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[str] = []

    def _fake_decompose(
        run_id: str,
        task_id: str,
        goal: str,
        config,
    ) -> tuple[dict, list[dict]]:
        plan = {
            "schema_version": "1.0",
            "phases": [
                {
                    "phase_id": "p1",
                    "title": "Phase",
                    "todos": [
                        {"todo_id": "t1", "title": "First slice", "acceptance_criteria": "A"},
                        {"todo_id": "t2", "title": "Second slice", "acceptance_criteria": "B"},
                    ],
                }
            ],
        }
        ev = [
            {
                "run_id": run_id,
                "task_id": task_id,
                "stage": "phased_decompose",
                "metadata": {"phased_plan": plan},
            }
        ]
        return plan, ev

    def _fake_guarded(run_id: str, task_id: str, prompt: str, config) -> tuple[str, list[dict]]:
        calls.append(task_id)
        assert "Overall goal" in prompt
        assert "Current atomic todo" in prompt
        events = [
            {
                "run_id": run_id,
                "task_id": task_id,
                "mode": "guarded_pipeline",
                "stage": "planner_doc",
                "metadata": {"planner_doc": f"# {task_id}"},
            },
            {
                "run_id": run_id,
                "task_id": task_id,
                "mode": "guarded_pipeline",
                "stage": "finalize",
                "score": {"passed": True},
            },
        ]
        payload = {
            "answer": f"ok-{task_id}",
            "checks": [{"name": "verifier_passed", "passed": True}],
            "refusal": None,
        }
        return json.dumps(payload), events

    monkeypatch.setattr(
        "workflow_pipelines.strategy_overlay.execution_modes.modes.phased_pipeline.pipeline.run_decompose_phase",
        _fake_decompose,
    )
    monkeypatch.setattr(
        "workflow_pipelines.strategy_overlay.execution_modes.modes.phased_pipeline.pipeline.run_guarded_pipeline",
        _fake_guarded,
    )

    out, events = run_phased_pipeline("r1", "root", "Build a multi-step feature with API and tests", DEFAULT_CONFIG)
    assert calls == ["t1", "t2"]
    body = json.loads(out)
    assert body["checks"][0]["passed"] is True
    assert "t1" in body["answer"] and "t2" in body["answer"]
    assert body.get("phased_plan", {}).get("schema_version") == "1.0"
    assert sum(1 for e in events if e.get("stage") == "finalize") == 1
    assert any(e.get("stage") == "phased_decompose" for e in events)


def test_fallback_single_todo_plan() -> None:
    p = fallback_single_todo_plan("just do X")
    assert flatten_plan(p)[0][2]["title"] == "just do X"
