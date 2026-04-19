"""B5: shell cold-start demo matches golden Stage 1 success path."""

from __future__ import annotations

import subprocess
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def test_stage1_cold_start_demo_script_exits_zero() -> None:
    script = _repo_root() / "scripts" / "stage1-cold-start-demo.sh"
    assert script.is_file()
    proc = subprocess.run(
        ["bash", str(script)],
        cwd=str(_repo_root()),
        capture_output=True,
        text=True,
        timeout=180,
        check=False,
    )
    assert proc.returncode == 0, proc.stdout + "\n" + proc.stderr
