from __future__ import annotations

from sde_modes.modes.guarded_pipeline.verify_core import heuristic_verify


def test_heuristic_verify_blocks_eval_under_static_gate() -> None:
    code = "x = 1\neval('1+1')\n"
    passed, issues, report = heuristic_verify("t", "plan", code)
    assert passed is False
    assert any("static_gate:eval_call" in i for i in issues)
    assert "static_gates" in report


def test_heuristic_verify_warns_bare_except() -> None:
    code = "try:\n    x = 1\nexcept:\n    pass\n"
    passed, issues, report = heuristic_verify("t", "plan", code)
    assert passed is True
    assert issues == []
    assert any("bare_except" in h for h in report["hints"])


def test_heuristic_verify_empty_still_fails() -> None:
    passed, issues, _report = heuristic_verify("t", "plan", "   ")
    assert passed is False
    assert "empty_output" in issues
