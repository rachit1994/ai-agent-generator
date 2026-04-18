"""Optional git worktrees for parallel project steps (Phase 6)."""

from __future__ import annotations

import subprocess
from pathlib import Path


def git_worktree_available(repo_root: Path) -> bool:
    """True if ``repo_root`` looks like a git checkout (file or dir ``.git``)."""
    return (repo_root / ".git").exists()


def add_detached_worktree(repo_root: Path, worktree_path: Path) -> bool:
    """
    ``git worktree add --detach <path> HEAD``.

    ``worktree_path`` should be outside the main working tree when possible (e.g. under session_dir).
    """
    worktree_path.parent.mkdir(parents=True, exist_ok=True)
    if worktree_path.exists():
        remove_worktree(repo_root, worktree_path)
    proc = subprocess.run(
        ["git", "-C", str(repo_root), "worktree", "add", "--detach", str(worktree_path), "HEAD"],
        capture_output=True,
        text=True,
        timeout=180,
        check=False,
    )
    return proc.returncode == 0


def remove_worktree(repo_root: Path, worktree_path: Path) -> None:
    """``git worktree remove --force`` from the primary repo."""
    if not worktree_path.exists():
        return
    subprocess.run(
        ["git", "-C", str(repo_root), "worktree", "remove", "--force", str(worktree_path)],
        capture_output=True,
        text=True,
        timeout=180,
        check=False,
    )
