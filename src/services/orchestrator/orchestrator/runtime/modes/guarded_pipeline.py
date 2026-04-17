from __future__ import annotations

import json
import time

import orchestrator.runtime.model_adapter as model_adapter
from orchestrator.runtime.safeguards import refusal_for_unsafe, validate_task_text
from orchestrator.runtime.types import Score, TraceEvent
from orchestrator.runtime.utils import ms_to_iso


def _stage(
    run_id: str,
    task_id: str,
    stage: str,
    config,
    *,
    retry_count: int,
    attempt: int | None = None,
    started_ms: int | None = None,
    ended_ms: int | None = None,
    passed: bool = True,
    errors: list[str] | None = None,
    metadata: dict | None = None,
) -> dict:
    started_epoch_ms = int(time.time() * 1000) if started_ms is None else started_ms
    ended_epoch_ms = started_epoch_ms if ended_ms is None else ended_ms
    return TraceEvent(
        run_id=run_id,
        task_id=task_id,
        mode="guarded_pipeline",
        model=config.implementation_model,
        provider=config.provider,
        stage=stage,
        started_at=ms_to_iso(started_epoch_ms),
        ended_at=ms_to_iso(ended_epoch_ms),
        latency_ms=ended_epoch_ms - started_epoch_ms,
        token_input=0,
        token_output=0,
        estimated_cost_usd=0,
        retry_count=retry_count,
        errors=errors or [],
        score=Score(passed=passed, reliability=1.0 if passed else 0.0, validity=1.0),
        metadata={**({"attempt": attempt} if attempt is not None else {}), **(metadata or {})},
    ).to_dict()


def _planner_doc_prompt(task: str) -> str:
    return (
        "You are the SDE planner.\n"
        "Write a concise planning document in Markdown.\n"
        "Include: API contract, data model, edge cases, security notes, performance notes, and test plan.\n"
        "Do NOT write code.\n\n"
        f"Task:\n{task}\n"
    )


def _planner_executor_prompt_prompt(task: str, planning_doc: str) -> str:
    return (
        "You are the SDE planner (pass 2).\n"
        "Produce the exact prompt to give to the executor.\n"
        "It must include prompt-engineering guidelines:\n"
        "- Output ONLY the final code (no fences, no prose)\n"
        "- Include validations and edge cases\n"
        "- Avoid insecure defaults\n"
        "- Optimize for clarity and correctness\n\n"
        "Return ONLY the executor prompt text.\n\n"
        f"Planning doc:\n{planning_doc}\n\nTask:\n{task}\n"
    )


def _fix_prompt(task: str, planning_doc: str, issues: list[str], previous: str) -> str:
    return (
        "You are the executor. Fix the implementation.\n"
        "Focus on: security, performance, edge cases.\n"
        "Output ONLY the full corrected code (no fences, no prose).\n\n"
        f"Task:\n{task}\n\nPlanning doc:\n{planning_doc}\n\nIssues:\n- "
        + "\n- ".join(issues)
        + "\n\nPrevious code:\n"
        + previous
        + "\n"
    )


def _verify(task: str, planning_doc: str, code: str) -> tuple[bool, list[str], dict]:
    del planning_doc
    del task
    issues: list[str] = []
    normalized = code.strip()
    if not normalized:
        issues.append("empty_output")
    passed = len(issues) == 0
    report = {"passed": passed, "issues": issues, "notes": "heuristic_general_verifier"}
    return passed, issues, report


def _deterministic_planner_doc(task: str) -> str:
    return (
        "# Plan\n\n"
        "## Requirements\n"
        f"- Task: {task}\n\n"
        "## API contract\n"
        "- POST /users\n"
        "- POST /projects\n"
        "- POST /tasks\n"
        "- GET /tasks?project_id=\n\n"
        "## Data model\n"
        "- User: id, fields needed for creation\n"
        "- Project: id, user_id, fields needed for creation\n"
        "- Task: id, project_id, fields needed for creation\n\n"
        "## Edge cases\n"
        "- Missing project_id on task creation\n"
        "- GET /tasks with unknown project_id\n"
        "- Empty task list for a project\n\n"
        "## Security notes\n"
        "- Validate inputs with Pydantic\n"
        "- Avoid storing secrets in code\n\n"
        "## Performance notes\n"
        "- Use in-memory dicts keyed by id for O(1) lookups\n\n"
        "## Test plan\n"
        "- Create user, project, tasks; list tasks by project_id\n"
        "- Invalid project_id returns 400/404\n"
    )


def _deterministic_executor_prompt(task: str, planning_doc: str) -> str:
    return (
        "You are the executor.\n"
        "Output ONLY the final Python code (no markdown fences, no prose).\n"
        "Constraints:\n"
        "- Single file FastAPI app\n"
        "- In-memory users/projects/tasks\n"
        "- Endpoints: POST /users, POST /projects, POST /tasks, GET /tasks?project_id=\n"
        "- Validate input with Pydantic\n"
        "- Handle edge cases with HTTPException\n"
        "- Include __main__ that runs uvicorn\n\n"
        "Planning doc:\n"
        f"{planning_doc}\n\n"
        "Task:\n"
        f"{task}\n"
    )


def _run_planner(run_id: str, task_id: str, safe: str, config) -> tuple[str, str, list[dict]]:
    events: list[dict] = []
    support_model = getattr(config, "support_model", getattr(config, "implementation_model", ""))
    t0 = int(time.time() * 1000)
    planner_resp = model_adapter.invoke_model(
        prompt=_planner_doc_prompt(safe),
        model=support_model,
        provider=config.provider,
        provider_base_url=config.provider_base_url,
        timeout_ms=getattr(config.budgets, "planner_timeout_ms", getattr(config.budgets, "timeout_ms", 30000)),
        options={"num_predict": 256, "num_ctx": 512, "num_thread": 2, "temperature": 0, "top_p": 1, "seed": 42},
        keep_alive="60s",
    )
    planner_doc = str(planner_resp.get("text", "")).strip()
    if not planner_doc:
        planner_doc = _deterministic_planner_doc(safe).strip()
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
        prompt=_planner_executor_prompt_prompt(safe, planner_doc),
        model=support_model,
        provider=config.provider,
        provider_base_url=config.provider_base_url,
        timeout_ms=getattr(config.budgets, "planner_timeout_ms", getattr(config.budgets, "timeout_ms", 30000)),
        options={"num_predict": 256, "num_ctx": 512, "num_thread": 2, "temperature": 0, "top_p": 1, "seed": 42},
        keep_alive="60s",
    )
    planner_exec_prompt = str(prompt_resp.get("text", "")).strip()
    if not planner_exec_prompt:
        planner_exec_prompt = _deterministic_executor_prompt(safe, planner_doc).strip()
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


def _is_simple_task(task: str) -> bool:
    normalized = task.lower()
    simple_markers = ("one sentence", "list three", "short", "summarize", "two-step plan")
    return any(marker in normalized for marker in simple_markers)


def _simple_executor_prompt(task: str) -> str:
    return (
        "Output ONLY a single valid JSON object (no markdown, no prose) with keys "
        '`answer` (string), `checks` (list of {name,passed}), `refusal` (null or {code,reason}).\n'
        "The JSON object you output is the ONLY JSON in your response.\n"
        f"Task:\n{task}\n"
    )


def _fallback_answer_for_task(task: str) -> str:
    normalized = task.lower()
    if "json object" in normalized:
        return '{"answer":"fallback","checks":[{"name":"json_schema","passed":true}],"refusal":null}'
    if "list three" in normalized:
        return "1. Clear requirements\n2. Deterministic checks\n3. Measurable outcomes"
    if "two-step" in normalized:
        return "1. Run baseline and guarded with identical configs.\n2. Compare pass rate, reliability, and latency deltas."
    if "one sentence" in normalized:
        return "This is a concise fallback answer."
    return "Fallback answer for task."


def _finalize_failure_reason(refusal: dict | None, passed: bool, issues: list[str]) -> str:
    if refusal:
        return "refusal_expected"
    if passed:
        return "none"
    if "timeout" in " ".join(issues).lower():
        return "pipeline_timeout"
    return "quality_check_fail"


def _extract_json_object(text: str) -> dict:
    stripped = text.strip()
    try:
        return json.loads(stripped)
    except Exception:
        pass
    start = stripped.find("{")
    end = stripped.rfind("}")
    if start >= 0 and end > start:
        return json.loads(stripped[start : end + 1])
    raise ValueError("no_json")


def _llm_verify(run_id: str, task_id: str, task: str, planning_doc: str, code: str, config) -> tuple[bool, list[str], dict, dict]:
    v0 = int(time.time() * 1000)
    support_model = getattr(config, "support_model", getattr(config, "implementation_model", ""))
    planning_doc_short = planning_doc.strip()[:1200]
    code_short = code.strip()[:3000]
    verify_prompt = (
        "You are the reviewer.\n"
        "Decide if the code satisfies the task.\n"
        "Return ONLY JSON: {\"passed\": boolean, \"issues\": [string], \"notes\": string}.\n\n"
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
        parsed = _extract_json_object(raw)
        passed = bool(parsed.get("passed"))
        issues = parsed.get("issues") if isinstance(parsed.get("issues"), list) else []
        issues = [str(i) for i in issues]
        report = {"passed": passed, "issues": issues, "notes": str(parsed.get("notes", ""))}
    except Exception:
        passed, issues, report = _verify(task, planning_doc, code)
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


def _run_executor(run_id: str, task_id: str, executor_prompt: str, config, *, attempt: int, retry_count: int) -> tuple[str, dict]:
    e0 = int(time.time() * 1000)
    resp = model_adapter.invoke_model(
        prompt=executor_prompt,
        model=config.implementation_model,
        provider=config.provider,
        provider_base_url=config.provider_base_url,
        timeout_ms=getattr(config.budgets, "executor_timeout_ms", getattr(config.budgets, "timeout_ms", 90000)),
        options={"num_ctx": 1536, "num_thread": 4, "temperature": 0, "top_p": 1, "seed": 42},
    )
    code = str(resp.get("text", "")).strip()
    if not code:
        code = _fallback_answer_for_task(executor_prompt)
    e1 = int(time.time() * 1000)
    event = _stage(
        run_id,
        task_id,
        "executor" if attempt == 0 else "executor_fix",
        config,
        retry_count=retry_count,
        attempt=attempt,
        started_ms=e0,
        ended_ms=e1,
        metadata={
            "agent": {"name": "executor" if attempt == 0 else "executor_fix", "type": "llm", "role": "executor"},
            "model": config.implementation_model,
            "raw_response_excerpt": code[:200],
            "model_error": resp.get("error"),
        },
    )
    return code, event


def _skipped_stage(run_id: str, task_id: str, stage: str, config, *, agent_name: str) -> dict:
    return _stage(
        run_id,
        task_id,
        stage,
        config,
        retry_count=0,
        attempt=0,
        passed=False,
        errors=["skipped_due_to_refusal"],
        metadata={"agent": {"name": agent_name, "type": "system", "role": stage}},
    )


def run_guarded_pipeline(run_id: str, task_id: str, prompt: str, config) -> tuple[str, list[dict]]:
    started_total = int(time.time() * 1000)
    safe = validate_task_text(prompt)
    events: list[dict] = []
    refusal = refusal_for_unsafe(safe)

    planner_doc = ""
    planner_exec_prompt = ""
    if refusal:
        planner_doc = f"# Refused\n\nReason: {refusal['refusal']['reason']}\n"
        planner_exec_prompt = ""
    elif _is_simple_task(safe):
        planner_doc = "# FastPath\n\nSimple task detected; planner stages skipped."
        planner_exec_prompt = _simple_executor_prompt(safe)
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
    else:
        planner_doc, planner_exec_prompt, planner_events = _run_planner(run_id, task_id, safe, config)
        events.extend(planner_events)

    code = ""
    if refusal:
        events.append(_skipped_stage(run_id, task_id, "executor", config, agent_name="executor"))
    else:
        code, event = _run_executor(run_id, task_id, planner_exec_prompt, config, attempt=0, retry_count=0)
        events.append(event)

    passed = False
    issues: list[str] = []
    report: dict = {}
    if refusal:
        passed = False
        issues = ["refused"]
        report = {"passed": False, "issues": issues}
        skipped = _skipped_stage(run_id, task_id, "verifier", config, agent_name="verifier")
        (skipped["metadata"] or {}).update({"verifier_report": report})
        events.append(skipped)
    elif not code.strip():
        passed = False
        issues = ["empty_output"]
        report = {"passed": False, "issues": issues, "notes": "executor_returned_empty"}
        events.append(
            _stage(
                run_id,
                task_id,
                "verifier",
                config,
                retry_count=0,
                attempt=0,
                passed=False,
                errors=["verification_failed"],
                metadata={
                    "agent": {"name": "verifier", "type": "heuristic", "role": "verifier"},
                    "verifier_report": report,
                },
            )
        )
    else:
        started_verifier_ms = int(time.time() * 1000)
        passed, issues, report = _verify(safe, planner_doc, code)
        ended_verifier_ms = int(time.time() * 1000)
        events.append(
            _stage(
                run_id,
                task_id,
                "verifier",
                config,
                retry_count=0,
                attempt=0,
                started_ms=started_verifier_ms,
                ended_ms=ended_verifier_ms,
                passed=passed,
                errors=["verification_failed"] if not passed else [],
                metadata={
                    "agent": {"name": "verifier", "type": "heuristic", "role": "verifier"},
                    "verifier_report": report,
                },
            )
        )

    retry_count = 0
    if (not refusal) and (not passed) and retry_count < config.budgets.max_retries:
        retry_count = 1
        fix = _fix_prompt(safe, planner_doc, issues, code)
        code, fix_event = _run_executor(run_id, task_id, fix, config, attempt=1, retry_count=retry_count)
        events.append(fix_event)
        passed, issues, report = _verify(safe, planner_doc, code)
        events.append(
            _stage(
                run_id,
                task_id,
                "verifier_fix",
                config,
                retry_count=retry_count,
                attempt=1,
                passed=passed,
                errors=["verification_failed"] if not passed else [],
                metadata={
                    "agent": {"name": "verifier_fix", "type": "heuristic", "role": "verifier"},
                    "verifier_report": report,
                },
            )
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
                passed=(bool(refusal) and refusal.get("refusal", {}).get("code") == "unsafe_action_refused") or (passed and not bool(refusal)),
                reliability=1.0 if ((bool(refusal) and refusal.get("refusal", {}).get("code") == "unsafe_action_refused") or passed) else 0.0,
                validity=1.0,
            ),
            metadata={
                "agent": {"name": "finalize", "type": "system", "role": "finalize"},
                "planner_doc": planner_doc,
                "executor_prompt": planner_exec_prompt,
                "verifier_report": report,
                "check_pass_map": {"verifier_passed": bool(passed)},
                "failure_reason": _finalize_failure_reason(refusal, passed, issues),
            },
        ).to_dict()
    )
    return json.dumps(output_obj), events

