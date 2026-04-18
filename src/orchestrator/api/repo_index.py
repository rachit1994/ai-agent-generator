"""Lightweight repo file manifest for project ContextPack (Category 1 MVP)."""

from __future__ import annotations

import fnmatch
import json
import subprocess
from pathlib import Path
from typing import Any


def _git_ls_files(repo_root: Path) -> list[str] | None:
    try:
        proc = subprocess.run(
            ["git", "-C", str(repo_root), "ls-files"],
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
        if proc.returncode != 0:
            return None
        lines = [ln.strip() for ln in proc.stdout.splitlines() if ln.strip()]
        return lines
    except (OSError, subprocess.TimeoutExpired):
        return None


def build_repo_index(
    repo_root: Path,
    *,
    path_scopes: list[str],
    max_files: int = 500,
) -> dict[str, Any]:
    """
    Collect tracked paths (git when available) filtered by glob-like scopes.

    ``path_scopes`` entries use ``**`` or ``*`` shell-style patterns relative to repo root.
    """
    all_paths = _git_ls_files(repo_root)
    if all_paths is None:
        all_paths = [str(p.relative_to(repo_root)) for p in repo_root.rglob("*") if p.is_file()][: max_files * 2]
    matched: list[str] = []
    for rel in all_paths:
        if len(matched) >= max_files:
            break
        if not path_scopes:
            matched.append(rel)
            continue
        for pat in path_scopes:
            if fnmatch.fnmatch(rel, pat) or fnmatch.fnmatch(rel, pat.rstrip("/") + "/**"):
                matched.append(rel)
                break
    return {
        "schema_version": "1.0",
        "repo_root": str(repo_root.resolve()),
        "path_scopes": path_scopes,
        "file_count": len(matched),
        "paths": matched[:max_files],
    }
