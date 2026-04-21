from __future__ import annotations

import json
import importlib
from pathlib import Path

import workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner as runner

_single_task_module = importlib.import_module(
    "workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.single_task"
)


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
    monkeypatch.setenv("PA_STORAGE_BACKEND_MODE", "artifact_compat")
    monkeypatch.setattr(
        _single_task_module,
        "write_online_evaluation_shadow_canary_artifact",
        lambda output_dir, run_id: {"run_id": run_id},
    )
    monkeypatch.setattr(
        _single_task_module,
        "validate_execution_run_directory",
        lambda output_dir, mode: {"ok": True, "validation_ready": True, "errors": []},
    )

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


def test_execute_single_task_aborts_when_autonomy_contract_validation_fails(
    tmp_path: Path, monkeypatch
) -> None:
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
    monkeypatch.setenv("PA_STORAGE_BACKEND_MODE", "artifact_compat")
    monkeypatch.setattr(
        _single_task_module,
        "write_online_evaluation_shadow_canary_artifact",
        lambda output_dir, run_id: {"run_id": run_id},
    )
    monkeypatch.setattr(
        _single_task_module,
        "validate_execution_run_directory",
        lambda output_dir, mode: {
            "ok": False,
            "validation_ready": False,
            "errors": ["autonomy_boundaries_contract:autonomy_boundaries_schema"],
        },
    )

    try:
        runner.execute_single_task("ignored", "baseline")
    except ValueError as exc:
        message = str(exc)
    else:
        assert False, "expected ValueError"

    assert "run_directory_validation_failed:" in message
    assert "autonomy_boundaries_contract:autonomy_boundaries_schema" in message

