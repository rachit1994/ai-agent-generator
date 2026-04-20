"""Repo data suite ``data/medium-hard-sde-suite.jsonl`` stays loadable and curated."""

from __future__ import annotations

from pathlib import Path

from workflow_pipelines.production_pipeline_task_to_promote.benchmark.suite import read_suite


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[5]


def test_medium_hard_sde_suite_jsonl_loads_five_tasks_with_stable_ids() -> None:
    path = _repo_root() / "data" / "medium-hard-sde-suite.jsonl"
    rows = read_suite(str(path))
    assert [r["taskId"] for r in rows] == ["mh-01", "mh-02", "mh-03", "mh-04", "mh-05"]
    assert [r["difficulty"] for r in rows] == [
        "medium",
        "medium",
        "failure-prone",
        "failure-prone",
        "medium",
    ]
    for row in rows:
        checks = row["expectedChecks"]
        assert len(checks) == 1
        assert checks[0].get("name") == "structured_json_contract"
        assert "prompt" in row and len(str(row["prompt"])) > 50
