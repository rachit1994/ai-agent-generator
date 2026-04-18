"""Thread-safe session I/O for parallel project steps (Phase 6)."""

from __future__ import annotations

import threading
from pathlib import Path

_io_locks: dict[str, threading.Lock] = {}
_io_guard = threading.Lock()


def session_io_lock(session_dir: Path) -> threading.Lock:
    """Serialize ``step_runs.jsonl`` / lease heartbeat writes across worker threads."""
    key = str(session_dir.resolve())
    with _io_guard:
        if key not in _io_locks:
            _io_locks[key] = threading.Lock()
        return _io_locks[key]
