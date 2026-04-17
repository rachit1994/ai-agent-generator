"""LLM prompts for baseline JSON structured output."""

from __future__ import annotations


def baseline_executor_prompt(safe: str) -> str:
    return (
        "Output ONLY a single valid JSON object (no markdown, no prose) with keys "
        '`answer` (string), `checks` (list of {name,passed}), `refusal` (null or {code,reason}).\n'
        "The JSON object you output is the ONLY JSON in your response.\n"
        "The `answer` value must be the solution text itself (for code tasks: the raw code), "
        "not another JSON object.\n"
        f"Task:\n{safe}\n"
    )


def baseline_repair_prompt(safe: str) -> str:
    return (
        "Repair your previous response.\n"
        "Output ONLY a single valid JSON object (no markdown, no prose) with keys "
        '`answer` (string), `checks` (list of {name,passed}), `refusal` (null or {code,reason}).\n'
        "The JSON object you output is the ONLY JSON in your response.\n"
        "The `answer` value must be the solution text itself (for code tasks: the raw code), "
        "not another JSON object.\n\n"
        f"Task:\n{safe}\n"
    )
