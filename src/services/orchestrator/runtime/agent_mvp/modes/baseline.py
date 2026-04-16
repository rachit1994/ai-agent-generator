from __future__ import annotations

import json
import time

from agent_mvp.model_adapter import invoke_model
from agent_mvp.safeguards import refusal_for_unsafe, validate_structured_output, validate_task_text
from agent_mvp.types import Score, TraceEvent
from agent_mvp.utils import now_iso


def run_baseline(run_id: str, task_id: str, prompt: str, config) -> tuple[str, list[dict]]:
    started = int(time.time() * 1000)
    safe = validate_task_text(prompt)
    refusal = refusal_for_unsafe(safe)
    if refusal:
        output_obj = refusal
    else:
        raw = invoke_model(
            prompt=f"Return JSON {{answer,checks,refusal}}. Task: {safe}",
            model=config.implementation_model,
            provider=config.provider,
            provider_base_url=config.provider_base_url,
            timeout_ms=config.budgets.timeout_ms,
        )["text"]
        output_obj = validate_structured_output(raw)
    ended = int(time.time() * 1000)
    checks = output_obj["checks"]
    passed_count = sum(1 for c in checks if c.get("passed"))
    event = TraceEvent(
        run_id=run_id,
        task_id=task_id,
        mode="baseline",
        model=config.implementation_model,
        provider=config.provider,
        stage="finalize",
        started_at=now_iso(),
        ended_at=now_iso(),
        latency_ms=ended - started,
        token_input=max(len(safe) // 4, 1),
        token_output=max(len(output_obj["answer"]) // 4, 0),
        estimated_cost_usd=0,
        retry_count=0,
        errors=[output_obj["refusal"]["code"]] if output_obj.get("refusal") else [],
        score=Score(
            passed=all(c.get("passed") for c in checks),
            reliability=passed_count / max(len(checks), 1),
            validity=1,
        ),
    )
    return json.dumps(output_obj), [event.to_dict()]
