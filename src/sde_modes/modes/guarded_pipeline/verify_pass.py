"""Initial heuristic verification and optional executor fix + verifier_fix."""

from __future__ import annotations

import time
from typing import Any

from . import prompts
from .events import _skipped_stage, _stage
from .executor import run_executor
from .verify_core import heuristic_verify


def run_initial_verification(
    run_id: str,
    task_id: str,
    safe: str,
    planner_doc: str,
    code: str,
    refusal: dict | None,
    config: Any,
    events: list[dict],
) -> tuple[bool, list[str], dict]:
    if refusal:
        passed = False
        issues = ["refused"]
        report: dict = {"passed": False, "issues": issues}
        skipped = _skipped_stage(run_id, task_id, "verifier", config, agent_name="verifier")
        (skipped["metadata"] or {}).update({"verifier_report": report})
        events.append(skipped)
        return passed, issues, report
    if not code.strip():
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
        return passed, issues, report
    v0 = int(time.time() * 1000)
    passed, issues, report = heuristic_verify(safe, planner_doc, code)
    v1 = int(time.time() * 1000)
    events.append(
        _stage(
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
                "agent": {"name": "verifier", "type": "heuristic", "role": "verifier"},
                "verifier_report": report,
            },
        )
    )
    return passed, issues, report


def run_fix_retry_if_configured(
    run_id: str,
    task_id: str,
    safe: str,
    planner_doc: str,
    code: str,
    refusal: dict | None,
    passed: bool,
    issues: list[str],
    report: dict,
    config: Any,
    events: list[dict],
) -> tuple[int, str, bool, list[str], dict]:
    if refusal or passed or config.budgets.max_retries <= 0:
        return 0, code, passed, issues, report
    retry_count = 1
    fix = prompts.fix_prompt(safe, planner_doc, issues, code)
    new_code, fix_event = run_executor(run_id, task_id, fix, config, attempt=1, retry_count=retry_count)
    events.append(fix_event)
    passed2, issues2, report2 = heuristic_verify(safe, planner_doc, new_code)
    events.append(
        _stage(
            run_id,
            task_id,
            "verifier_fix",
            config,
            retry_count=retry_count,
            attempt=1,
            passed=passed2,
            errors=["verification_failed"] if not passed2 else [],
            metadata={
                "agent": {"name": "verifier_fix", "type": "heuristic", "role": "verifier"},
                "verifier_report": report2,
            },
        )
    )
    return retry_count, new_code, passed2, issues2, report2
