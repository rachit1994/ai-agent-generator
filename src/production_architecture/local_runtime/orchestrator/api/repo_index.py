"""Lightweight repo file manifest for project ContextPack (Category 1 MVP)."""

from __future__ import annotations

import fnmatch
import subprocess
from pathlib import Path
from typing import Any


def _normalized_scopes(path_scopes: list[str]) -> tuple[list[str], bool]:
    scopes: list[str] = []
    malformed = False
    for scope in path_scopes:
        if not isinstance(scope, str):
            malformed = True
            continue
        cleaned = scope.strip()
        if not cleaned:
            malformed = True
            continue
        scopes.append(cleaned)
    return scopes, malformed


def _empty_index(repo_root: Path, *, path_scopes: list[str]) -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "repo_root": str(repo_root.resolve()),
        "path_scopes": path_scopes,
        "file_count": 0,
        "paths": [],
    }


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
    scopes, malformed = _normalized_scopes(path_scopes)
    if malformed:
        return _empty_index(repo_root, path_scopes=scopes)
    if not isinstance(max_files, int) or isinstance(max_files, bool) or max_files < 1:
        return _empty_index(repo_root, path_scopes=scopes)

    all_paths = _git_ls_files(repo_root)
    if all_paths is None:
        all_paths = [str(p.relative_to(repo_root)) for p in repo_root.rglob("*") if p.is_file()][: max_files * 2]
    matched: list[str] = []
    for rel in all_paths:
        if len(matched) >= max_files:
            break
        if not scopes:
            matched.append(rel)
            continue
        for pat in scopes:
            if fnmatch.fnmatch(rel, pat) or fnmatch.fnmatch(rel, pat.rstrip("/") + "/**"):
                matched.append(rel)
                break
    out = _empty_index(repo_root, path_scopes=scopes)
    out["file_count"] = len(matched)
    out["paths"] = matched[:max_files]
    return out
