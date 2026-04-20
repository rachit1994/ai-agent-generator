from __future__ import annotations

import json
from pathlib import Path

import workflow_pipelines.production_pipeline_task_to_promote.runner as runner


def test_execute_single_task_writes_artifacts(tmp_path: Path, monkeypatch) -> None:
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

    result = runner.execute_single_task(
        "ignored",
        "baseline",
        project_step_id="alpha",
        project_session_dir=str(tmp_path / "sess"),
    )
    output_dir = Path(result["output_dir"])

    assert (output_dir / "answer.txt").exists()
    assert (output_dir / "generated_script.py").exists()
    assert (output_dir / "orchestration.jsonl").exists()
    assert (output_dir / "run.log").exists()
    manifest = json.loads((output_dir / "run-manifest.json").read_text(encoding="utf-8"))
    assert manifest["schema"] == "sde.run_manifest.v1"
    assert manifest["mode"] == "baseline"
    assert manifest["task"] == "ignored"
    assert manifest["project_step_id"] == "alpha"
    assert manifest["project_session_dir"] == str(tmp_path / "sess")

