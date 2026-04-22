from __future__ import annotations

from core_components.evaluation_service import (
    build_evaluation_service,
    execute_evaluation_service_runtime,
    validate_evaluation_service_dict,
)


def test_build_evaluation_service_is_deterministic() -> None:
    summary = {"metrics": {"passRate": 1.0}}
    online_eval = {"status": "ok"}
    promotion_eval = {"status": "promote"}
    one = build_evaluation_service(
        run_id="rid-eval",
        summary=summary,
        online_eval=online_eval,
        promotion_eval=promotion_eval,
    )
    two = build_evaluation_service(
        run_id="rid-eval",
        summary=summary,
        online_eval=online_eval,
        promotion_eval=promotion_eval,
    )
    assert one == two
    assert one["status"] == "ready"
    assert validate_evaluation_service_dict(one) == []
    assert one["execution"]["payloads_processed"] == 3


def test_validate_evaluation_service_fail_closed() -> None:
    errs = validate_evaluation_service_dict({"schema": "bad"})
    assert "evaluation_service_schema" in errs
    assert "evaluation_service_schema_version" in errs


def test_build_evaluation_service_treats_missing_status_payloads_as_not_ready() -> None:
    payload = build_evaluation_service(
        run_id="rid-eval",
        summary={"metrics": {"passRate": 1.0}},
        online_eval={"result": "ok"},
        promotion_eval={"result": "promote"},
    )
    assert payload["status"] == "degraded"
    assert payload["metrics"]["has_online_eval"] is False
    assert payload["metrics"]["has_promotion_eval"] is False


def test_validate_evaluation_service_rejects_status_metrics_mismatch() -> None:
    payload = build_evaluation_service(
        run_id="rid-eval",
        summary={"metrics": {"passRate": 1.0}},
        online_eval={"status": "finished"},
        promotion_eval={"status": "promote"},
    )
    payload["status"] = "degraded"
    errs = validate_evaluation_service_dict(payload)
    assert "evaluation_service_status_metrics_mismatch" in errs


def test_build_evaluation_service_accepts_decision_only_eval_payloads() -> None:
    payload = build_evaluation_service(
        run_id="rid-eval-decision",
        summary={"metrics": {"passRate": 1.0}},
        online_eval={"decision": "hold"},
        promotion_eval={"decision": "promote"},
    )
    assert payload["status"] == "ready"


def test_validate_evaluation_service_rejects_invalid_evidence_refs() -> None:
    payload = build_evaluation_service(
        run_id="rid-eval-evidence",
        summary={"metrics": {"passRate": 1.0}},
        online_eval={"status": "finished"},
        promotion_eval={"status": "promote"},
    )
    payload["evidence"]["online_eval_ref"] = "../learning/online_evaluation_shadow_canary.json"
    errs = validate_evaluation_service_dict(payload)
    assert "evaluation_service_evidence_ref:online_eval_ref" in errs


def test_validate_evaluation_service_rejects_non_object_evidence() -> None:
    payload = build_evaluation_service(
        run_id="rid-eval-evidence-shape",
        summary={"metrics": {"passRate": 1.0}},
        online_eval={"status": "finished"},
        promotion_eval={"status": "promote"},
    )
    payload["evidence"] = "bad"
    errs = validate_evaluation_service_dict(payload)
    assert "evaluation_service_evidence" in errs


def test_validate_evaluation_service_rejects_absolute_evidence_ref() -> None:
    payload = build_evaluation_service(
        run_id="rid-eval-evidence-absolute",
        summary={"metrics": {"passRate": 1.0}},
        online_eval={"status": "finished"},
        promotion_eval={"status": "promote"},
    )
    payload["evidence"]["summary_ref"] = "/tmp/summary.json"
    errs = validate_evaluation_service_dict(payload)
    assert "evaluation_service_evidence_ref:summary_ref" in errs


def test_execute_evaluation_service_runtime_detects_missing_sources() -> None:
    execution = execute_evaluation_service_runtime(
        summary={"metrics": {"passRate": 1.0}},
        online_eval={"result": "ok"},
        promotion_eval={"decision": "promote"},
    )
    assert execution["payloads_processed"] == 3
    assert execution["missing_signal_sources"] == ["online_eval"]
    assert execution["summary_metrics_present"] is True
    assert execution["malformed_payloads"] == 0
