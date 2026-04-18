#!/usr/bin/env python3
"""Bump ``[project].version`` in pyproject.toml (semver MAJOR.MINOR.PATCH).

Environment:
  VERSION_BUMP   ``minor`` (default), ``patch``, ``major``, or ``none`` (no change).
  SKIP_VERSION_BUMP  If set to ``1``, exit immediately (used by the pre-push hook).
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

_VERSION_LINE = re.compile(r"^(version\s*=\s*\")([\d]+)\.([\d]+)\.([\d]+)(\")", re.MULTILINE)


def compute_next_version(current: str, bump: str) -> str:
    bump = bump.lower().strip()
    if bump == "none":
        return current
    parts = current.split(".")
    if len(parts) != 3:
        raise ValueError(f"expected semver x.y.z, got {current!r}")
    major, minor, patch = (int(parts[0]), int(parts[1]), int(parts[2]))
    match bump:
        case "major":
            return f"{major + 1}.0.0"
        case "minor":
            return f"{major}.{minor + 1}.0"
        case "patch":
            return f"{major}.{minor}.{patch + 1}"
        case _:
            raise ValueError(f"unknown VERSION_BUMP {bump!r} (use major, minor, patch, none)")


def read_project_version(text: str) -> str:
    m = _VERSION_LINE.search(text)
    if not m:
        raise ValueError("could not find project version = \"x.y.z\" in pyproject.toml")
    return f"{m.group(2)}.{m.group(3)}.{m.group(4)}"


def replace_project_version(text: str, new_version: str) -> str:
    def repl(m: re.Match[str]) -> str:
        return f"{m.group(1)}{new_version}{m.group(5)}"

    new_text, n = _VERSION_LINE.subn(repl, text, count=1)
    if n != 1:
        raise ValueError("version line replace failed")
    return new_text


def main() -> int:
    if os.environ.get("SKIP_VERSION_BUMP", "").strip() == "1":
        return 0

    root = Path(__file__).resolve().parent.parent
    path = root / "pyproject.toml"
    bump = os.environ.get("VERSION_BUMP", "minor").lower().strip()
    text = path.read_text(encoding="utf-8")
    current = read_project_version(text)
    if bump == "none":
        print(current, end="")
        return 0

    nxt = compute_next_version(current, bump)
    if nxt == current:
        print(current, end="")
        return 0

    path.write_text(replace_project_version(text, nxt), encoding="utf-8")
    print(nxt, end="")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ValueError as e:
        print(f"bump_version: {e}", file=sys.stderr)
        raise SystemExit(1)
