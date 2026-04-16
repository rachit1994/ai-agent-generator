from __future__ import annotations

import json
import time

from agent_mvp.model_adapter import invoke_model
from agent_mvp.safeguards import refusal_for_unsafe, validate_structured_output, validate_task_text
from agent_mvp.types import Score, TraceEvent
from agent_mvp.utils import now_iso


def _stage(run_id: str, task_id: str, stage: str, config, retry_count: int, passed: bool = True) -> dict:
    event = TraceEvent(
        run_id=run_id,
        task_id=task_id,
        mode="guarded_pipeline",
        model=config.implementation_model,
        provider=config.provider,
        stage=stage,
        started_at=now_iso(),
        ended_at=now_iso(),
        latency_ms=0,
        token_input=0,
        token_output=0,
        estimated_cost_usd=0,
        retry_count=retry_count,
        errors=[],
        score=Score(passed=passed, reliability=1.0 if passed else 0.0, validity=1.0),
    )
    return event.to_dict()


def run_guarded(run_id: str, task_id: str, prompt: str, config) -> tuple[str, list[dict]]:
    started_total = int(time.time() * 1000)
    safe = validate_task_text(prompt)
    events: list[dict] = []
    refusal = refusal_for_unsafe(safe)
    plan = "unsafe" if refusal else "1) plan solution 2) execute 3) verify"
    events.append(_stage(run_id, task_id, "planner", config, 0))
    if refusal:
        structured = refusal
    else:
        raw = invoke_model(
            prompt=f"Plan:\n{plan}\nTask:{safe}\nReturn JSON {{answer,checks,refusal}}.",
            model=config.implementation_model,
            provider=config.provider,
            provider_base_url=config.provider_base_url,
            timeout_ms=config.budgets.timeout_ms,
        )["text"]
        structured = validate_structured_output(raw)
    events.append(_stage(run_id, task_id, "executor", config, 0))
    passed = all(c.get("passed") for c in structured["checks"])
    events.append(_stage(run_id, task_id, "verifier", config, 0, passed))
    retry_count = 0
    if not passed and retry_count < config.budgets.max_retries:
        retry_count = 1
        repaired_raw = invoke_model(
            prompt=f"Repair previous invalid output. Return strict JSON {{answer,checks,refusal}} for task: {safe}",
            model=config.implementation_model,
            provider=config.provider,
            provider_base_url=config.provider_base_url,
            timeout_ms=config.budgets.timeout_ms,
        )["text"]
        structured = validate_structured_output(repaired_raw)
        passed = all(c.get("passed") for c in structured["checks"])
        events.append(_stage(run_id, task_id, "repair", config, retry_count, passed))
    ended_total = int(time.time() * 1000)
    checks = structured["checks"]
    passed_count = sum(1 for c in checks if c.get("passed"))
    final = TraceEvent(
        run_id=run_id,
        task_id=task_id,
        mode="guarded_pipeline",
        model=config.implementation_model,
        provider=config.provider,
        stage="finalize",
        started_at=now_iso(),
        ended_at=now_iso(),
        latency_ms=ended_total - started_total,
        token_input=max(len(safe) // 4, 1),
        token_output=max(len(structured["answer"]) // 4, 0),
        estimated_cost_usd=0,
        retry_count=retry_count,
        errors=[structured["refusal"]["code"]] if structured.get("refusal") else [],
        score=Score(passed=passed, reliability=passed_count / max(len(checks), 1), validity=1),
        metadata={"checks": checks, "refusal": structured.get("refusal")},
    )
    events.append(final.to_dict())
    return json.dumps(structured), events
