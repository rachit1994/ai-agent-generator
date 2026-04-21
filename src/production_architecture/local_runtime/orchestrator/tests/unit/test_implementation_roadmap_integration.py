from __future__ import annotations

import json
from pathlib import Path

from implementation_roadmap.implementation_roadmap import validate_implementation_roadmap_path
from production_architecture.storage.storage.storage import ensure_dir, write_json
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.implementation_roadmap_layer import (
    write_implementation_roadmap_artifact,
)


def test_implementation_roadmap_written_and_valid(tmp_path: Path) -> None:
    run_id = "run-implementation-roadmap"
    run_dir = tmp_path / "runs" / run_id
    ensure_dir(run_dir / "program")
    write_json(run_dir / "summary.json", {"balanced_gates": {"validation_ready": True}})
    write_json(run_dir / "review.json", {"status": "completed_review_pass"})
    write_json(run_dir / "program" / "production_readiness.json", {"status": "ready"})
    write_json(run_dir / "program" / "topology_and_repository_layout.json", {"status": "ready"})
    write_json(run_dir / "program" / "consolidated_improvements.json", {"status": "ready"})
    write_json(
        run_dir / "program" / "closure_security_reliability_scalability_plans.json",
        {"status": "ready"},
    )
    payload = write_implementation_roadmap_artifact(
        output_dir=run_dir, run_id=run_id, mode="guarded_pipeline"
    )
    assert payload["run_id"] == run_id
    assert validate_implementation_roadmap_path(run_dir / "program" / "implementation_roadmap.json") == []
    body = json.loads((run_dir / "program" / "implementation_roadmap.json").read_text(encoding="utf-8"))
    assert body["status"] in {"on_track", "at_risk"}
