"""Event lineage: replay manifest, minimal event_store envelope, kill-switch latch file."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from sde_foundations.storage import ensure_dir, write_json
from sde_gates.time_util import iso_now

REPLAY_MANIFEST_CONTRACT = "sde.replay_manifest.v1"


def write_event_lineage_artifacts(*, output_dir: Path, run_id: str) -> None:
    """Persist replay manifest and a single event envelope referencing ``traces.jsonl``."""
    traces_path = output_dir / "traces.jsonl"
    if not traces_path.is_file():
        return
    raw = traces_path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    text = raw.decode("utf-8")
    n = len([ln for ln in text.splitlines() if ln.strip()])
    write_json(
        output_dir / "replay_manifest.json",
        {
            "schema_version": "1.0",
            "run_id": run_id,
            "contract_version": REPLAY_MANIFEST_CONTRACT,
            "window": {"first_line": 1, "last_line": max(n, 1)},
            "sources": [{"path": "traces.jsonl", "sha256": digest}],
            "chain_root": digest,
            "projection_version": "1.0",
            "passed": True,
            "built_at": iso_now(),
        },
    )
    ev_dir = output_dir / "event_store"
    ensure_dir(ev_dir)
    event_id = f"evt-{run_id}-traces"
    envelope = {
        "event_id": event_id,
        "aggregate_id": run_id,
        "command_id": f"cmd-{run_id}-traces-ref",
        "causation_id": None,
        "contract_version": "1.0",
        "payload": {
            "type": "delivery_trace_reference",
            "path": "traces.jsonl",
            "sha256": digest,
        },
        "occurred_at": iso_now(),
    }
    (ev_dir / "run_events.jsonl").write_text(json.dumps(envelope) + "\n", encoding="utf-8")
    write_json(
        output_dir / "kill_switch_state.json",
        {
            "schema_version": "1.0",
            "latched": False,
            "updated_at": iso_now(),
            "last_event_id": event_id,
        },
    )
