"""Phased pipeline: decompose → guarded plan/execute/review per atomic todo."""

from __future__ import annotations

import json
import time
from typing import Any

from sde_foundations.safeguards import refusal_for_unsafe, validate_task_text
from sde_foundations.types import Score, TraceEvent
from sde_foundations.utils import ms_to_iso

from sde_modes.modes.guarded_pipeline import run_guarded_pipeline
from sde_modes.modes.guarded_pipeline.verify_core import finalize_failure_reason

from .decompose import fallback_single_todo_plan, flatten_plan, run_decompose_phase, todo_prompt


def _sub_verifier_passed(sub_obj: dict[str, Any]) -> bool:
    if sub_obj.get("refusal"):
        return False
    for row in sub_obj.get("checks") or []:
        if isinstance(row, dict) and row.get("name") == "verifier_passed":
            return bool(row.get("passed"))
    return False


def _execute_todo_slices(
    flat: list[tuple[str, str, dict[str, Any]]],
    *,
    run_id: str,
    safe: str,
    config: Any,
    events: list[dict],
) -> tuple[bool, str, int]:
    combined: list[str] = []
    all_passed = True
    retry_count = 0
    for phase_id, _phase_title, todo in flat:
        sub_prompt = todo_prompt(safe, todo)
        sub_tid = str(todo.get("todo_id"))
        sub_json, sub_ev = run_guarded_pipeline(run_id, sub_tid, sub_prompt, config)
        _merge_sub_events(events, sub_ev, phase_id, sub_tid)
        try:
            sub_obj = json.loads(sub_json)
        except (json.JSONDecodeError, TypeError):
            all_passed = False
            combined.append(f"### {sub_tid}\n(sub-run output not valid JSON)\n")
            continue
        ok = _sub_verifier_passed(sub_obj)
        all_passed = all_passed and ok
        combined.append(f"### {sub_tid}\n{str(sub_obj.get('answer', '')).strip()}\n")
        for ev in reversed(sub_ev):
            if ev.get("stage") == "finalize":
                retry_count = max(retry_count, int(ev.get("retry_count") or 0))
                break
    return all_passed, "\n".join(combined), retry_count


def _merge_sub_events(parent_events: list[dict], sub_events: list[dict], phase_id: str, todo_id: str) -> None:
    for ev in sub_events:
        if ev.get("stage") == "finalize":
            continue
        meta = dict(ev.get("metadata") or {})
        phased_meta = dict(meta.get("phased") or {})
        phased_meta.update({"phase_id": phase_id, "todo_id": todo_id})
        meta["phased"] = phased_meta
        ev2 = dict(ev)
        ev2["metadata"] = meta
        parent_events.append(ev2)


def run_phased_pipeline(run_id: str, task_id: str, prompt: str, config: Any) -> tuple[str, list[dict]]:
    started_total = int(time.time() * 1000)
    safe = validate_task_text(prompt)
    events: list[dict] = []
    refusal = refusal_for_unsafe(safe)
    if refusal:
        ended = int(time.time() * 1000)
        output_obj = refusal
        refusal_ok = bool(refusal.get("refusal", {}).get("code") == "unsafe_action_refused")
        events.append(
            TraceEvent(
                run_id=run_id,
                task_id=task_id,
                mode="phased_pipeline",
                model=config.implementation_model,
                provider=config.provider,
                stage="finalize",
                started_at=ms_to_iso(started_total),
                ended_at=ms_to_iso(ended),
                latency_ms=ended - started_total,
                token_input=max(len(safe) // 4, 1),
                token_output=0,
                estimated_cost_usd=0,
                retry_count=0,
                errors=[output_obj["refusal"]["code"]] if output_obj.get("refusal") else [],
                score=Score(passed=refusal_ok, reliability=1.0 if refusal_ok else 0.0, validity=1.0),
                metadata={
                    "agent": {"name": "finalize", "type": "system", "role": "finalize"},
                    "failure_reason": finalize_failure_reason(refusal, False, ["refused"]),
                    "phased": {"skipped": True, "reason": "parent_refusal"},
                },
            ).to_dict()
        )
        return json.dumps(output_obj), events

    plan, dec_ev = run_decompose_phase(run_id, task_id, safe, config)
    events.extend(dec_ev)

    flat = flatten_plan(plan)
    if not flat:
        plan = fallback_single_todo_plan(safe)
        flat = flatten_plan(plan)

    all_passed, code, retry_count = _execute_todo_slices(flat, run_id=run_id, safe=safe, config=config, events=events)
    ended_total = int(time.time() * 1000)
    output_obj: dict[str, Any] = {
        "answer": code,
        "checks": [{"name": "verifier_passed", "passed": all_passed}],
        "refusal": None,
        "phased_plan": plan,
    }
    issues: list[str] = [] if all_passed else ["one_or_more_todos_failed_verification"]
    events.append(
        TraceEvent(
            run_id=run_id,
            task_id=task_id,
            mode="phased_pipeline",
            model=config.implementation_model,
            provider=config.provider,
            stage="finalize",
            started_at=ms_to_iso(started_total),
            ended_at=ms_to_iso(ended_total),
            latency_ms=ended_total - started_total,
            token_input=max(len(safe) // 4, 1),
            token_output=max(len(code) // 4, 0),
            estimated_cost_usd=0,
            retry_count=retry_count,
            errors=issues,
            score=Score(
                passed=all_passed,
                reliability=1.0 if all_passed else 0.0,
                validity=1.0,
            ),
            metadata={
                "agent": {"name": "finalize", "type": "system", "role": "finalize"},
                "verifier_report": {"passed": all_passed, "issues": issues, "notes": "phased_aggregate"},
                "check_pass_map": {"verifier_passed": bool(all_passed)},
                "failure_reason": finalize_failure_reason(None, all_passed, issues),
                "phased": {
                    "todo_count": len(flat),
                    "phase_count": len({p for p, _, _ in flat}),
                    "all_todos_passed": all_passed,
                },
            },
        ).to_dict()
    )
    return json.dumps(output_obj), events
