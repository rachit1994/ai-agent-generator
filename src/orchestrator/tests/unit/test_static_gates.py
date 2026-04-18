from __future__ import annotations

import json
from pathlib import Path

from sde_gates.hard_stops import evaluate_hard_stops
from sde_gates.static_analysis import run_static_code_gates


def test_hs04_fails_when_static_report_not_passed_all(tmp_path: Path) -> None:
    sg = tmp_path / "static_gates_report.json"
    sg.write_text(
        json.dumps({"schema_version": "1.0", "passed_all": False, "blockers": [{"id": "eval_call"}]}),
        encoding="utf-8",
    )
    hs = evaluate_hard_stops(tmp_path, [], {}, run_status="ok", mode="baseline")
    hs04 = next(h for h in hs if h["id"] == "HS04")
    assert hs04["passed"] is False


def test_hs04_passes_when_static_report_clean(tmp_path: Path) -> None:
    sg = tmp_path / "static_gates_report.json"
    sg.write_text(json.dumps({"schema_version": "1.0", "passed_all": True, "blockers": []}), encoding="utf-8")
    hs = evaluate_hard_stops(tmp_path, [], {}, run_status="ok", mode="baseline")
    hs04 = next(h for h in hs if h["id"] == "HS04")
    assert hs04["passed"] is True


def test_static_gates_no_python_includes_tool_keys() -> None:
    rep = run_static_code_gates(extracted_python=None)
    assert rep["bandit"]["skipped"] == "no_python_source"
    assert rep["basedpyright"]["skipped"] == "no_python_source"


def test_static_gates_passes_clean_python() -> None:
    rep = run_static_code_gates(extracted_python="def f():\n    return 1\n")
    assert rep["passed_all"] is True
    assert not rep["blockers"]


def test_static_gates_blocks_subprocess_shell_true() -> None:
    code = "import subprocess\nsubprocess.run('x', shell=True)\n"
    rep = run_static_code_gates(extracted_python=code)
    assert rep["passed_all"] is False
    assert any(b.get("id") == "subprocess_shell_true" for b in rep["blockers"])


def test_static_gates_blocks_syntax_error() -> None:
    rep = run_static_code_gates(extracted_python="def x(\n")
    assert rep["passed_all"] is False
    assert any(b.get("id") == "syntax_error" for b in rep["blockers"])

