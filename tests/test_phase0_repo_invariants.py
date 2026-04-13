"""Phase 0: machine-checkable repo invariants for checklist item 1 (Python pin + lockfile)."""

from __future__ import annotations

from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]


def test_python_version_file_pins_3_13() -> None:
    text = (_REPO_ROOT / ".python-version").read_text(encoding="utf-8").strip()
    assert text == "3.13"


def test_uv_lock_committed_and_non_empty() -> None:
    lock = _REPO_ROOT / "uv.lock"
    assert lock.is_file()
    assert lock.stat().st_size > 0


def test_pyproject_requires_python_3_13_or_newer() -> None:
    raw = (_REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert 'requires-python = ">=3.13"' in raw


def test_phase0_checklist_item_5_starting_docs_exist_and_non_empty() -> None:
    """Phase 0 checklist step 5 — README, doc-precedence, execution playbook (paths must exist in repo)."""
    rels = (
        "README.md",
        "docs/implementation/2026-04-13-persona-agent-platform-doc-precedence.md",
        "docs/implementation/2026-04-13-persona-agent-platform-execution-playbook.md",
    )
    for relative in rels:
        path = _REPO_ROOT / relative
        assert path.is_file(), f"missing {relative}"
        assert path.stat().st_size > 0, f"empty {relative}"
