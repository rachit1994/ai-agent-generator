from __future__ import annotations

import json
from pathlib import Path

from guardrails_and_safety.risk_budgets_permission_matrix.risk_budgets.hard_stops_events import evaluate_event_lineage_hard_stops


def test_hs18_fails_when_traces_mutated_after_manifest(tmp_path: Path) -> None:
    run_id = "r-test"
    traces = tmp_path / "traces.jsonl"
    traces.write_text('{"stage":"finalize"}\n', encoding="utf-8")
    digest = __import__("hashlib").sha256(traces.read_bytes()).hexdigest()
    (tmp_path / "replay_manifest.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "run_id": run_id,
                "contract_version": "sde.replay_manifest.v1",
                "sources": [{"path": "traces.jsonl", "sha256": digest}],
                "chain_root": digest,
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / "event_store").mkdir()
    (tmp_path / "event_store" / "run_events.jsonl").write_text(
        json.dumps(
            {
                "event_id": "e1",
                "aggregate_id": run_id,
                "causation_id": None,
                "contract_version": "1.0",
                "payload": {},
                "occurred_at": "2026-01-01T00:00:00+00:00",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (tmp_path / "kill_switch_state.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "latched": False,
                "updated_at": "2026-01-01T00:00:00+00:00",
                "last_event_id": "e1",
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / "summary.json").write_text(json.dumps({"run_class": "full"}), encoding="utf-8")
    hs_before = evaluate_event_lineage_hard_stops(tmp_path, [])
    assert all(h["passed"] for h in hs_before)

    traces.write_text('{"stage":"finalize","tampered":true}\n', encoding="utf-8")
    hs_after = evaluate_event_lineage_hard_stops(tmp_path, [])
    by_id = {h["id"]: h["passed"] for h in hs_after}
    assert by_id["HS18"] is False
    assert by_id["HS17"] is True


def test_event_lineage_hard_stops_skipped_for_coding_only_run_class(tmp_path: Path) -> None:
    (tmp_path / "replay_manifest.json").write_text("{}", encoding="utf-8")
    (tmp_path / "summary.json").write_text(json.dumps({"run_class": "coding_only"}), encoding="utf-8")
    assert evaluate_event_lineage_hard_stops(tmp_path, []) == []


def test_hs20_fails_when_same_command_id_commits_two_external_mutations(tmp_path: Path) -> None:
    run_id = "r-hs20"
    traces = tmp_path / "traces.jsonl"
    traces.write_text("{}\n", encoding="utf-8")
    digest = __import__("hashlib").sha256(traces.read_bytes()).hexdigest()
    (tmp_path / "replay_manifest.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "run_id": run_id,
                "contract_version": "sde.replay_manifest.v1",
                "sources": [{"path": "traces.jsonl", "sha256": digest}],
                "chain_root": digest,
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / "event_store").mkdir()
    dup_cmd = "cmd-pay-001"
    line_a = {
        "event_id": "e-a",
        "aggregate_id": run_id,
        "command_id": dup_cmd,
        "causation_id": None,
        "contract_version": "1.0",
        "payload": {"external_mutation_committed": True, "detail": "first"},
        "occurred_at": "2026-01-01T00:00:00+00:00",
    }
    line_b = {
        "event_id": "e-b",
        "aggregate_id": run_id,
        "command_id": dup_cmd,
        "causation_id": None,
        "contract_version": "1.0",
        "payload": {"external_mutation_committed": True, "detail": "second"},
        "occurred_at": "2026-01-01T00:00:01+00:00",
    }
    (tmp_path / "event_store" / "run_events.jsonl").write_text(
        json.dumps(line_a) + "\n" + json.dumps(line_b) + "\n",
        encoding="utf-8",
    )
    (tmp_path / "kill_switch_state.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "latched": False,
                "updated_at": "2026-01-01T00:00:00+00:00",
                "last_event_id": "e-b",
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / "summary.json").write_text(json.dumps({"run_class": "full"}), encoding="utf-8")
    by_id = {h["id"]: h for h in evaluate_event_lineage_hard_stops(tmp_path, [])}
    assert by_id["HS20"]["passed"] is False
    assert by_id["HS17"]["passed"] is True


def test_hs20_passes_when_command_id_repeated_without_committed_mutation(tmp_path: Path) -> None:
    run_id = "r-hs20b"
    traces = tmp_path / "traces.jsonl"
    traces.write_text("{}\n", encoding="utf-8")
    digest = __import__("hashlib").sha256(traces.read_bytes()).hexdigest()
    (tmp_path / "replay_manifest.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "run_id": run_id,
                "contract_version": "sde.replay_manifest.v1",
                "sources": [{"path": "traces.jsonl", "sha256": digest}],
                "chain_root": digest,
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / "event_store").mkdir()
    dup_cmd = "cmd-idem-1"
    body = (
        json.dumps(
            {
                "event_id": "e1",
                "aggregate_id": run_id,
                "command_id": dup_cmd,
                "contract_version": "1.0",
                "payload": {"external_mutation_committed": False},
                "occurred_at": "2026-01-01T00:00:00+00:00",
            }
        )
        + "\n"
        + json.dumps(
            {
                "event_id": "e2",
                "aggregate_id": run_id,
                "command_id": dup_cmd,
                "contract_version": "1.0",
                "payload": {"external_mutation_committed": True},
                "occurred_at": "2026-01-01T00:00:01+00:00",
            }
        )
        + "\n"
    )
    (tmp_path / "event_store" / "run_events.jsonl").write_text(body, encoding="utf-8")
    (tmp_path / "kill_switch_state.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "latched": False,
                "updated_at": "2026-01-01T00:00:00+00:00",
                "last_event_id": "e2",
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / "summary.json").write_text(json.dumps({"run_class": "full"}), encoding="utf-8")
    by_id = {h["id"]: h["passed"] for h in evaluate_event_lineage_hard_stops(tmp_path, [])}
    assert by_id["HS20"] is True
