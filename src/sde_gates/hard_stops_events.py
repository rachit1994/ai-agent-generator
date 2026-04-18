"""HS17–HS20 replay and platform-lineage checks (event harness)."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .run_profile import is_coding_only

SUPPORTED_EVENT_CONTRACTS = frozenset({"1.0"})
SUPPORTED_REPLAY_MANIFEST_CONTRACTS = frozenset({"1.0", "sde.replay_manifest.v1"})


def _run_events_path(output_dir: Path) -> Path:
    return output_dir / "event_store" / "run_events.jsonl"


def _replay_manifest_path(output_dir: Path) -> Path:
    return output_dir / "replay_manifest.json"


def _hs17_event_contract(output_dir: Path) -> bool:
    path = _run_events_path(output_dir)
    if not path.is_file():
        return False
    line = path.read_text(encoding="utf-8").splitlines()
    if not line or not line[0].strip():
        return False
    try:
        env = json.loads(line[0])
    except json.JSONDecodeError:
        return False
    ver = env.get("contract_version")
    if ver not in SUPPORTED_EVENT_CONTRACTS:
        return False
    return bool(env.get("event_id") and env.get("aggregate_id") and env.get("occurred_at"))


def _hs18_replay_manifest(output_dir: Path) -> bool:
    man_path = _replay_manifest_path(output_dir)
    traces_path = output_dir / "traces.jsonl"
    if not man_path.is_file() or not traces_path.is_file():
        return False
    try:
        man = json.loads(man_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False
    if man.get("contract_version") not in SUPPORTED_REPLAY_MANIFEST_CONTRACTS:
        return False
    sources = man.get("sources") or []
    if not sources or not isinstance(sources[0], dict):
        return False
    rel = sources[0].get("path")
    expected = sources[0].get("sha256")
    if rel != "traces.jsonl" or not expected:
        return False
    actual = hashlib.sha256(traces_path.read_bytes()).hexdigest()
    return actual == expected and man.get("chain_root") == actual


def _trace_event_suggests_veto(ev: dict[str, Any]) -> bool:
    errs = ev.get("errors") or []
    if isinstance(errs, list) and any("veto" in str(x).lower() or "kill_switch" in str(x).lower() for x in errs):
        return True
    meta = ev.get("metadata") if isinstance(ev.get("metadata"), dict) else {}
    return bool(meta.get("safety_veto") or meta.get("kill_switch_activated"))


def _hs19_kill_switch_lineage(output_dir: Path, events: list[dict[str, Any]]) -> bool:
    ks = output_dir / "kill_switch_state.json"
    if not ks.is_file():
        return False
    try:
        latch = json.loads(ks.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False
    if latch.get("schema_version") != "1.0":
        return False
    vetoish = any(_trace_event_suggests_veto(ev) for ev in events if isinstance(ev, dict))
    if not vetoish:
        return True
    ev_path = _run_events_path(output_dir)
    if not ev_path.is_file():
        return False
    blob = ev_path.read_text(encoding="utf-8").lower()
    return "veto" in blob or "kill_switch" in blob


def _event_command_id(event: dict[str, Any]) -> str | None:
    raw = event.get("command_id")
    if isinstance(raw, str) and raw.strip():
        return raw.strip()
    payload = event.get("payload")
    if isinstance(payload, dict):
        inner = payload.get("command_id")
        if isinstance(inner, str) and inner.strip():
            return inner.strip()
    return None


def _payload_external_mutation_committed(payload: Any) -> bool:
    if not isinstance(payload, dict):
        return False
    return payload.get("external_mutation_committed") is True


def _hs20_no_duplicate_committed_mutations(output_dir: Path) -> bool:
    """HS20: same ``command_id`` must not record two committed external mutations (idempotency)."""
    path = _run_events_path(output_dir)
    if not path.is_file():
        return True
    committed_counts: dict[str, int] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(event, dict):
            continue
        cid = _event_command_id(event)
        if cid is None:
            continue
        if not _payload_external_mutation_committed(event.get("payload")):
            continue
        committed_counts[cid] = committed_counts.get(cid, 0) + 1
        if committed_counts[cid] > 1:
            return False
    return True


def evaluate_event_lineage_hard_stops(output_dir: Path, events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if is_coding_only(output_dir):
        return []
    if not _replay_manifest_path(output_dir).is_file():
        return []
    return [
        {"id": "HS17", "passed": _hs17_event_contract(output_dir), "evidence_ref": "event_store/run_events.jsonl"},
        {"id": "HS18", "passed": _hs18_replay_manifest(output_dir), "evidence_ref": "replay_manifest.json"},
        {"id": "HS19", "passed": _hs19_kill_switch_lineage(output_dir, events), "evidence_ref": "kill_switch_state.json"},
        {"id": "HS20", "passed": _hs20_no_duplicate_committed_mutations(output_dir), "evidence_ref": "event_store/run_events.jsonl"},
    ]
