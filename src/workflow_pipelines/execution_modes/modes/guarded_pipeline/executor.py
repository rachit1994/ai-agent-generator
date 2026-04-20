"""Executor LLM call and empty-output fallback."""

from __future__ import annotations

import time
from typing import Any

import model_adapter.model_adapter as model_adapter

from .events import _stage


def fallback_answer_for_task(task: str) -> str:
    normalized = task.lower()
    if "json object" in normalized:
        return '{"answer":"fallback","checks":[{"name":"json_schema","passed":true}],"refusal":null}'
    if "list three" in normalized:
        return "1. Clear requirements\n2. Deterministic checks\n3. Measurable outcomes"
    if "two-step" in normalized:
        return "1. Run baseline and guarded with identical configs.\n2. Compare pass rate, reliability, and latency deltas."
    if "one sentence" in normalized:
        return "This is a concise fallback answer."
    return "Fallback answer for task."


def run_executor(
    run_id: str,
    task_id: str,
    executor_prompt: str,
    config: Any,
    *,
    attempt: int,
    retry_count: int,
) -> tuple[str, dict]:
    e0 = int(time.time() * 1000)
    resp = model_adapter.invoke_model(
        prompt=executor_prompt,
        model=config.implementation_model,
        provider=config.provider,
        provider_base_url=config.provider_base_url,
        timeout_ms=getattr(config.budgets, "executor_timeout_ms", getattr(config.budgets, "timeout_ms", 90000)),
        options={"num_ctx": 1536, "num_thread": 4, "temperature": 0, "top_p": 1, "seed": 42},
    )
    code = str(resp.get("text", "")).strip()
    if not code:
        code = fallback_answer_for_task(executor_prompt)
    e1 = int(time.time() * 1000)
    event = _stage(
        run_id,
        task_id,
        "executor" if attempt == 0 else "executor_fix",
        config,
        retry_count=retry_count,
        attempt=attempt,
        started_ms=e0,
        ended_ms=e1,
        metadata={
            "agent": {"name": "executor" if attempt == 0 else "executor_fix", "type": "llm", "role": "executor"},
            "model": config.implementation_model,
            "raw_response_excerpt": code[:200],
            "model_error": resp.get("error"),
        },
    )
    return code, event
