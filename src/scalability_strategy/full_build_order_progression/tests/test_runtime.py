from __future__ import annotations

from scalability_strategy.full_build_order_progression import (
    build_full_build_order_progression,
    validate_full_build_order_progression_dict,
)


def test_build_full_build_order_progression_is_deterministic() -> None:
    events = [
        {"type": "stage_event", "stage": "planner_doc"},
        {"type": "stage_event", "stage": "planner_prompt"},
        {"type": "stage_event", "stage": "executor"},
        {"type": "stage_event", "stage": "finalize"},
    ]
    one = build_full_build_order_progression(run_id="rid-fbop", mode="guarded_pipeline", orchestration_events=events)
    two = build_full_build_order_progression(run_id="rid-fbop", mode="guarded_pipeline", orchestration_events=events)
    assert one == two
    assert validate_full_build_order_progression_dict(one) == []


def test_validate_full_build_order_progression_fail_closed() -> None:
    errs = validate_full_build_order_progression_dict({"schema": "bad"})
    assert "full_build_order_progression_schema" in errs
    assert "full_build_order_progression_schema_version" in errs


def test_build_full_build_order_progression_requires_allowed_entry_stage() -> None:
    payload = build_full_build_order_progression(
        run_id="rid-fbop",
        mode="guarded_pipeline",
        orchestration_events=[
            {"type": "stage_event", "stage": "planner_prompt"},
            {"type": "stage_event", "stage": "executor"},
            {"type": "stage_event", "stage": "finalize"},
        ],
    )
    assert payload["checks"]["starts_with_allowed_entry_stage"] is False
    assert payload["status"] == "incomplete"


def test_validate_full_build_order_progression_rejects_status_checks_mismatch() -> None:
    payload = build_full_build_order_progression(
        run_id="rid-fbop",
        mode="guarded_pipeline",
        orchestration_events=[
            {"type": "stage_event", "stage": "planner_doc"},
            {"type": "stage_event", "stage": "planner_prompt"},
            {"type": "stage_event", "stage": "executor"},
            {"type": "stage_event", "stage": "finalize"},
        ],
    )
    payload["status"] = "out_of_order"
    errs = validate_full_build_order_progression_dict(payload)
    assert "full_build_order_progression_status_checks_mismatch" in errs


def test_validate_full_build_order_progression_rejects_summary_sequence_mismatch() -> None:
    payload = build_full_build_order_progression(
        run_id="rid-fbop",
        mode="guarded_pipeline",
        orchestration_events=[
            {"type": "stage_event", "stage": "planner_doc"},
            {"type": "stage_event", "stage": "planner_prompt"},
            {"type": "stage_event", "stage": "executor"},
            {"type": "stage_event", "stage": "finalize"},
        ],
    )
    payload["summary"]["required_stage_present_count"] = 0
    errs = validate_full_build_order_progression_dict(payload)
    assert "full_build_order_progression_summary_sequence_mismatch" in errs


def test_validate_full_build_order_progression_rejects_evidence_ref_mismatch() -> None:
    payload = build_full_build_order_progression(
        run_id="rid-fbop",
        mode="guarded_pipeline",
        orchestration_events=[
            {"type": "stage_event", "stage": "planner_doc"},
            {"type": "stage_event", "stage": "planner_prompt"},
            {"type": "stage_event", "stage": "executor"},
            {"type": "stage_event", "stage": "finalize"},
        ],
    )
    payload["evidence"]["orchestration_ref"] = "/tmp/orchestration.jsonl"
    errs = validate_full_build_order_progression_dict(payload)
    assert "full_build_order_progression_evidence_ref:orchestration_ref" in errs


def test_validate_full_build_order_progression_rejects_other_evidence_ref_mismatches() -> None:
    payload = build_full_build_order_progression(
        run_id="rid-fbop",
        mode="guarded_pipeline",
        orchestration_events=[
            {"type": "stage_event", "stage": "planner_doc"},
            {"type": "stage_event", "stage": "planner_prompt"},
            {"type": "stage_event", "stage": "executor"},
            {"type": "stage_event", "stage": "finalize"},
        ],
    )
    payload["evidence"]["run_manifest_ref"] = "../run-manifest.json"
    payload["evidence"]["progression_ref"] = "strategy/other.json"
    errs = validate_full_build_order_progression_dict(payload)
    assert "full_build_order_progression_evidence_ref:run_manifest_ref" in errs
    assert "full_build_order_progression_evidence_ref:progression_ref" in errs


def test_validate_full_build_order_progression_rejects_order_score_mismatch() -> None:
    payload = build_full_build_order_progression(
        run_id="rid-fbop",
        mode="guarded_pipeline",
        orchestration_events=[
            {"type": "stage_event", "stage": "planner_doc"},
            {"type": "stage_event", "stage": "planner_prompt"},
            {"type": "stage_event", "stage": "executor"},
            {"type": "stage_event", "stage": "finalize"},
        ],
    )
    payload["summary"]["order_score"] = 0.4
    errs = validate_full_build_order_progression_dict(payload)
    assert "full_build_order_progression_order_score_mismatch" in errs


def test_validate_full_build_order_progression_rejects_baseline_entry_stage_mismatch() -> None:
    payload = build_full_build_order_progression(
        run_id="rid-fbop",
        mode="baseline",
        orchestration_events=[
            {"type": "stage_event", "stage": "executor"},
            {"type": "stage_event", "stage": "finalize"},
        ],
    )
    payload["stage_sequence"] = ["planner_doc", "finalize"]
    payload["checks"]["starts_with_allowed_entry_stage"] = True
    payload["checks"]["required_stages_present"] = False
    payload["status"] = "incomplete"
    payload["summary"]["observed_stage_count"] = 2
    payload["summary"]["distinct_stage_count"] = 2
    payload["summary"]["required_stage_count"] = 2
    payload["summary"]["required_stage_present_count"] = 1
    payload["summary"]["order_score"] = 0.8
    errs = validate_full_build_order_progression_dict(payload)
    assert "full_build_order_progression_mode_entry_stage_mismatch" in errs


def test_validate_full_build_order_progression_accepts_valid_baseline_entry_stage() -> None:
    payload = build_full_build_order_progression(
        run_id="rid-fbop",
        mode="baseline",
        orchestration_events=[
            {"type": "stage_event", "stage": "executor"},
            {"type": "stage_event", "stage": "finalize"},
        ],
    )
    errs = validate_full_build_order_progression_dict(payload)
    assert "full_build_order_progression_mode_entry_stage_mismatch" not in errs

