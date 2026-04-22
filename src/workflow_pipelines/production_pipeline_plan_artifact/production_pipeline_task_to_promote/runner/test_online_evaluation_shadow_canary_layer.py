from __future__ import annotations

import json
from pathlib import Path

import pytest

from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.online_evaluation_shadow_canary_layer import (
    write_online_evaluation_shadow_canary_artifact,
)


def _write_records(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(row) for row in rows), encoding="utf-8")


def test_runner_layer_writes_contract_valid_payload(tmp_path: Path) -> None:
    output_dir = tmp_path / "run"
    _write_records(
        output_dir / "learning" / "online_eval_records.jsonl",
        [
            {
                "request_id": f"req-{idx}",
                "cohort": "shadow" if idx % 2 else "canary",
                "baseline_latency_ms": 10.0 + idx,
                "candidate_latency_ms": 11.0 + idx,
                "baseline_outcome": True,
                "candidate_outcome": True,
                "baseline_quality": 0.6,
                "candidate_quality": 0.7,
            }
            for idx in range(6)
        ],
    )
    payload = write_online_evaluation_shadow_canary_artifact(output_dir=output_dir, run_id="rid")
    assert payload["schema"] == "sde.online_evaluation_shadow_canary.v1"
    assert payload["evidence"]["online_eval_records_ref"] == "learning/online_eval_records.jsonl"


def test_runner_layer_fails_closed_when_records_missing(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="online_evaluation_shadow_canary_contract:online_eval_records_missing"):
        write_online_evaluation_shadow_canary_artifact(output_dir=tmp_path / "run", run_id="rid")


def test_runner_layer_fails_closed_for_malformed_jsonl(tmp_path: Path) -> None:
    records_path = tmp_path / "run" / "learning" / "online_eval_records.jsonl"
    records_path.parent.mkdir(parents=True, exist_ok=True)
    records_path.write_text("{bad json", encoding="utf-8")
    with pytest.raises(ValueError, match="online_evaluation_shadow_canary_contract:online_eval_records_jsonl:1"):
        write_online_evaluation_shadow_canary_artifact(output_dir=tmp_path / "run", run_id="rid")


def test_runner_layer_ignores_malformed_optional_canary_report(tmp_path: Path) -> None:
    output_dir = tmp_path / "run"
    _write_records(
        output_dir / "learning" / "online_eval_records.jsonl",
        [
            {
                "request_id": f"req-{idx}",
                "cohort": "shadow" if idx % 2 else "canary",
                "baseline_latency_ms": 10.0 + idx,
                "candidate_latency_ms": 11.0 + idx,
                "baseline_outcome": True,
                "candidate_outcome": True,
                "baseline_quality": 0.6,
                "candidate_quality": 0.7,
            }
            for idx in range(6)
        ],
    )
    (output_dir / "learning" / "canary_report.json").write_text("{bad json", encoding="utf-8")
    payload = write_online_evaluation_shadow_canary_artifact(output_dir=output_dir, run_id="rid")
    assert payload["schema"] == "sde.online_evaluation_shadow_canary.v1"


def test_runner_layer_ignores_unreadable_optional_canary_report(tmp_path: Path) -> None:
    output_dir = tmp_path / "run"
    _write_records(
        output_dir / "learning" / "online_eval_records.jsonl",
        [
            {
                "request_id": f"req-{idx}",
                "cohort": "shadow" if idx % 2 else "canary",
                "baseline_latency_ms": 10.0 + idx,
                "candidate_latency_ms": 11.0 + idx,
                "baseline_outcome": True,
                "candidate_outcome": True,
                "baseline_quality": 0.6,
                "candidate_quality": 0.7,
            }
            for idx in range(6)
        ],
    )
    canary_path = output_dir / "learning" / "canary_report.json"
    canary_path.parent.mkdir(parents=True, exist_ok=True)
    canary_path.write_bytes(b"\xff\xfe\xfd")
    payload = write_online_evaluation_shadow_canary_artifact(output_dir=output_dir, run_id="rid")
    assert payload["schema"] == "sde.online_evaluation_shadow_canary.v1"
