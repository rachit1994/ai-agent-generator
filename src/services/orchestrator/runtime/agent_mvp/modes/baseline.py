from __future__ import annotations

import json
import time

from agent_mvp.model_adapter import invoke_model
from agent_mvp.safeguards import refusal_for_unsafe, validate_structured_output, validate_task_text
from agent_mvp.types import Score, TraceEvent
from agent_mvp.utils import ms_to_iso


def run_baseline(run_id: str, task_id: str, prompt: str, config) -> tuple[str, list[dict]]:
    started_total_ms = int(time.time() * 1000)
    safe = validate_task_text(prompt)
    events: list[dict] = []
    refusal = refusal_for_unsafe(safe)
    raw = ""
    if refusal:
        output_obj = refusal
    else:
        started_executor_ms = int(time.time() * 1000)
        model_resp = invoke_model(
            prompt=(
                "Output ONLY a single valid JSON object (no markdown, no prose) with keys "
                '`answer` (string), `checks` (list of {name,passed}), `refusal` (null or {code,reason}).\n'
                "The JSON object you output is the ONLY JSON in your response.\n"
                "The `answer` value must be the solution text itself (for code tasks: the raw code), "
                "not another JSON object.\n"
                f"Task:\n{safe}\n"
            ),
            model=config.implementation_model,
            provider=config.provider,
            provider_base_url=config.provider_base_url,
            timeout_ms=config.budgets.timeout_ms,
        )
        raw = model_resp["text"]
        output_obj = validate_structured_output(raw)
        ended_executor_ms = int(time.time() * 1000)
        events.append(
            TraceEvent(
                run_id=run_id,
                task_id=task_id,
                mode="baseline",
                model=config.implementation_model,
                provider=config.provider,
                stage="executor",
                started_at=ms_to_iso(started_executor_ms),
                ended_at=ms_to_iso(ended_executor_ms),
                latency_ms=ended_executor_ms - started_executor_ms,
                token_input=0,
                token_output=0,
                estimated_cost_usd=0,
                retry_count=0,
                errors=[],
                score=Score(passed=True, reliability=1.0, validity=1.0),
                metadata={
                    "attempt": 0,
                    "agent": {"name": "baseline_executor", "type": "llm", "role": "executor"},
                    "raw_response_excerpt": raw[:200],
                },
            ).to_dict()
        )
        passed = all(c.get("passed") for c in output_obj["checks"])
        retry_count = 0
        if not passed and retry_count < config.budgets.max_retries:
            retry_count = 1
            started_repair_ms = int(time.time() * 1000)
            repair_resp = invoke_model(
                prompt=(
                    "Repair your previous response.\n"
                    "Output ONLY a single valid JSON object (no markdown, no prose) with keys "
                    '`answer` (string), `checks` (list of {name,passed}), `refusal` (null or {code,reason}).\n'
                    "The JSON object you output is the ONLY JSON in your response.\n"
                    "The `answer` value must be the solution text itself (for code tasks: the raw code), "
                    "not another JSON object.\n\n"
                    f"Task:\n{safe}\n"
                ),
                model=config.implementation_model,
                provider=config.provider,
                provider_base_url=config.provider_base_url,
                timeout_ms=config.budgets.timeout_ms,
            )
            repaired_raw = repair_resp["text"]
            output_obj = validate_structured_output(repaired_raw)
            ended_repair_ms = int(time.time() * 1000)
            events.append(
                TraceEvent(
                    run_id=run_id,
                    task_id=task_id,
                    mode="baseline",
                    model=config.implementation_model,
                    provider=config.provider,
                    stage="repair",
                    started_at=ms_to_iso(started_repair_ms),
                    ended_at=ms_to_iso(ended_repair_ms),
                    latency_ms=ended_repair_ms - started_repair_ms,
                    token_input=0,
                    token_output=0,
                    estimated_cost_usd=0,
                    retry_count=retry_count,
                    errors=["repair_failed"] if not all(c.get("passed") for c in output_obj["checks"]) else [],
                    score=Score(passed=True, reliability=1.0, validity=1.0),
                    metadata={
                        "attempt": 1,
                        "agent": {"name": "baseline_repairer", "type": "llm", "role": "repair"},
                        "raw_response_excerpt": repaired_raw[:200],
                    },
                ).to_dict()
            )
    ended_total_ms = int(time.time() * 1000)
    checks = output_obj["checks"]
    passed_count = sum(1 for c in checks if c.get("passed"))
    event = TraceEvent(
        run_id=run_id,
        task_id=task_id,
        mode="baseline",
        model=config.implementation_model,
        provider=config.provider,
        stage="finalize",
        started_at=ms_to_iso(started_total_ms),
        ended_at=ms_to_iso(ended_total_ms),
        latency_ms=ended_total_ms - started_total_ms,
        token_input=max(len(safe) // 4, 1),
        token_output=max(len(output_obj["answer"]) // 4, 0),
        estimated_cost_usd=0,
        retry_count=max((e.get("retry_count", 0) for e in events), default=0),
        errors=[output_obj["refusal"]["code"]] if output_obj.get("refusal") else [],
        score=Score(
            passed=all(c.get("passed") for c in checks),
            reliability=passed_count / max(len(checks), 1),
            validity=1,
        ),
        metadata={
            "agent": {"name": "baseline_finalizer", "type": "system", "role": "finalize"},
            "raw_response_excerpt": raw[:200],
        },
    )
    events.append(event.to_dict())
    return json.dumps(output_obj), events
