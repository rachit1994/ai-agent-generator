from __future__ import annotations

import json
from pathlib import Path

import pytest

import workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner as runner
from guardrails_and_safety import validate_execution_run_directory


def _event(
    run_id: str,
    task_id: str,
    *,
    stage: str,
    passed: bool = True,
    metadata: dict | None = None,
) -> dict:
    return {
        "run_id": run_id,
        "task_id": task_id,
        "mode": "guarded_pipeline",
        "model": "fake",
        "provider": "fake",
        "stage": stage,
        "started_at": "t0",
        "ended_at": "t1",
        "latency_ms": 1,
        "token_input": 1,
        "token_output": 1,
        "estimated_cost_usd": 0,
        "retry_count": 0,
        "errors": [],
        "score": {"passed": passed, "reliability": 1.0 if passed else 0.0, "validity": 1.0},
        "metadata": metadata or {},
    }


def test_guarded_pipeline_writes_completion_harness_and_passes_extended_gates(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def _fake_run_guarded(run_id: str, task_id: str, prompt: str, config):  # type: ignore[no-untyped-def]
        output_obj = {
            "answer": "```python\nprint('guarded')\n```",
            "checks": [{"name": "verifier_passed", "passed": True}],
            "refusal": None,
        }
        events = [
            _event(
                run_id,
                task_id,
                stage="planner_doc",
                metadata={"planner_doc": "# Plan\nDo the thing."},
            ),
            _event(
                run_id,
                task_id,
                stage="executor",
                metadata={"executor_prompt": "Implement minimal hello."},
            ),
            _event(
                run_id,
                task_id,
                stage="finalize",
                metadata={"verifier_report": {"passed": True, "issues": []}},
            ),
        ]
        return json.dumps(output_obj), events

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(runner, "run_guarded", _fake_run_guarded)

    result = runner.execute_single_task("task text", "guarded_pipeline")
    output_dir = Path(result["output_dir"])

    assert (output_dir / "program" / "project_plan.json").is_file()
    assert (output_dir / "program" / "research_digest.md").is_file()
    assert (output_dir / "product_brief.md").is_file()
    assert (output_dir / "architecture_sketch.md").is_file()
    assert (output_dir / "test_plan_stub.md").is_file()
    assert (output_dir / "program" / "plan_lock.json").is_file()
    disc = json.loads((output_dir / "program" / "discovery.json").read_text(encoding="utf-8"))
    assert disc.get("goal_excerpt") == "task text"
    assert disc.get("non_goals") == []
    assert "task excerpt" in (output_dir / "program" / "research_digest.md").read_text(encoding="utf-8").lower()
    assert "Product brief" in (output_dir / "product_brief.md").read_text(encoding="utf-8")
    assert (output_dir / "step_reviews" / "step_verify.json").is_file()
    assert (output_dir / "verification_bundle.json").is_file()
    review = json.loads((output_dir / "review.json").read_text(encoding="utf-8"))
    assert "definition_of_done" in review

    gate = validate_execution_run_directory(output_dir, mode="guarded_pipeline")
    assert gate["validation_ready"] is True
    assert gate["ok"] is True
    hs_ids = [h["id"] for h in gate["hard_stops"]]
    assert hs_ids == [f"HS{i:02d}" for i in range(1, 33)]
    assert all(h["passed"] for h in gate["hard_stops"])
