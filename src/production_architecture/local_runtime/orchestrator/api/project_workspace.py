"""Phase 7: enforce optional ``workspace`` on ``project_plan.json`` (branch + path prefixes)."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any


def _git_ok(repo_root: Path, *args: str) -> tuple[int, str, str]:
    proc = subprocess.run(
        ["git", "-C", str(repo_root), *args],
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    return proc.returncode, (proc.stdout or "").strip(), (proc.stderr or "").strip()


def git_head_matches_branch(repo_root: Path, branch: str) -> tuple[bool, str | None]:
    """
    True when ``HEAD`` resolves to the same commit as ``refs/heads/<branch>``.

    Works for detached HEAD checked out at that branch tip.
    """
    if not branch.strip():
        return False, "workspace_branch_empty"
    if not (repo_root / ".git").exists():
        return False, "workspace_branch_requires_git_repo"
    ref = f"refs/heads/{branch.strip()}"
    rc1, tip, err1 = _git_ok(repo_root, "rev-parse", ref)
    if rc1 != 0:
        return False, f"workspace_branch_ref_missing:{ref}:{err1}"
    rc2, head, err2 = _git_ok(repo_root, "rev-parse", "HEAD")
    if rc2 != 0:
        return False, f"workspace_head_unreadable:{err2}"
    if tip != head:
        return False, f"workspace_branch_mismatch:want={tip} got={head}"
    return True, None


def _normalize_slash_path(s: str) -> str:
    x = s.strip().replace("\\", "/")
    while x.startswith("./"):
        x = x[2:]
    return x


def _path_scope_to_prefix_dir(pattern: str) -> str | None:
    """
    Map a glob-like path_scope entry to a conservative directory prefix (no ``..``).

    Examples: ``src/**`` → ``src``; ``docs/**/*.md`` → ``docs``; ``src/foo.py`` → ``src``.
    """
    raw = _normalize_slash_path(pattern)
    if not raw:
        return None
    parts = raw.split("/")
    if any(p == ".." for p in parts):
        return None
    if "*" in raw:
        before = raw.split("*", 1)[0].rstrip("/")
        return before if before else None
    if "/" not in raw:
        return None
    return raw.rsplit("/", 1)[0]


def _prefix_dir_to_key(dir_prefix: str) -> str:
    d = dir_prefix.strip().rstrip("/")
    if not d:
        return ""
    return d + "/"


def path_scope_pattern_allowed(pattern: str, allowed_prefixes: list[str]) -> bool:
    """
    True if the pattern's directory prefix is contained by an allowed repo prefix.
    """
    root = _path_scope_to_prefix_dir(pattern)
    if root is None:
        return False
    scope_key = _prefix_dir_to_key(root)
    for ap in allowed_prefixes:
        a = _normalize_slash_path(ap)
        if not a:
            continue
        allow_key = _prefix_dir_to_key(a.rstrip("*"))
        if not allow_key:
            continue
        if scope_key.startswith(allow_key):
            return True
    return False


def _normalized_allowed_prefixes(workspace: dict[str, Any]) -> list[str]:
    raw_prefs = workspace.get("allowed_path_prefixes")
    if not isinstance(raw_prefs, list):
        return []
    return [str(p) for p in raw_prefs if isinstance(p, str) and p.strip()]


def _path_scope_errors_for_step(step_row: dict[str, Any], allowed_prefixes: list[str]) -> list[str]:
    sid = step_row.get("step_id")
    if not isinstance(sid, str):
        return []
    scopes = step_row.get("path_scope") or []
    if not isinstance(scopes, list) or not scopes:
        return [f"project_plan_workspace_path_scope_required:{sid}"]
    errs: list[str] = []
    for pat in scopes:
        if not isinstance(pat, str) or not pat.strip():
            errs.append(f"project_plan_workspace_path_scope_bad_pattern:{sid}")
            continue
        if not path_scope_pattern_allowed(pat, allowed_prefixes):
            errs.append(f"project_plan_workspace_path_scope_outside_prefixes:{sid}:{pat}")
    return errs


def plan_workspace_path_errors(plan: dict[str, Any]) -> list[str]:
    """
    When ``workspace.allowed_path_prefixes`` is a non-empty list, ensure every step's
    ``path_scope`` patterns sit under those prefixes.
    """
    ws = plan.get("workspace")
    if not isinstance(ws, dict):
        return []
    if ws.get("allowed_path_prefixes") is None:
        return []
    prefs = _normalized_allowed_prefixes(ws)
    if not prefs:
        return []
    errors: list[str] = []
    for row in plan.get("steps") or []:
        if isinstance(row, dict):
            errors.extend(_path_scope_errors_for_step(row, prefs))
    return errors


def evaluate_workspace_repo_gates(plan: dict[str, Any], repo_root: Path) -> str | None:
    """
    Runtime checks (git). Returns a short machine reason string, or ``None`` if ok / N/A.
    """
    ws = plan.get("workspace")
    if not isinstance(ws, dict):
        return None
    branch = ws.get("branch")
    if branch is None:
        return None
    if not isinstance(branch, str) or not branch.strip():
        return None
    ok, reason = git_head_matches_branch(repo_root, branch)
    if ok:
        return None
    return reason or "workspace_branch_check_failed"
