from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


def _load_bump_module():
    root = Path(__file__).resolve().parent.parent
    path = root / "scripts" / "bump_version.py"
    spec = importlib.util.spec_from_file_location("_bump_version", path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_mod = _load_bump_module()


@pytest.mark.parametrize(
    ("current", "bump", "expected"),
    [
        ("0.3.0", "minor", "0.4.0"),
        ("0.3.9", "minor", "0.4.0"),
        ("1.2.3", "patch", "1.2.4"),
        ("1.2.3", "major", "2.0.0"),
        ("0.0.0", "minor", "0.1.0"),
    ],
)
def test_compute_next_version(current: str, bump: str, expected: str) -> None:
    assert _mod.compute_next_version(current, bump) == expected


def test_compute_next_version_none_unchanged() -> None:
    assert _mod.compute_next_version("0.3.0", "none") == "0.3.0"


def test_replace_project_version_roundtrip() -> None:
    text = '[project]\nname = "sde"\nversion = "0.3.0"\n'
    out = _mod.replace_project_version(text, "0.4.0")
    assert 'version = "0.4.0"' in out
    assert _mod.read_project_version(out) == "0.4.0"


def test_compute_next_version_invalid_bump() -> None:
    with pytest.raises(ValueError, match="unknown"):
        _mod.compute_next_version("0.1.0", "beta")
