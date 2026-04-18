"""Phase 11: append-only session event log for driver auditability."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from sde_foundations.storage import ensure_dir
from sde_gates.time_util import iso_now

SESSION_EVENTS_FILENAME = "session_events.jsonl"
SESSION_EVENTS_SCHEMA_VERSION = "1.0"


def append_session_event(
    session_dir: Path,
    event: str,
    payload: dict[str, Any] | None = None,
) -> None:
    """Append one JSON line to ``session_events.jsonl`` (best-effort; never raises)."""
    try:
        ensure_dir(session_dir)
        path = session_dir / SESSION_EVENTS_FILENAME
        row: dict[str, Any] = {
            "schema_version": SESSION_EVENTS_SCHEMA_VERSION,
            "ts": iso_now(),
            "event": event,
            "payload": payload or {},
        }
        with path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(row, separators=(",", ":")) + "\n")
    except OSError:
        return
