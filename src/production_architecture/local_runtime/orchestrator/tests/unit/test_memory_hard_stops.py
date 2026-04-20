from __future__ import annotations

import json
from pathlib import Path

from guardrails_and_safety.risk_budgets_permission_matrix.risk_budgets.hard_stops_memory import evaluate_memory_hard_stops


def _minimal_memory_tree(
    tmp_path: Path,
    *,
    chunk_provenance_id: str = "evt-r-traces",
    envelope_event_id: str = "evt-r-traces",
) -> None:
    (tmp_path / "memory").mkdir(parents=True)
    (tmp_path / "event_store").mkdir(parents=True)
    (tmp_path / "capability").mkdir(parents=True)
    (tmp_path / "memory" / "retrieval_bundle.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "run_id": "r",
                "chunks": [{"text": "x", "provenance_id": chunk_provenance_id, "confidence": 1.0}],
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / "memory" / "quarantine.jsonl").write_text("", encoding="utf-8")
    (tmp_path / "memory" / "quality_metrics.json").write_text(
        json.dumps({"schema_version": "1.0", "contradiction_rate": 0.0}),
        encoding="utf-8",
    )
    (tmp_path / "capability" / "skill_nodes.json").write_text(
        json.dumps({"schema_version": "1.0", "nodes": []}),
        encoding="utf-8",
    )
    (tmp_path / "event_store" / "run_events.jsonl").write_text(
        json.dumps(
            {
                "event_id": envelope_event_id,
                "aggregate_id": "r",
                "causation_id": None,
                "contract_version": "1.0",
                "payload": {},
                "occurred_at": "2026-01-01T00:00:00+00:00",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (tmp_path / "summary.json").write_text(json.dumps({"run_class": "full"}), encoding="utf-8")


def test_hs22_fails_on_unresolved_quarantine_row(tmp_path: Path) -> None:
    _minimal_memory_tree(tmp_path)
    (tmp_path / "memory" / "quarantine.jsonl").write_text(
        json.dumps({"id": "c1", "status": "unresolved_contradiction"}) + "\n",
        encoding="utf-8",
    )
    hs = {h["id"]: h["passed"] for h in evaluate_memory_hard_stops(tmp_path)}
    assert hs["HS22"] is False
    assert hs["HS21"] is True


def test_hs21_fails_when_provenance_not_in_event_store(tmp_path: Path) -> None:
    _minimal_memory_tree(tmp_path, chunk_provenance_id="wrong-id", envelope_event_id="evt-r-traces")
    hs = {h["id"]: h["passed"] for h in evaluate_memory_hard_stops(tmp_path)}
    assert hs["HS21"] is False


def test_memory_hard_stops_skipped_when_coding_only(tmp_path: Path) -> None:
    _minimal_memory_tree(tmp_path)
    (tmp_path / "summary.json").write_text(json.dumps({"run_class": "coding_only"}), encoding="utf-8")
    assert evaluate_memory_hard_stops(tmp_path) == []
