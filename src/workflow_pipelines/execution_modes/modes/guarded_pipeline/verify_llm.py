"""LLM-backed verifier with heuristic fallback on parse errors."""

from __future__ import annotations

import time
from typing import Any

import model_adapter.model_adapter as model_adapter

from .events import _stage
from .verify_core import extract_json_object, heuristic_verify


def llm_verify(
    run_id: str,
    task_id: str,
    task: str,
    planning_doc: str,
    code: str,
    config: Any,
) -> tuple[bool, list[str], dict, dict]:
    v0 = int(time.time() * 1000)
    support_model = getattr(config, "support_model", getattr(config, "implementation_model", ""))
    planning_doc_short = planning_doc.strip()[:1200]
    code_short = code.strip()[:3000]
    verify_prompt = (
        "You are the reviewer.\n"
        "Decide if the code satisfies the task.\n"
        'Return ONLY JSON: {"passed": boolean, "issues": [string], "notes": string}.\n\n'
        "Required checks:\n"
        "- Uses FastAPI\n"
        "- Has POST /users, POST /projects, POST /tasks\n"
        "- Has GET /tasks with project_id filter\n"
        "- Has __main__ running uvicorn\n"
        "- Has basic validation + HTTPException for invalid IDs\n\n"
        f"Task:\n{task}\n\nPlanning doc (truncated):\n{planning_doc_short}\n\nCode (truncated):\n{code_short}\n"
    )
    resp = model_adapter.invoke_model(
        prompt=verify_prompt,
        model=support_model,
        provider=config.provider,
        provider_base_url=config.provider_base_url,
        timeout_ms=getattr(config.budgets, "verifier_timeout_ms", getattr(config.budgets, "timeout_ms", 30000)),
        response_format="json",
        options={"num_predict": 128, "num_ctx": 512, "num_thread": 2, "temperature": 0, "top_p": 1, "seed": 42},
        keep_alive="60s",
    )
    raw = str(resp.get("text", ""))
    try:
        parsed = extract_json_object(raw)
        passed = bool(parsed.get("passed"))
        issues = parsed.get("issues") if isinstance(parsed.get("issues"), list) else []
        issues = [str(i) for i in issues]
        report = {"passed": passed, "issues": issues, "notes": str(parsed.get("notes", ""))}
    except Exception:
        passed, issues, report = heuristic_verify(task, planning_doc, code)
        report = {**report, "notes": "llm_verifier_parse_failed"}
    v1 = int(time.time() * 1000)
    event = _stage(
        run_id,
        task_id,
        "verifier",
        config,
        retry_count=0,
        attempt=0,
        started_ms=v0,
        ended_ms=v1,
        passed=passed,
        errors=["verification_failed"] if not passed else [],
        metadata={
            "agent": {"name": "verifier", "type": "llm", "role": "verifier"},
            "model": support_model,
            "model_error": resp.get("error"),
            "raw_response_excerpt": raw[:200],
            "verifier_report": report,
        },
    )
    return passed, issues, report, event
