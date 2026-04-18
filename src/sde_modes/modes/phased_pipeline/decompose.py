"""LLM-backed decomposition of a large task into phased atomic todos."""

from __future__ import annotations

import json
import re
import time
from typing import Any

import sde_foundations.model_adapter as model_adapter

from sde_modes.modes.guarded_pipeline import simple
from sde_modes.modes.guarded_pipeline.events import _stage

from . import prompts


def fallback_single_todo_plan(goal: str) -> dict[str, Any]:
    """Public fallback when LLM decomposition is unusable."""
    return _deterministic_plan(goal)


def _deterministic_plan(goal: str) -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "phases": [
            {
                "phase_id": "phase_0",
                "title": "Execution",
                "todos": [
                    {
                        "todo_id": "todo_0",
                        "title": goal,
                        "acceptance_criteria": "Original goal satisfied; output matches task constraints.",
                    }
                ],
            }
        ],
    }


def _validate_todo_row(t: Any) -> bool:
    return isinstance(t, dict) and bool(t.get("todo_id")) and bool(t.get("title"))


def _validate_phase_row(ph: Any) -> bool:
    if not isinstance(ph, dict) or not ph.get("phase_id") or not ph.get("title"):
        return False
    todos = ph.get("todos")
    if not isinstance(todos, list) or len(todos) == 0:
        return False
    return all(_validate_todo_row(t) for t in todos)


def _validate_plan(plan: Any) -> bool:
    if not isinstance(plan, dict) or plan.get("schema_version") != "1.0":
        return False
    phases = plan.get("phases")
    if not isinstance(phases, list) or len(phases) == 0:
        return False
    return all(_validate_phase_row(ph) for ph in phases)


def _parse_plan_text(text: str) -> dict[str, Any]:
    stripped = text.strip()
    if stripped.startswith("```"):
        m = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", stripped, flags=re.IGNORECASE)
        if m:
            stripped = m.group(1).strip()
    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        start = stripped.find("{")
        end = stripped.rfind("}")
        if start >= 0 and end > start:
            return json.loads(stripped[start : end + 1])
    raise ValueError("plan_not_json")


def flatten_plan(plan: dict[str, Any]) -> list[tuple[str, str, dict[str, Any]]]:
    """Return list of (phase_id, phase_title, todo_dict)."""
    out: list[tuple[str, str, dict[str, Any]]] = []
    for ph in plan.get("phases") or []:
        if not isinstance(ph, dict):
            continue
        pid = str(ph.get("phase_id", ""))
        ptitle = str(ph.get("title", ""))
        for t in ph.get("todos") or []:
            if isinstance(t, dict):
                out.append((pid, ptitle, t))
    return out


def run_decompose_phase(
    run_id: str,
    task_id: str,
    goal: str,
    config: Any,
) -> tuple[dict[str, Any], list[dict]]:
    events: list[dict] = []
    if simple.is_simple_task(goal):
        plan = _deterministic_plan(goal)
        events.append(
            _stage(
                run_id,
                task_id,
                "phased_decompose",
                config,
                retry_count=0,
                attempt=0,
                passed=True,
                metadata={
                    "agent": {"name": "phased_decompose", "type": "system", "role": "planner"},
                    "phased_plan": plan,
                    "fast_path": True,
                },
            )
        )
        return plan, events

    support_model = getattr(config, "support_model", getattr(config, "implementation_model", ""))
    t0 = int(time.time() * 1000)
    resp = model_adapter.invoke_model(
        prompt=prompts.phased_decompose_prompt(goal),
        model=support_model,
        provider=config.provider,
        provider_base_url=config.provider_base_url,
        timeout_ms=getattr(config.budgets, "planner_timeout_ms", getattr(config.budgets, "timeout_ms", 30000)),
        options={"num_predict": 512, "num_ctx": 1024, "num_thread": 2, "temperature": 0, "top_p": 1, "seed": 43},
        keep_alive="60s",
    )
    raw = str(resp.get("text", "")).strip()
    t1 = int(time.time() * 1000)
    plan: dict[str, Any]
    parse_ok = True
    try:
        candidate = _parse_plan_text(raw)
        plan = candidate if _validate_plan(candidate) else _deterministic_plan(goal)
        parse_ok = _validate_plan(candidate)
    except (TypeError, ValueError):
        plan = _deterministic_plan(goal)
        parse_ok = False

    events.append(
        _stage(
            run_id,
            task_id,
            "phased_decompose",
            config,
            retry_count=0,
            attempt=0,
            started_ms=t0,
            ended_ms=t1,
            passed=parse_ok,
            errors=[] if parse_ok else ["phased_plan_parse_or_schema_failed"],
            metadata={
                "agent": {"name": "phased_decompose", "type": "llm", "role": "planner"},
                "phased_plan": plan,
                "model": support_model,
                "model_error": resp.get("error"),
                "raw_response_excerpt": raw[:400],
            },
        )
    )
    return plan, events


def todo_prompt(goal: str, todo: dict[str, Any]) -> str:
    crit = str(todo.get("acceptance_criteria") or "").strip()
    return (
        "## Overall goal\n"
        f"{goal}\n\n"
        "## Current atomic todo\n"
        f"**{todo.get('todo_id')}** — {todo.get('title')}\n\n"
        "## Acceptance criteria\n"
        f"{crit if crit else 'Complete the todo scope; keep changes minimal and testable.'}\n"
    )
