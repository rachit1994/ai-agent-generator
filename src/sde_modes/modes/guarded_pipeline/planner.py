"""Two-stage planner: Markdown plan then executor-bound prompt."""

from __future__ import annotations

import time
from typing import Any

import sde_foundations.model_adapter as model_adapter

from . import deterministic
from . import prompts
from .events import _stage


def run_planner(run_id: str, task_id: str, safe: str, config: Any) -> tuple[str, str, list[dict]]:
    events: list[dict] = []
    support_model = getattr(config, "support_model", getattr(config, "implementation_model", ""))
    t0 = int(time.time() * 1000)
    planner_resp = model_adapter.invoke_model(
        prompt=prompts.planner_doc_prompt(safe),
        model=support_model,
        provider=config.provider,
        provider_base_url=config.provider_base_url,
        timeout_ms=getattr(config.budgets, "planner_timeout_ms", getattr(config.budgets, "timeout_ms", 30000)),
        options={"num_predict": 256, "num_ctx": 512, "num_thread": 2, "temperature": 0, "top_p": 1, "seed": 42},
        keep_alive="60s",
    )
    planner_doc = str(planner_resp.get("text", "")).strip()
    if not planner_doc:
        planner_doc = deterministic.deterministic_planner_doc(safe).strip()
    planner_doc_excerpt = str(planner_resp.get("text", "")).strip()[:200]
    if not planner_doc_excerpt:
        planner_doc_excerpt = planner_doc[:200]
    t1 = int(time.time() * 1000)
    events.append(
        _stage(
            run_id,
            task_id,
            "planner_doc",
            config,
            retry_count=0,
            attempt=0,
            started_ms=t0,
            ended_ms=t1,
            metadata={
                "agent": {"name": "planner_doc", "type": "llm", "role": "planner"},
                "planner_doc": planner_doc,
                "model": support_model,
                "model_error": planner_resp.get("error"),
                "raw_response_excerpt": planner_doc_excerpt,
            },
        )
    )
    t2 = int(time.time() * 1000)
    prompt_resp = model_adapter.invoke_model(
        prompt=prompts.planner_executor_prompt(safe, planner_doc),
        model=support_model,
        provider=config.provider,
        provider_base_url=config.provider_base_url,
        timeout_ms=getattr(config.budgets, "planner_timeout_ms", getattr(config.budgets, "timeout_ms", 30000)),
        options={"num_predict": 256, "num_ctx": 512, "num_thread": 2, "temperature": 0, "top_p": 1, "seed": 42},
        keep_alive="60s",
    )
    planner_exec_prompt = str(prompt_resp.get("text", "")).strip()
    if not planner_exec_prompt:
        planner_exec_prompt = deterministic.deterministic_executor_prompt(safe, planner_doc).strip()
    prompt_excerpt = str(prompt_resp.get("text", "")).strip()[:200]
    if not prompt_excerpt:
        prompt_excerpt = planner_exec_prompt[:200]
    t3 = int(time.time() * 1000)
    events.append(
        _stage(
            run_id,
            task_id,
            "planner_prompt",
            config,
            retry_count=0,
            attempt=1,
            started_ms=t2,
            ended_ms=t3,
            metadata={
                "agent": {"name": "planner_prompt", "type": "llm", "role": "planner"},
                "executor_prompt": planner_exec_prompt,
                "model": support_model,
                "model_error": prompt_resp.get("error"),
                "raw_response_excerpt": prompt_excerpt,
            },
        )
    )
    return planner_doc, planner_exec_prompt, events
