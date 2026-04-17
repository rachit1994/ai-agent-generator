"""LLM prompt strings for planner, executor fix, and verifier paths."""

from __future__ import annotations


def planner_doc_prompt(task: str) -> str:
    return (
        "You are the SDE planner.\n"
        "Write a concise planning document in Markdown.\n"
        "Include: API contract, data model, edge cases, security notes, performance notes, and test plan.\n"
        "Do NOT write code.\n\n"
        f"Task:\n{task}\n"
    )


def planner_executor_prompt(task: str, planning_doc: str) -> str:
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


def fix_prompt(task: str, planning_doc: str, issues: list[str], previous: str) -> str:
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
