"""Memory harness: retrieval bundle, quarantine log, quality metrics, skill surface."""

from __future__ import annotations

from pathlib import Path

from production_architecture.storage.storage.storage import ensure_dir, write_json
from guardrails_and_safety.risk_budgets_permission_matrix.time_and_budget.time_util import iso_now


def write_memory_artifacts(*, output_dir: Path, run_id: str) -> None:
    """Emit minimal memory contracts (local SDE default-on memory path)."""
    mem = output_dir / "memory"
    ensure_dir(mem)
    event_id = f"evt-{run_id}-traces"
    write_json(
        mem / "retrieval_bundle.json",
        {
            "schema_version": "1.0",
            "run_id": run_id,
            "chunks": [
                {
                    "text": "harness_episodic_stub",
                    "provenance_id": event_id,
                    "confidence": 0.5,
                    "memory_type": "episodic",
                }
            ],
        },
    )
    (mem / "quarantine.jsonl").write_text("", encoding="utf-8")
    write_json(
        mem / "quality_metrics.json",
        {
            "schema_version": "1.0",
            "contradiction_rate": 0.0,
            "staleness_p95_hours": 0.0,
            "updated_at": iso_now(),
        },
    )
    cap = output_dir / "capability"
    ensure_dir(cap)
    write_json(cap / "skill_nodes.json", {"schema_version": "1.0", "nodes": []})
