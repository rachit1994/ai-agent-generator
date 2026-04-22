from __future__ import annotations

import math

import pytest

from success_criteria.transfer_learning_metrics import (
    build_transfer_learning_metrics,
    validate_transfer_learning_metrics_dict,
    validate_transfer_learning_metrics_path,
)


def test_build_transfer_learning_metrics_is_deterministic() -> None:
    parsed = {"checks": [{"name": "a", "passed": True}]}
    events = [{"stage": "finalize", "score": {"passed": True}}]
    skill_nodes = {"schema_version": "1.0", "nodes": [{"skill_id": "x", "score": 0.8}]}
    one = build_transfer_learning_metrics(run_id="rid-t", parsed=parsed, events=events, skill_nodes=skill_nodes)
    two = build_transfer_learning_metrics(run_id="rid-t", parsed=parsed, events=events, skill_nodes=skill_nodes)
    assert one == two
    assert validate_transfer_learning_metrics_dict(one) == []


def test_transfer_learning_metrics_fail_closed_when_malformed() -> None:
    errs = validate_transfer_learning_metrics_dict({"schema": "x"})
    assert "transfer_learning_metrics_schema" in errs
    assert "transfer_learning_metrics_schema_version" in errs


def test_transfer_learning_metrics_contract_rejects_boolean_metric_types() -> None:
    body = {
        "schema": "sde.transfer_learning_metrics.v1",
        "schema_version": "1.0",
        "run_id": "rid-a",
        "metrics": {
            "transfer_gain_rate": True,
            "negative_transfer_rate": 0.2,
            "retained_success_rate": 0.8,
            "net_transfer_points": 10.0,
            "transfer_efficiency_score": 0.8,
        },
        "evidence": {"traces_ref": "traces.jsonl", "skill_nodes_ref": "capability/skill_nodes.json"},
    }
    errs = validate_transfer_learning_metrics_dict(body)
    assert "transfer_learning_metrics_metric_type:transfer_gain_rate" in errs


def test_transfer_learning_metrics_contract_rejects_out_of_range_rate() -> None:
    body = {
        "schema": "sde.transfer_learning_metrics.v1",
        "schema_version": "1.0",
        "run_id": "rid-a",
        "metrics": {
            "transfer_gain_rate": 1.1,
            "negative_transfer_rate": 0.2,
            "retained_success_rate": 0.8,
            "net_transfer_points": 10.0,
            "transfer_efficiency_score": 0.8,
        },
        "evidence": {"traces_ref": "traces.jsonl", "skill_nodes_ref": "capability/skill_nodes.json"},
    }
    errs = validate_transfer_learning_metrics_dict(body)
    assert "transfer_learning_metrics_metric_range:transfer_gain_rate" in errs


def test_transfer_learning_metrics_contract_rejects_wrong_evidence_refs() -> None:
    body = {
        "schema": "sde.transfer_learning_metrics.v1",
        "schema_version": "1.0",
        "run_id": "rid-a",
        "metrics": {
            "transfer_gain_rate": 0.8,
            "negative_transfer_rate": 0.2,
            "retained_success_rate": 0.8,
            "net_transfer_points": 10.0,
            "transfer_efficiency_score": 0.8,
        },
        "evidence": {"traces_ref": "traces.bad", "skill_nodes_ref": "capability/other.json"},
    }
    errs = validate_transfer_learning_metrics_dict(body)
    assert "transfer_learning_metrics_evidence_traces_ref" in errs
    assert "transfer_learning_metrics_evidence_skill_nodes_ref" in errs


def test_transfer_learning_metrics_path_rejects_malformed_json(tmp_path) -> None:
    path = tmp_path / "transfer_learning_metrics.json"
    path.write_text("{not json", encoding="utf-8")
    assert validate_transfer_learning_metrics_path(path) == ["transfer_learning_metrics_json"]


def test_transfer_learning_metrics_path_rejects_missing_file(tmp_path) -> None:
    assert validate_transfer_learning_metrics_path(tmp_path / "missing.json") == [
        "transfer_learning_metrics_file_missing"
    ]


def test_transfer_learning_metrics_build_expected_values() -> None:
    payload = build_transfer_learning_metrics(
        run_id="rid-values",
        parsed={},
        events=[
            {"stage": "finalize", "score": {"passed": True}},
            {"stage": "finalize", "score": {"passed": False}},
        ],
        skill_nodes={"nodes": [{"score": 0.9}]},
    )
    assert payload == build_transfer_learning_metrics(
        run_id="rid-values",
        parsed={},
        events=[
            {"stage": "finalize", "score": {"passed": True}},
            {"stage": "finalize", "score": {"passed": False}},
        ],
        skill_nodes={"nodes": [{"score": 0.9}]},
    )
    assert payload["metrics"] == {
        "transfer_gain_rate": 0.74,
        "negative_transfer_rate": 0.0,
        "retained_success_rate": 0.5,
        "net_transfer_points": 74.0,
        "transfer_efficiency_score": 0.72,
    }


def test_transfer_learning_metrics_builder_rejects_blank_run_id() -> None:
    try:
        build_transfer_learning_metrics(
            run_id="  ",
            parsed={},
            events=[],
            skill_nodes=None,
        )
    except ValueError as exc:
        assert str(exc) == "transfer_learning_metrics_run_id"
    else:
        raise AssertionError("Expected ValueError for blank run_id")


@pytest.mark.parametrize("run_id", [None, 123])  # type: ignore[list-item]
def test_transfer_learning_metrics_builder_rejects_non_string_run_id(run_id: object) -> None:
    with pytest.raises(ValueError, match="transfer_learning_metrics_run_id"):
        build_transfer_learning_metrics(
            run_id=run_id,  # type: ignore[arg-type]
            parsed={},
            events=[],
            skill_nodes=None,
        )


def test_transfer_learning_metrics_treats_truthy_non_boolean_finalize_pass_as_failed() -> None:
    payload = build_transfer_learning_metrics(
        run_id="rid-truthy-finalize",
        parsed={},
        events=[
            {"stage": "finalize", "score": {"passed": "true"}},
            {"stage": "finalize", "score": {"passed": True}},
        ],
        skill_nodes={"nodes": [{"score": 0.9}]},
    )
    assert payload["metrics"]["retained_success_rate"] == pytest.approx(0.5)


def test_transfer_learning_metrics_contract_rejects_net_transfer_points_mismatch() -> None:
    payload = build_transfer_learning_metrics(
        run_id="rid-net-mismatch",
        parsed={},
        events=[{"stage": "finalize", "score": {"passed": True}}],
        skill_nodes={"nodes": [{"score": 0.9}]},
    )
    payload["metrics"]["net_transfer_points"] = payload["metrics"]["net_transfer_points"] + 1.0
    errs = validate_transfer_learning_metrics_dict(payload)
    assert "transfer_learning_metrics_net_transfer_points_mismatch" in errs


def test_transfer_learning_metrics_contract_rejects_transfer_efficiency_score_mismatch() -> None:
    payload = build_transfer_learning_metrics(
        run_id="rid-efficiency-mismatch",
        parsed={},
        events=[{"stage": "finalize", "score": {"passed": True}}],
        skill_nodes={"nodes": [{"score": 0.9}]},
    )
    payload["metrics"]["transfer_efficiency_score"] = 0.0
    errs = validate_transfer_learning_metrics_dict(payload)
    assert "transfer_learning_metrics_transfer_efficiency_score_mismatch" in errs


@pytest.mark.parametrize(
    "metric_key",
    [
        "transfer_gain_rate",
        "negative_transfer_rate",
        "retained_success_rate",
        "net_transfer_points",
        "transfer_efficiency_score",
    ],
)
def test_transfer_learning_metrics_contract_rejects_non_finite_values(metric_key: str) -> None:
    payload = build_transfer_learning_metrics(
        run_id="rid-non-finite",
        parsed={},
        events=[{"stage": "finalize", "score": {"passed": True}}],
        skill_nodes={"nodes": [{"score": 0.8}]},
    )
    payload["metrics"][metric_key] = math.nan
    errs = validate_transfer_learning_metrics_dict(payload)
    assert f"transfer_learning_metrics_metric_non_finite:{metric_key}" in errs


def test_transfer_learning_metrics_reports_net_transfer_mismatch_with_other_errors() -> None:
    payload = build_transfer_learning_metrics(
        run_id="rid-net-mismatch-with-other-errors",
        parsed={},
        events=[{"stage": "finalize", "score": {"passed": True}}],
        skill_nodes={"nodes": [{"score": 0.9}]},
    )
    payload["metrics"]["net_transfer_points"] += 1.0
    payload["evidence"]["traces_ref"] = "wrong.jsonl"
    errs = validate_transfer_learning_metrics_dict(payload)
    assert "transfer_learning_metrics_evidence_traces_ref" in errs
    assert "transfer_learning_metrics_net_transfer_points_mismatch" in errs


def test_transfer_learning_metrics_reports_efficiency_mismatch_with_other_errors() -> None:
    payload = build_transfer_learning_metrics(
        run_id="rid-efficiency-mismatch-with-other-errors",
        parsed={},
        events=[{"stage": "finalize", "score": {"passed": True}}],
        skill_nodes={"nodes": [{"score": 0.9}]},
    )
    payload["metrics"]["transfer_efficiency_score"] = 0.0
    payload["evidence"]["traces_ref"] = "wrong.jsonl"
    errs = validate_transfer_learning_metrics_dict(payload)
    assert "transfer_learning_metrics_evidence_traces_ref" in errs
    assert "transfer_learning_metrics_transfer_efficiency_score_mismatch" in errs
