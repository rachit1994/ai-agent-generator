"""Phase 9: read-only project session / plan validation (CI preflight)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .project_plan import detect_dependency_cycle
from .project_schema import read_json_dict, validate_progress, validate_project_plan
from .project_workspace import evaluate_workspace_repo_gates

EXIT_VALIDATE_OK = 0
EXIT_VALIDATE_WORKSPACE = 1
EXIT_VALIDATE_INVALID = 2


def validate_project_session(
    session_dir: Path,
    *,
    repo_root: Path,
    check_workspace: bool = True,
    progress_file: Path | None = None,
) -> dict[str, Any]:
    """
    Validate ``project_plan.json`` and optional workspace gates without executing steps.

    Returns a JSON-serializable dict including ``exit_code``:
    **0** ok, **1** workspace contract failed, **2** missing/invalid plan or dependency cycle.
    """
    session_dir = session_dir.resolve()
    repo_root = repo_root.resolve()
    plan_path = session_dir / "project_plan.json"
    out: dict[str, Any] = {"session_dir": str(session_dir), "repo_root": str(repo_root)}

    if not plan_path.is_file():
        out["exit_code"] = EXIT_VALIDATE_INVALID
        out["ok"] = False
        out["error"] = "missing_project_plan_json"
        return out

    try:
        plan = read_json_dict(plan_path)
    except (OSError, ValueError, TypeError) as exc:
        out["exit_code"] = EXIT_VALIDATE_INVALID
        out["ok"] = False
        out["error"] = "project_plan_read_failed"
        out["detail"] = str(exc)
        return out

    perrs = validate_project_plan(plan)
    if perrs:
        out["exit_code"] = EXIT_VALIDATE_INVALID
        out["ok"] = False
        out["error"] = "invalid_project_plan"
        out["details"] = perrs
        return out

    cyc = detect_dependency_cycle(plan)
    if cyc:
        out["exit_code"] = EXIT_VALIDATE_INVALID
        out["ok"] = False
        out["error"] = "dependency_cycle"
        out["cycle"] = cyc
        return out

    if check_workspace:
        gate = evaluate_workspace_repo_gates(plan, repo_root)
        if gate:
            out["exit_code"] = EXIT_VALIDATE_WORKSPACE
            out["ok"] = False
            out["error"] = "workspace_contract"
            out["detail"] = gate
            return out

    progress_path = progress_file.resolve() if progress_file is not None else session_dir / "progress.json"
    progress_warnings: list[str] = []
    if progress_path.is_file():
        try:
            prog = read_json_dict(progress_path)
            prog_errs = validate_progress(prog)
            if prog_errs:
                progress_warnings.append(f"progress_nonconforming:{prog_errs}")
        except (OSError, ValueError, TypeError) as exc:
            progress_warnings.append(f"progress_read_failed:{exc}")

    out["exit_code"] = EXIT_VALIDATE_OK
    out["ok"] = True
    out["plan_path"] = str(plan_path)
    out["step_count"] = len(plan.get("steps") or [])
    if progress_warnings:
        out["progress_warnings"] = progress_warnings
    return out
