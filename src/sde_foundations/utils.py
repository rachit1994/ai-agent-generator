from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


def outputs_base() -> Path:
    """Directory that contains ``runs/<run-id>/`` (repo ``outputs/`` when inside this project).

    Resolution order:
    1. ``SDE_OUTPUTS_ROOT`` if set (must be an absolute or user-expandable path to the ``outputs`` dir).
    2. Nearest ancestor of :func:`os.getcwd` that contains ``pyproject.toml``, then ``<that-dir>/outputs``.
    3. ``Path.cwd() / "outputs"`` (e.g. hermetic tests with no project marker in cwd chain).
    """

    raw = os.environ.get("SDE_OUTPUTS_ROOT", "").strip()
    if raw:
        return Path(raw).expanduser().resolve()
    cwd = Path.cwd().resolve()
    for directory in (cwd, *cwd.parents):
        if (directory / "pyproject.toml").is_file():
            return directory / "outputs"
    return cwd / "outputs"


def create_run_id() -> str:
    stamp = datetime.now(timezone.utc).isoformat().replace(":", "-").replace(".", "-")
    return f"{stamp}-{uuid4().hex[:8]}"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def ms_to_iso(epoch_ms: int) -> str:
    return datetime.fromtimestamp(epoch_ms / 1000.0, tz=timezone.utc).isoformat()
