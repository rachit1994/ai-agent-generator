"""Load prompt text from prompt files."""

from __future__ import annotations

from pathlib import Path

from V1.utils.constants import PROMPTS_DIR


def load_prompt_text(path: Path) -> str:
    resolved = path.resolve()
    if PROMPTS_DIR.resolve() not in resolved.parents:
        raise ValueError(f"Prompt path must stay within {PROMPTS_DIR}")
    return resolved.read_text(encoding="utf-8").strip()


def load_role_prompt(role_name: str) -> str:
    return load_prompt_text(PROMPTS_DIR / "roles" / f"{role_name}.md")


def load_phase_prompt(phase_id: str) -> str:
    return load_prompt_text(PROMPTS_DIR / "phases" / f"{phase_id}.md")

