"""Run orchestrator-owned verification commands (Category 4)."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

from time_and_budget.time_util import iso_now


def run_step_verification(
    *,
    repo_root: Path,
    session_dir: Path,
    step_id: str,
    verification: dict[str, Any] | None,
) -> dict[str, Any]:
    """Execute declared commands; return bundle suitable for JSON write."""
    results: list[dict[str, Any]] = []
    if not verification or not isinstance(verification.get("commands"), list):
        results.append(
            {
                "cmd": "noop",
                "passed": True,
                "exit_code": 0,
                "log": "no_verification_commands",
            }
        )
        bundle = {
            "schema_version": "1.0",
            "step_id": step_id,
            "passed": True,
            "captured_at": iso_now(),
            "commands": results,
        }
        _write_bundle(session_dir, step_id, bundle)
        return bundle

    all_ok = True
    for row in verification["commands"]:
        if not isinstance(row, dict):
            all_ok = False
            results.append({"cmd": "?", "passed": False, "exit_code": -1, "log": "bad_command_row"})
            continue
        cmd = str(row.get("cmd", "")).strip()
        args = row.get("args") or []
        if not isinstance(args, list):
            args = []
        args_str = [str(a) for a in args]
        cwd_raw = row.get("cwd")
        cwd = repo_root if cwd_raw in (None, "") else repo_root / str(cwd_raw)
        try:
            proc = subprocess.run(
                [cmd, *args_str],
                cwd=str(cwd),
                capture_output=True,
                text=True,
                timeout=int(row.get("timeout_sec", 600)),
                check=False,
            )
            ok = proc.returncode == 0
            all_ok = all_ok and ok
            log = (proc.stdout + "\n" + proc.stderr)[-8000:]
            results.append(
                {
                    "cmd": cmd,
                    "args": args_str,
                    "cwd": str(cwd),
                    "exit_code": proc.returncode,
                    "passed": ok,
                    "log": log,
                }
            )
        except subprocess.TimeoutExpired:
            all_ok = False
            results.append({"cmd": cmd, "passed": False, "exit_code": -9, "log": "timeout"})
        except OSError as exc:
            all_ok = False
            results.append({"cmd": cmd, "passed": False, "exit_code": -1, "log": str(exc)})

    bundle = {
        "schema_version": "1.0",
        "step_id": step_id,
        "passed": all_ok,
        "captured_at": iso_now(),
        "commands": results,
    }
    _write_bundle(session_dir, step_id, bundle)
    return bundle


def _write_bundle(session_dir: Path, step_id: str, bundle: dict[str, Any]) -> None:
    vdir = session_dir / "verification"
    vdir.mkdir(parents=True, exist_ok=True)
    (vdir / f"{step_id}.json").write_text(json.dumps(bundle, indent=2), encoding="utf-8")
