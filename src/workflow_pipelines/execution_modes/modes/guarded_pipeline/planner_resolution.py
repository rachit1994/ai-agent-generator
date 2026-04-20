"""Resolve planner doc + executor prompt for refusal, fast-path, or full planner."""

from __future__ import annotations

from typing import Any

from . import planner as planner_mod
from . import simple
from .events import _stage


def resolve_planner_phase(
    run_id: str,
    task_id: str,
    safe: str,
    config: Any,
    refusal: dict | None,
) -> tuple[str, str, list[dict]]:
    events: list[dict] = []
    planner_doc = ""
    planner_exec_prompt = ""
    if refusal:
        planner_doc = f"# Refused\n\nReason: {refusal['refusal']['reason']}\n"
        return planner_doc, planner_exec_prompt, events
    if simple.is_simple_task(safe):
        planner_doc = "# FastPath\n\nSimple task detected; planner stages skipped."
        planner_exec_prompt = simple.simple_executor_prompt(safe)
        events.append(
            _stage(
                run_id,
                task_id,
                "planner_doc",
                config,
                retry_count=0,
                attempt=0,
                passed=True,
                metadata={
                    "agent": {"name": "planner_doc_fast_path", "type": "system", "role": "planner"},
                    "planner_doc": planner_doc,
                    "fast_path": True,
                },
            )
        )
        events.append(
            _stage(
                run_id,
                task_id,
                "planner_prompt",
                config,
                retry_count=0,
                attempt=1,
                passed=True,
                metadata={
                    "agent": {"name": "planner_prompt_fast_path", "type": "system", "role": "planner"},
                    "executor_prompt": planner_exec_prompt,
                    "fast_path": True,
                },
            )
        )
        return planner_doc, planner_exec_prompt, events
    doc, prompt, ev = planner_mod.run_planner(run_id, task_id, safe, config)
    events.extend(ev)
    return doc, prompt, events
