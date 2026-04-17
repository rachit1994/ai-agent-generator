"""End-to-end guarded pipeline: refusal, planner, executor, verifier, finalize."""

from __future__ import annotations

import json
import time
from typing import Any

from sde_foundations.safeguards import refusal_for_unsafe, validate_task_text
from sde_foundations.types import Score, TraceEvent
from sde_foundations.utils import ms_to_iso

from .events import _skipped_stage
from .executor import run_executor
from .planner_resolution import resolve_planner_phase
from .verify_core import finalize_failure_reason
from .verify_pass import run_fix_retry_if_configured, run_initial_verification


def run_guarded_pipeline(run_id: str, task_id: str, prompt: str, config: Any) -> tuple[str, list[dict]]:
    started_total = int(time.time() * 1000)
    safe = validate_task_text(prompt)
    events: list[dict] = []
    refusal = refusal_for_unsafe(safe)
    planner_doc, planner_exec_prompt, planner_events = resolve_planner_phase(run_id, task_id, safe, config, refusal)
    events.extend(planner_events)

    code = ""
    if refusal:
        events.append(_skipped_stage(run_id, task_id, "executor", config, agent_name="executor"))
    else:
        code, event = run_executor(run_id, task_id, planner_exec_prompt, config, attempt=0, retry_count=0)
        events.append(event)

    passed, issues, report = run_initial_verification(
        run_id, task_id, safe, planner_doc, code, refusal, config, events
    )
    retry_count, code, passed, issues, report = run_fix_retry_if_configured(
        run_id, task_id, safe, planner_doc, code, refusal, passed, issues, report, config, events
    )

    ended_total = int(time.time() * 1000)
    output_obj = (
        refusal
        if refusal
        else {
            "answer": code,
            "checks": [{"name": "verifier_passed", "passed": passed}],
            "refusal": None,
        }
    )
    refusal_ok = bool(refusal) and refusal.get("refusal", {}).get("code") == "unsafe_action_refused"
    events.append(
        TraceEvent(
            run_id=run_id,
            task_id=task_id,
            mode="guarded_pipeline",
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
            errors=[output_obj["refusal"]["code"]] if output_obj.get("refusal") else [],
            score=Score(
                passed=refusal_ok or (passed and not bool(refusal)),
                reliability=1.0 if (refusal_ok or passed) else 0.0,
                validity=1.0,
            ),
            metadata={
                "agent": {"name": "finalize", "type": "system", "role": "finalize"},
                "planner_doc": planner_doc,
                "executor_prompt": planner_exec_prompt,
                "verifier_report": report,
                "check_pass_map": {"verifier_passed": bool(passed)},
                "failure_reason": finalize_failure_reason(refusal, passed, issues),
            },
        ).to_dict()
    )
    return json.dumps(output_obj), events
