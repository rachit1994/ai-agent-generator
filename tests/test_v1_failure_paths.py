import subprocess

import pytest

from V1.features.cli_runner import invoke_cursor_cli
from V1.features.prompt_loader import load_prompt_text


def test_invoke_cursor_cli_raises_on_timeout(monkeypatch) -> None:
    def _run(*args, **kwargs):  # noqa: ANN002, ANN003
        cmd = args[0]
        if cmd[0] == "qwen":
            raise subprocess.TimeoutExpired(cmd="qwen", timeout=1)
        return subprocess.CompletedProcess(
            args=cmd,
            returncode=0,
            stdout="EVIDENCE: fallback\nVERDICT: PASS",
            stderr="",
        )

    monkeypatch.setattr(subprocess, "run", _run)
    result = invoke_cursor_cli(role_name="architect", prompt_text="test", timeout_seconds=1)
    assert result.exit_code == 0
    assert "VERDICT: PASS" in result.stdout


def test_load_prompt_text_rejects_outside_prompt_directory(tmp_path) -> None:
    outside_file = tmp_path / "outside.md"
    outside_file.write_text("x", encoding="utf-8")
    with pytest.raises(ValueError):
        load_prompt_text(outside_file)


def test_invoke_cursor_cli_uses_cursor_as_fallback(monkeypatch) -> None:
    calls = []

    def _run(*args, **kwargs):  # noqa: ANN002, ANN003
        cmd = args[0]
        calls.append(cmd[0])
        if cmd[0] == "qwen":
            raise FileNotFoundError("qwen not installed")
        return subprocess.CompletedProcess(
            args=cmd,
            returncode=0,
            stdout="EVIDENCE: fallback\nVERDICT: PASS",
            stderr="",
        )

    monkeypatch.setattr(subprocess, "run", _run)
    result = invoke_cursor_cli(role_name="architect", prompt_text="test")
    assert calls == ["qwen", "cursor-agent"]
    assert result.exit_code == 0
    assert "VERDICT: PASS" in result.stdout

