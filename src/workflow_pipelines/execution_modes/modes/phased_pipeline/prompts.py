"""Prompts for phased (multi-todo) execution."""

from __future__ import annotations


def phased_decompose_prompt(goal: str) -> str:
    return (
        "You are the SDE phased planner. Break the user's goal into sequential phases and "
        "atomic todos. Each todo must be small enough for one guarded implementation pass "
        "(plan → code → verify).\n\n"
        "Reply with ONLY one JSON object (no markdown fences, no prose) using this shape:\n"
        '{"schema_version":"1.0","phases":[{"phase_id":"string","title":"string",'
        '"todos":[{"todo_id":"string","title":"string","acceptance_criteria":"string"}]}]}\n\n'
        "Rules:\n"
        "- At least one phase; each phase has at least one todo.\n"
        "- todo_id and phase_id: use lowercase letters, digits, underscores only.\n"
        "- Order phases and todos in the intended execution order.\n"
        "- acceptance_criteria must be concrete and verifiable.\n\n"
        f"User goal:\n{goal}\n"
    )
