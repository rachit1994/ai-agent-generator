"""§13.D — shadow/canary artifact contract (**HS28** / ``canary_report.json``)."""

from __future__ import annotations

from pathlib import Path

from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.benchmark.online_eval_shadow_contract import (
    ONLINE_EVAL_SHADOW_CONTRACT,
    validate_canary_report_dict,
    validate_canary_report_path,
)
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.evolution_layer import (
    write_evolution_artifacts,
)


def test_online_eval_shadow_contract_id() -> None:
    assert ONLINE_EVAL_SHADOW_CONTRACT == "sde.online_eval_shadow.v1"


def test_validate_canary_report_dict_hs28_ok() -> None:
    body = {
        "schema_version": "1.0",
        "shadow_metrics": {"latency_p95_ms": 0},
        "promote": False,
        "recorded_at": "2026-01-01T00:00:00Z",
    }
    assert validate_canary_report_dict(body) == []


def test_validate_canary_report_dict_not_object() -> None:
    assert validate_canary_report_dict([]) == ["online_eval_shadow_not_object"]


def test_validate_canary_report_dict_bad_shadow_metrics() -> None:
    body = {
        "schema_version": "1.0",
        "shadow_metrics": "nope",
        "promote": True,
        "recorded_at": "t",
    }
    assert "online_eval_shadow_metrics" in validate_canary_report_dict(body)


def test_validate_canary_report_dict_requires_schema_version_value() -> None:
    body = {
        "schema_version": "2.0",
        "shadow_metrics": {"latency_p95_ms": 1},
        "promote": True,
        "recorded_at": "2026-01-01T00:00:00Z",
    }
    assert "online_eval_shadow_schema_version_value" in validate_canary_report_dict(body)


def test_validate_canary_report_dict_promote_not_bool() -> None:
    body = {
        "schema_version": "1.0",
        "shadow_metrics": {},
        "promote": "yes",
        "recorded_at": "t",
    }
    assert "online_eval_shadow_promote_type" in validate_canary_report_dict(body)


def test_validate_canary_report_dict_promote_missing() -> None:
    body = {
        "schema_version": "1.0",
        "shadow_metrics": {"latency_p95_ms": 0},
        "recorded_at": "2026-01-01T00:00:00Z",
    }
    assert "online_eval_shadow_promote_missing" in validate_canary_report_dict(body)


def test_validate_canary_report_dict_recorded_at_missing() -> None:
    body = {
        "schema_version": "1.0",
        "shadow_metrics": {"latency_p95_ms": 0},
        "promote": True,
    }
    assert "online_eval_shadow_recorded_at" in validate_canary_report_dict(body)


def test_validate_canary_report_dict_requires_latency_metric() -> None:
    body = {
        "schema_version": "1.0",
        "shadow_metrics": {},
        "promote": True,
        "recorded_at": "2026-01-01T00:00:00Z",
    }
    assert "online_eval_shadow_metrics_latency_p95_missing" in validate_canary_report_dict(body)


def test_validate_canary_report_dict_rejects_latency_type_and_range() -> None:
    body_type = {
        "schema_version": "1.0",
        "shadow_metrics": {"latency_p95_ms": True},
        "promote": True,
        "recorded_at": "2026-01-01T00:00:00Z",
    }
    body_range = {
        "schema_version": "1.0",
        "shadow_metrics": {"latency_p95_ms": -1},
        "promote": True,
        "recorded_at": "2026-01-01T00:00:00Z",
    }
    assert "online_eval_shadow_metrics_latency_p95_type" in validate_canary_report_dict(body_type)
    assert "online_eval_shadow_metrics_latency_p95_range" in validate_canary_report_dict(body_range)


def test_validate_canary_report_dict_accepts_camel_case_aliases() -> None:
    body = {
        "schemaVersion": "1.0",
        "shadowMetrics": {"latency_p95_ms": 0},
        "promote": False,
        "recordedAt": "2026-01-01T00:00:00Z",
    }
    assert validate_canary_report_dict(body) == []


def test_validate_canary_report_path_missing(tmp_path: Path) -> None:
    assert validate_canary_report_path(tmp_path / "nope.json") == ["online_eval_shadow_file_missing"]


def test_validate_canary_report_path_bad_json(tmp_path: Path) -> None:
    p = tmp_path / "c.json"
    p.write_text("{", encoding="utf-8")
    assert validate_canary_report_path(p) == ["online_eval_shadow_json"]


def test_validate_canary_report_path_non_object_json(tmp_path: Path) -> None:
    p = tmp_path / "c.json"
    p.write_text("[]", encoding="utf-8")
    assert validate_canary_report_path(p) == ["online_eval_shadow_not_object"]


def test_write_evolution_artifacts_writes_valid_canary_report(tmp_path: Path) -> None:
    write_evolution_artifacts(output_dir=tmp_path, run_id="rid-shadow")
    cr = tmp_path / "learning" / "canary_report.json"
    assert validate_canary_report_path(cr) == []
