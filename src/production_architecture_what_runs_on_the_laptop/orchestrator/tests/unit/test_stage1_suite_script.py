from __future__ import annotations

from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[5]


def _script_path() -> Path:
    return _repo_root() / "scripts" / "run-stage1-suite.sh"


def test_stage1_suite_script_declares_wall_clock_slo() -> None:
    body = _script_path().read_text(encoding="utf-8")
    assert "STAGE1_SUITE_MAX_SECONDS" in body
    assert "wall-clock SLO breached" in body
    assert "must be >= 1 when set" in body
    assert "test_stage1_suite_script.py" in body
    assert "test_project_stage1_observability_export.py" in body
    assert "test_stage1_cold_start_demo.py" in body
    assert "docs/UNDERSTANDING-THE-CODE.md" in body


def test_version_index_only_script_is_noop() -> None:
    path = _repo_root() / "scripts" / "version-index-only.sh"
    assert path.is_file()
    body = path.read_text(encoding="utf-8")
    assert "skipped" in body
