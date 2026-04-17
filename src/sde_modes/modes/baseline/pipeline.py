"""Baseline mode: single executor pass, optional repair, finalize trace."""

from __future__ import annotations

import json
from typing import Any

from sde_foundations.safeguards import classify_output_failure, refusal_for_unsafe, validate_structured_output, validate_task_text
from sde_foundations.types import Score, TraceEvent
from sde_foundations.utils import ms_to_iso

from .prompts import baseline_executor_prompt, baseline_repair_prompt


def run_baseline(run_id: str, task_id: str, prompt: str, config: Any) -> tuple[str, list[dict]]:
    from sde_modes.modes import baseline as bl_pkg

    invoke_model = bl_pkg.invoke_model
    _now = bl_pkg.time.time

    started_total_ms = int(_now() * 1000)
    safe = validate_task_text(prompt)
    events: list[dict] = []
    refusal = refusal_for_unsafe(safe)
    raw = ""
    if refusal:
        output_obj = refusal
    else:
        started_executor_ms = int(_now() * 1000)
        timeout_ms = getattr(config.budgets, "executor_timeout_ms", getattr(config.budgets, "timeout_ms", 90000))
        model_resp = invoke_model(
            prompt=baseline_executor_prompt(safe),
            model=config.implementation_model,
            provider=config.provider,
            provider_base_url=config.provider_base_url,
            timeout_ms=timeout_ms,
            options={"temperature": 0, "top_p": 1, "seed": 42},
        )
        raw = model_resp["text"]
        output_obj = validate_structured_output(raw)
        ended_executor_ms = int(_now() * 1000)
        executor_errors: list[str] = []
        model_error = model_resp.get("error")
        if isinstance(model_error, str) and model_error:
            executor_errors.append("pipeline_timeout" if "timeout" in model_error.lower() else "evaluator_error")
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
                errors=executor_errors,
                score=Score(passed=True, reliability=1.0, validity=1.0),
                metadata={
                    "attempt": 0,
                    "agent": {"name": "baseline_executor", "type": "llm", "role": "executor"},
                    "raw_response_excerpt": raw[:200],
                    "model_error": model_error,
                },
            ).to_dict()
        )
        passed = all(c.get("passed") for c in output_obj["checks"])
        retry_count = 0
        if not passed and retry_count < config.budgets.max_retries:
            retry_count = 1
            started_repair_ms = int(_now() * 1000)
            repair_resp = invoke_model(
                prompt=baseline_repair_prompt(safe),
                model=config.implementation_model,
                provider=config.provider,
                provider_base_url=config.provider_base_url,
                timeout_ms=timeout_ms,
                options={"temperature": 0, "top_p": 1, "seed": 42},
            )
            repaired_raw = repair_resp["text"]
            output_obj = validate_structured_output(repaired_raw)
            ended_repair_ms = int(_now() * 1000)
            repair_errors: list[str] = []
            repair_model_error = repair_resp.get("error")
            if isinstance(repair_model_error, str) and repair_model_error:
                repair_errors.append("pipeline_timeout" if "timeout" in repair_model_error.lower() else "evaluator_error")
            if not all(c.get("passed") for c in output_obj["checks"]):
                repair_errors.append("quality_check_fail")
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
                    errors=repair_errors,
                    score=Score(passed=True, reliability=1.0, validity=1.0),
                    metadata={
                        "attempt": 1,
                        "agent": {"name": "baseline_repairer", "type": "llm", "role": "repair"},
                        "raw_response_excerpt": repaired_raw[:200],
                        "model_error": repair_model_error,
                    },
                ).to_dict()
            )
    ended_total_ms = int(_now() * 1000)
    checks = output_obj["checks"]
    passed_count = sum(1 for c in checks if c.get("passed"))
    check_pass_map = {str(c.get("name", "unknown")): bool(c.get("passed")) for c in checks if isinstance(c, dict)}
    failure_reason = classify_output_failure(output_obj)
    if failure_reason == "none":
        failure_reason = "none" if all(c.get("passed") for c in checks) else "quality_check_fail"
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
            "check_pass_map": check_pass_map,
            "failure_reason": failure_reason,
        },
    )
    events.append(event.to_dict())
    return json.dumps(output_obj), events
