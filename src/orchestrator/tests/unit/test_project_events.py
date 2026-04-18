"""Phase 11: session_events.jsonl audit log."""

from __future__ import annotations

import json
from pathlib import Path

from orchestrator.api.project_events import SESSION_EVENTS_FILENAME, append_session_event


def test_append_session_event_writes_jsonl(tmp_path: Path) -> None:
    sess = tmp_path / "s"
    sess.mkdir()
    append_session_event(sess, "test_a", {"k": 1})
    append_session_event(sess, "test_b", {})
    path = sess / SESSION_EVENTS_FILENAME
    assert path.is_file()
    lines = path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 2
    a = json.loads(lines[0])
    assert a["event"] == "test_a"
    assert a["payload"] == {"k": 1}
    assert a["schema_version"] == "1.0"
    assert "ts" in a
