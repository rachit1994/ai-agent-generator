from __future__ import annotations

import agent_mvp.model_adapter as model_adapter
from agent_mvp.config import DEFAULT_CONFIG
from agent_mvp.modes.guarded_pipeline import run_guarded_pipeline


def test_guarded_pipeline_planner_called_twice_and_sequential(monkeypatch) -> None:
    def _fake_invoke_model(prompt: str, model: str, provider: str, provider_base_url: str, timeout_ms: int, **_kwargs):  # type: ignore[no-untyped-def]
        if "You are the SDE planner." in prompt:
            return {"text": "# Plan\n\nEdge cases: handle empty tasks.\n", "token_input": 0, "token_output": 0, "error": None}
        if "You are the SDE planner (pass 2)." in prompt:
            return {"text": "Write only code.\n", "token_input": 0, "token_output": 0, "error": None}
        if "You are the reviewer." in prompt:
            return {"text": "{\"passed\": true, \"issues\": [], \"notes\": \"ok\"}", "token_input": 0, "token_output": 0, "error": None}
        return {"text": "from fastapi import FastAPI\n\napp = FastAPI()\n\nif __name__ == '__main__':\n    pass\n", "token_input": 0, "token_output": 0, "error": None}

    monkeypatch.setattr(model_adapter, "invoke_model", _fake_invoke_model)

    _, events = run_guarded_pipeline("r1", "t1", "FastAPI __main__", DEFAULT_CONFIG)

    stages = [e["stage"] for e in events]
    assert stages[:4] == ["planner_doc", "planner_prompt", "executor", "verifier"]
    assert "finalize" in stages[-1]
    planner_doc = next(e for e in events if e["stage"] == "planner_doc")["metadata"]["planner_doc"]
    assert isinstance(planner_doc, str) and len(planner_doc.strip()) > 0
    planner_prompt = next(e for e in events if e["stage"] == "planner_prompt")["metadata"]["executor_prompt"]
    assert isinstance(planner_prompt, str) and len(planner_prompt.strip()) > 0


def test_guarded_pipeline_fast_path_for_simple_task(monkeypatch) -> None:
    def _fake_invoke_model(prompt: str, model: str, provider: str, provider_base_url: str, timeout_ms: int, **_kwargs):  # type: ignore[no-untyped-def]
        if "You are the reviewer." in prompt:
            return {"text": "{\"passed\": true, \"issues\": [], \"notes\": \"ok\"}", "token_input": 0, "token_output": 0, "error": None}
        return {"text": "{\"answer\":\"hello\",\"checks\":[{\"name\":\"response_non_empty\",\"passed\":true}],\"refusal\":null}", "token_input": 0, "token_output": 0, "error": None}

    monkeypatch.setattr(model_adapter, "invoke_model", _fake_invoke_model)
    _, events = run_guarded_pipeline("r2", "t2", "Say hello in one sentence.", DEFAULT_CONFIG)
    planner_doc_event = next(e for e in events if e["stage"] == "planner_doc")
    planner_prompt_event = next(e for e in events if e["stage"] == "planner_prompt")
    assert planner_doc_event["metadata"]["fast_path"] is True
    assert planner_prompt_event["metadata"]["fast_path"] is True

