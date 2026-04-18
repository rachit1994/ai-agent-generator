from __future__ import annotations

import json
from pathlib import Path

import sde_pipeline.runner as runner
from sde_gates import validate_execution_run_directory


def test_execute_single_task_emits_cto_artifacts_and_passes_gates(tmp_path: Path, monkeypatch) -> None:
    def _fake_run_baseline(run_id: str, task_id: str, prompt: str, config):  # type: ignore[no-untyped-def]
        output_obj = {
            "answer": "```python\nprint('hello')\n```",
            "checks": [{"name": "ok", "passed": True}],
            "refusal": None,
        }
        event = {
            "run_id": run_id,
            "task_id": task_id,
            "mode": "baseline",
            "model": "fake",
            "provider": "fake",
            "stage": "finalize",
            "started_at": "t0",
            "ended_at": "t1",
            "latency_ms": 1,
            "token_input": 1,
            "token_output": 1,
            "estimated_cost_usd": 0,
            "retry_count": 0,
            "errors": [],
            "score": {"passed": True, "reliability": 1.0, "validity": 1.0},
            "metadata": {"agent": {"name": "baseline_executor", "type": "llm", "role": "executor"}},
        }
        return json.dumps(output_obj), [event]

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(runner, "run_baseline", _fake_run_baseline)

    result = runner.execute_single_task("ignored", "baseline")
    output_dir = Path(result["output_dir"])

    assert (output_dir / "review.json").is_file()
    assert (output_dir / "token_context.json").is_file()
    summary = json.loads((output_dir / "summary.json").read_text(encoding="utf-8"))
    assert "balanced_gates" in summary
    assert summary["quality"]["validation_ready"] is True

    gate = validate_execution_run_directory(output_dir, mode="baseline")
    assert gate["validation_ready"] is True
    assert gate["ok"] is True
    assert not gate["errors"]


def test_execute_single_task_repeat_two_isolated_runs(tmp_path: Path, monkeypatch) -> None:
    def _fake_run_baseline(run_id: str, task_id: str, prompt: str, config):  # type: ignore[no-untyped-def]
        output_obj = {
            "answer": "```python\nprint('hello')\n```",
            "checks": [{"name": "ok", "passed": True}],
            "refusal": None,
        }
        event = {
            "run_id": run_id,
            "task_id": task_id,
            "mode": "baseline",
            "model": "fake",
            "provider": "fake",
            "stage": "finalize",
            "started_at": "t0",
            "ended_at": "t1",
            "latency_ms": 1,
            "token_input": 1,
            "token_output": 1,
            "estimated_cost_usd": 0,
            "retry_count": 0,
            "errors": [],
            "score": {"passed": True, "reliability": 1.0, "validity": 1.0},
            "metadata": {"agent": {"name": "baseline_executor", "type": "llm", "role": "executor"}},
        }
        return json.dumps(output_obj), [event]

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(runner, "run_baseline", _fake_run_baseline)

    result = runner.execute_single_task("same", "baseline", repeat=2)
    assert result["repeat"] == 2
    assert result["validation_ready_all"] is True
    assert result["all_runs_no_pipeline_error"] is True
    runs = result["runs"]
    assert len(runs) == 2
    assert runs[0]["run_id"] != runs[1]["run_id"]
    assert runs[0]["output_dir"] != runs[1]["output_dir"]
