from __future__ import annotations

import json
import math

from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.evolution_layer import (
    write_evolution_artifacts,
)
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.memory_artifact_layer import (
    write_memory_artifacts,
)
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.benchmark.promotion_eval_contract import (
    validate_promotion_package_path,
)


def test_capability_model_artifacts_are_valid_and_connected(tmp_path) -> None:
    parsed = {"checks": [{"name": "ok", "passed": True}], "refusal": None}
    events = [{"stage": "finalize", "score": {"passed": True}}]
    nodes = write_memory_artifacts(output_dir=tmp_path, run_id="rid-int", parsed=parsed, events=events)
    write_evolution_artifacts(
        output_dir=tmp_path, run_id="rid-int", parsed=parsed, events=events, skill_nodes=nodes
    )
    assert validate_promotion_package_path(tmp_path / "lifecycle" / "promotion_package.json") == []


def test_capability_model_fail_closed_for_non_boolean_check_status(tmp_path) -> None:
    parsed = {"checks": [{"name": "bad", "passed": "false"}], "refusal": None}
    events = [{"stage": "finalize", "score": {"passed": False}}]
    nodes = write_memory_artifacts(output_dir=tmp_path, run_id="rid-int-fail-closed", parsed=parsed, events=events)
    assert math.isclose(nodes["nodes"][0]["score"], 0.0)
    write_evolution_artifacts(
        output_dir=tmp_path,
        run_id="rid-int-fail-closed",
        parsed=parsed,
        events=events,
        skill_nodes=nodes,
    )
    pkg = json.loads((tmp_path / "lifecycle" / "promotion_package.json").read_text(encoding="utf-8"))
    assert pkg["proposed_stage"] == "junior"
    assert validate_promotion_package_path(tmp_path / "lifecycle" / "promotion_package.json") == []


def test_capability_model_fail_closed_for_non_numeric_node_score(tmp_path) -> None:
    parsed = {"checks": [{"name": "ok", "passed": True}], "refusal": None}
    events = [{"stage": "finalize", "score": {"passed": True}}]
    write_evolution_artifacts(
        output_dir=tmp_path,
        run_id="rid-int-bad-score",
        parsed=parsed,
        events=events,
        skill_nodes={"schema_version": "1.0", "nodes": [{"skill_id": "x", "score": "bad"}]},
    )
    pkg = json.loads((tmp_path / "lifecycle" / "promotion_package.json").read_text(encoding="utf-8"))
    assert pkg["proposed_stage"] == "junior"
    assert validate_promotion_package_path(tmp_path / "lifecycle" / "promotion_package.json") == []


def test_capability_model_fail_closed_for_truthy_non_boolean_finalize_pass(tmp_path) -> None:
    parsed = {"checks": [{"name": "ok", "passed": True}], "refusal": None}
    events = [{"stage": "finalize", "score": {"passed": "true"}}]
    nodes = write_memory_artifacts(output_dir=tmp_path, run_id="rid-int-truthy-finalize", parsed=parsed, events=events)
    assert math.isclose(nodes["nodes"][0]["score"], 0.7)
    assert math.isclose(nodes["nodes"][0]["confidence"], 0.5)
