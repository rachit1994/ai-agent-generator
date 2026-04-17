"""Fast-path detection for trivial natural-language tasks."""

from __future__ import annotations


def is_simple_task(task: str) -> bool:
    normalized = task.lower()
    simple_markers = ("one sentence", "list three", "short", "summarize", "two-step plan")
    return any(marker in normalized for marker in simple_markers)


def simple_executor_prompt(task: str) -> str:
    return (
        "Output ONLY a single valid JSON object (no markdown, no prose) with keys "
        '`answer` (string), `checks` (list of {name,passed}), `refusal` (null or {code,reason}).\n'
        "The JSON object you output is the ONLY JSON in your response.\n"
        f"Task:\n{task}\n"
    )
