"""Run role prompts via Qwen Code with Cursor fallback."""

from __future__ import annotations

import subprocess

from V1.contracts.types import RoleResult
from V1.utils.constants import DEFAULT_TIMEOUT_SECONDS

QWEN_COMMAND = "qwen"
CURSOR_COMMAND = "cursor-agent"


def invoke_cursor_cli(role_name: str, prompt_text: str, timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS) -> RoleResult:
    role_wrapped_prompt = (
        f"You are acting as the '{role_name}' role.\n"
        f"Return both markers exactly once:\n"
        f"EVIDENCE: <concise evidence>\n"
        f"VERDICT: PASS|FAIL\n\n"
        f"{prompt_text}"
    )
    primary_cmd = [QWEN_COMMAND, "-p", role_wrapped_prompt]
    fallback_cmd = [
        CURSOR_COMMAND,
        "agent",
        "--print",
        "--output-format",
        "text",
        "--trust",
        role_wrapped_prompt,
    ]
    try:
        completed = subprocess.run(
            primary_cmd,
            capture_output=True,
            text=True,
            check=False,
            timeout=timeout_seconds,
        )
        if completed.returncode != 0:
            completed = subprocess.run(
                fallback_cmd,
                capture_output=True,
                text=True,
                check=False,
                timeout=timeout_seconds,
            )
    except subprocess.TimeoutExpired as primary_timeout:
        completed = subprocess.run(
            fallback_cmd,
            capture_output=True,
            text=True,
            check=False,
            timeout=timeout_seconds,
        )
        completed = subprocess.CompletedProcess(
            args=completed.args,
            returncode=completed.returncode,
            stdout=completed.stdout,
            stderr=(completed.stderr + f"\nPrimary qwen timeout: {primary_timeout}").strip(),
        )
    except FileNotFoundError:
        completed = subprocess.run(
            fallback_cmd,
            capture_output=True,
            text=True,
            check=False,
            timeout=timeout_seconds,
        )
    return RoleResult(
        role_name=role_name,
        stdout=completed.stdout,
        stderr=completed.stderr,
        exit_code=completed.returncode,
    )

