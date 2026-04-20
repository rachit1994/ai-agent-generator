from __future__ import annotations

import json
from pathlib import Path

from guardrails_and_safety.risk_budgets_permission_matrix.risk_budgets.hard_stops_evolution import evaluate_evolution_hard_stops
from guardrails_and_safety.risk_budgets_permission_matrix.risk_budgets.hard_stops_organization import evaluate_organization_hard_stops


def test_hs25_fails_when_causal_closure_incomplete(tmp_path: Path) -> None:
    (tmp_path / "learning").mkdir()
    (tmp_path / "learning" / "reflection_bundle.json").write_text(
        json.dumps(
            {
                "causal_closure_checklist": {
                    "failure_class": True,
                    "root_cause_evidence": False,
                    "intervention_mapped": True,
                    "post_fix_verified": True,
                }
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / "summary.json").write_text(json.dumps({"run_class": "full"}), encoding="utf-8")
    hs = {h["id"]: h["passed"] for h in evaluate_evolution_hard_stops(tmp_path)}
    assert hs["HS25"] is False


def test_hs26_fails_closed_when_promotion_package_not_object(tmp_path: Path) -> None:
    (tmp_path / "learning").mkdir()
    (tmp_path / "learning" / "reflection_bundle.json").write_text(
        json.dumps({"causal_closure_checklist": {"failure_class": True, "root_cause_evidence": True, "intervention_mapped": True, "post_fix_verified": True}}),
        encoding="utf-8",
    )
    (tmp_path / "lifecycle").mkdir()
    (tmp_path / "lifecycle" / "promotion_package.json").write_text("[]", encoding="utf-8")
    (tmp_path / "practice").mkdir()
    (tmp_path / "practice" / "task_spec.json").write_text(json.dumps({"gap_detection_ref": "learning/reflection_bundle.json"}), encoding="utf-8")
    (tmp_path / "practice" / "evaluation_result.json").write_text(json.dumps({"passed": True}), encoding="utf-8")
    (tmp_path / "learning" / "canary_report.json").write_text(
        json.dumps({"shadow_metrics": {"latency_p95_ms": 0}, "promote": True}),
        encoding="utf-8",
    )
    (tmp_path / "summary.json").write_text(json.dumps({"run_class": "full"}), encoding="utf-8")
    hs = {h["id"]: h["passed"] for h in evaluate_evolution_hard_stops(tmp_path)}
    assert hs["HS26"] is False


def test_hs26_passes_with_camel_case_promotion_package(tmp_path: Path) -> None:
    (tmp_path / "learning").mkdir()
    (tmp_path / "learning" / "reflection_bundle.json").write_text(
        json.dumps({"causal_closure_checklist": {"failure_class": True, "root_cause_evidence": True, "intervention_mapped": True, "post_fix_verified": True}}),
        encoding="utf-8",
    )
    (tmp_path / "lifecycle").mkdir()
    (tmp_path / "lifecycle" / "promotion_package.json").write_text(
        json.dumps(
            {
                "schemaVersion": "1.0",
                "aggregateId": "run-1",
                "currentStage": "junior",
                "proposedStage": "junior",
                "independentEvaluatorSignalIds": ["eval-1"],
                "evidenceWindow": ["run-1"],
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / "practice").mkdir()
    (tmp_path / "practice" / "task_spec.json").write_text(json.dumps({"gap_detection_ref": "learning/reflection_bundle.json"}), encoding="utf-8")
    (tmp_path / "practice" / "evaluation_result.json").write_text(json.dumps({"passed": True}), encoding="utf-8")
    (tmp_path / "learning" / "canary_report.json").write_text(
        json.dumps({"shadow_metrics": {"latency_p95_ms": 0}, "promote": True}),
        encoding="utf-8",
    )
    (tmp_path / "summary.json").write_text(json.dumps({"run_class": "full"}), encoding="utf-8")
    hs = {h["id"]: h["passed"] for h in evaluate_evolution_hard_stops(tmp_path)}
    assert hs["HS26"] is True


def test_hs28_fails_when_canary_missing_contract_fields(tmp_path: Path) -> None:
    (tmp_path / "learning").mkdir()
    (tmp_path / "learning" / "reflection_bundle.json").write_text(
        json.dumps({"causal_closure_checklist": {"failure_class": True, "root_cause_evidence": True, "intervention_mapped": True, "post_fix_verified": True}}),
        encoding="utf-8",
    )
    (tmp_path / "lifecycle").mkdir()
    (tmp_path / "lifecycle" / "promotion_package.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "aggregate_id": "run-1",
                "current_stage": "junior",
                "proposed_stage": "junior",
                "independent_evaluator_signal_ids": ["eval-1"],
                "evidence_window": ["run-1"],
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / "practice").mkdir()
    (tmp_path / "practice" / "task_spec.json").write_text(json.dumps({"gap_detection_ref": "learning/reflection_bundle.json"}), encoding="utf-8")
    (tmp_path / "practice" / "evaluation_result.json").write_text(json.dumps({"passed": True}), encoding="utf-8")
    (tmp_path / "learning" / "canary_report.json").write_text(
        json.dumps({"shadow_metrics": {"latency_p95_ms": 0}, "promote": True}),
        encoding="utf-8",
    )
    (tmp_path / "summary.json").write_text(json.dumps({"run_class": "full"}), encoding="utf-8")
    hs = {h["id"]: h["passed"] for h in evaluate_evolution_hard_stops(tmp_path)}
    assert hs["HS28"] is False


def test_hs28_passes_with_camel_case_canary_payload(tmp_path: Path) -> None:
    (tmp_path / "learning").mkdir()
    (tmp_path / "learning" / "reflection_bundle.json").write_text(
        json.dumps({"causal_closure_checklist": {"failure_class": True, "root_cause_evidence": True, "intervention_mapped": True, "post_fix_verified": True}}),
        encoding="utf-8",
    )
    (tmp_path / "lifecycle").mkdir()
    (tmp_path / "lifecycle" / "promotion_package.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "aggregate_id": "run-1",
                "current_stage": "junior",
                "proposed_stage": "junior",
                "independent_evaluator_signal_ids": ["eval-1"],
                "evidence_window": ["run-1"],
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / "practice").mkdir()
    (tmp_path / "practice" / "task_spec.json").write_text(json.dumps({"gap_detection_ref": "learning/reflection_bundle.json"}), encoding="utf-8")
    (tmp_path / "practice" / "evaluation_result.json").write_text(json.dumps({"passed": True}), encoding="utf-8")
    (tmp_path / "learning" / "canary_report.json").write_text(
        json.dumps(
            {
                "schemaVersion": "1.0",
                "shadowMetrics": {"latency_p95_ms": 0},
                "promote": True,
                "recordedAt": "2026-01-01T00:00:00Z",
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / "summary.json").write_text(json.dumps({"run_class": "full"}), encoding="utf-8")
    hs = {h["id"]: h["passed"] for h in evaluate_evolution_hard_stops(tmp_path)}
    assert hs["HS28"] is True


def test_hs27_fails_when_evaluation_result_not_object(tmp_path: Path) -> None:
    (tmp_path / "learning").mkdir()
    (tmp_path / "learning" / "reflection_bundle.json").write_text(
        json.dumps({"causal_closure_checklist": {"failure_class": True, "root_cause_evidence": True, "intervention_mapped": True, "post_fix_verified": True}}),
        encoding="utf-8",
    )
    (tmp_path / "lifecycle").mkdir()
    (tmp_path / "lifecycle" / "promotion_package.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "aggregate_id": "run-1",
                "current_stage": "junior",
                "proposed_stage": "junior",
                "independent_evaluator_signal_ids": ["eval-1"],
                "evidence_window": ["run-1"],
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / "practice").mkdir()
    (tmp_path / "practice" / "task_spec.json").write_text(json.dumps({"gap_detection_ref": "learning/reflection_bundle.json"}), encoding="utf-8")
    (tmp_path / "practice" / "evaluation_result.json").write_text("[]", encoding="utf-8")
    (tmp_path / "learning" / "canary_report.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "shadow_metrics": {"latency_p95_ms": 0},
                "promote": True,
                "recorded_at": "2026-01-01T00:00:00+00:00",
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / "summary.json").write_text(json.dumps({"run_class": "full"}), encoding="utf-8")
    hs = {h["id"]: h["passed"] for h in evaluate_evolution_hard_stops(tmp_path)}
    assert hs["HS27"] is False


def test_hs27_fails_when_evaluation_result_missing_passed_bool(tmp_path: Path) -> None:
    (tmp_path / "learning").mkdir()
    (tmp_path / "learning" / "reflection_bundle.json").write_text(
        json.dumps({"causal_closure_checklist": {"failure_class": True, "root_cause_evidence": True, "intervention_mapped": True, "post_fix_verified": True}}),
        encoding="utf-8",
    )
    (tmp_path / "lifecycle").mkdir()
    (tmp_path / "lifecycle" / "promotion_package.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "aggregate_id": "run-1",
                "current_stage": "junior",
                "proposed_stage": "junior",
                "independent_evaluator_signal_ids": ["eval-1"],
                "evidence_window": ["run-1"],
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / "practice").mkdir()
    (tmp_path / "practice" / "task_spec.json").write_text(json.dumps({"gap_detection_ref": "learning/reflection_bundle.json"}), encoding="utf-8")
    (tmp_path / "practice" / "evaluation_result.json").write_text(json.dumps({"passed": "yes"}), encoding="utf-8")
    (tmp_path / "learning" / "canary_report.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "shadow_metrics": {"latency_p95_ms": 0},
                "promote": True,
                "recorded_at": "2026-01-01T00:00:00+00:00",
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / "summary.json").write_text(json.dumps({"run_class": "full"}), encoding="utf-8")
    hs = {h["id"]: h["passed"] for h in evaluate_evolution_hard_stops(tmp_path)}
    assert hs["HS27"] is False


def test_hs27_fails_when_gap_detection_ref_does_not_target_reflection_bundle(tmp_path: Path) -> None:
    (tmp_path / "learning").mkdir()
    (tmp_path / "learning" / "reflection_bundle.json").write_text(
        json.dumps({"causal_closure_checklist": {"failure_class": True, "root_cause_evidence": True, "intervention_mapped": True, "post_fix_verified": True}}),
        encoding="utf-8",
    )
    (tmp_path / "lifecycle").mkdir()
    (tmp_path / "lifecycle" / "promotion_package.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "aggregate_id": "run-1",
                "current_stage": "junior",
                "proposed_stage": "junior",
                "independent_evaluator_signal_ids": ["eval-1"],
                "evidence_window": ["run-1"],
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / "practice").mkdir()
    (tmp_path / "practice" / "task_spec.json").write_text(
        json.dumps({"gap_detection_ref": "learning/other_bundle.json"}),
        encoding="utf-8",
    )
    (tmp_path / "practice" / "evaluation_result.json").write_text(json.dumps({"passed": True}), encoding="utf-8")
    (tmp_path / "learning" / "canary_report.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "shadow_metrics": {"latency_p95_ms": 0},
                "promote": True,
                "recorded_at": "2026-01-01T00:00:00+00:00",
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / "summary.json").write_text(json.dumps({"run_class": "full"}), encoding="utf-8")
    hs = {h["id"]: h["passed"] for h in evaluate_evolution_hard_stops(tmp_path)}
    assert hs["HS27"] is False


def test_hs29_fails_when_audit_lease_unknown(tmp_path: Path) -> None:
    (tmp_path / "coordination").mkdir()
    (tmp_path / "coordination" / "lease_table.json").write_text(
        json.dumps(
            {"leases": [{"lease_id": "lease-a", "lane_id": "x", "active": True}]},
        ),
        encoding="utf-8",
    )
    (tmp_path / "iam").mkdir()
    (tmp_path / "iam" / "permission_matrix.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "version": 1,
                "roles": [{"name": "implementor", "risk_tier": "standard"}],
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / "iam" / "action_audit.jsonl").write_text(
        json.dumps({"risk": "low", "lease_id": "lease-unknown"}) + "\n",
        encoding="utf-8",
    )
    (tmp_path / "orchestration").mkdir()
    (tmp_path / "orchestration" / "shard_map.json").write_text(
        json.dumps({"single_shard": True}),
        encoding="utf-8",
    )
    (tmp_path / "strategy").mkdir()
    (tmp_path / "strategy" / "proposal.json").write_text(
        json.dumps({"applied_autonomy": False}),
        encoding="utf-8",
    )
    (tmp_path / "summary.json").write_text(json.dumps({"run_class": "full"}), encoding="utf-8")
    hs = {h["id"]: h["passed"] for h in evaluate_organization_hard_stops(tmp_path)}
    assert hs["HS29"] is False


def test_hs29_fails_when_audit_actor_or_action_missing(tmp_path: Path) -> None:
    (tmp_path / "coordination").mkdir()
    (tmp_path / "coordination" / "lease_table.json").write_text(
        json.dumps({"leases": [{"lease_id": "lease-a", "lane_id": "x", "active": True}]}),
        encoding="utf-8",
    )
    (tmp_path / "iam").mkdir()
    (tmp_path / "iam" / "permission_matrix.json").write_text(
        json.dumps({"schema_version": "1.0", "roles": [{"name": "implementor"}]}),
        encoding="utf-8",
    )
    (tmp_path / "iam" / "action_audit.jsonl").write_text(
        json.dumps({"risk": "low", "lease_id": "lease-a", "occurred_at": "2026-01-01T00:00:00+00:00"}) + "\n",
        encoding="utf-8",
    )
    (tmp_path / "orchestration").mkdir()
    (tmp_path / "orchestration" / "shard_map.json").write_text(json.dumps({"single_shard": True}), encoding="utf-8")
    (tmp_path / "strategy").mkdir()
    (tmp_path / "strategy" / "proposal.json").write_text(json.dumps({"applied_autonomy": False}), encoding="utf-8")
    (tmp_path / "summary.json").write_text(json.dumps({"run_class": "full"}), encoding="utf-8")
    hs = {h["id"]: h["passed"] for h in evaluate_organization_hard_stops(tmp_path)}
    assert hs["HS29"] is False


def test_hs29_fails_when_audit_line_missing_lease_id(tmp_path: Path) -> None:
    (tmp_path / "coordination").mkdir()
    (tmp_path / "coordination" / "lease_table.json").write_text(
        json.dumps({"leases": [{"lease_id": "lease-a", "lane_id": "x", "active": True}]}),
        encoding="utf-8",
    )
    (tmp_path / "iam").mkdir()
    (tmp_path / "iam" / "permission_matrix.json").write_text(
        json.dumps({"schema_version": "1.0", "roles": [{"name": "implementor"}]}),
        encoding="utf-8",
    )
    (tmp_path / "iam" / "action_audit.jsonl").write_text(
        json.dumps({"risk": "low"}) + "\n",
        encoding="utf-8",
    )
    (tmp_path / "orchestration").mkdir()
    (tmp_path / "orchestration" / "shard_map.json").write_text(json.dumps({"single_shard": True}), encoding="utf-8")
    (tmp_path / "strategy").mkdir()
    (tmp_path / "strategy" / "proposal.json").write_text(json.dumps({"applied_autonomy": False}), encoding="utf-8")
    (tmp_path / "summary.json").write_text(json.dumps({"run_class": "full"}), encoding="utf-8")
    hs = {h["id"]: h["passed"] for h in evaluate_organization_hard_stops(tmp_path)}
    assert hs["HS29"] is False


def test_hs31_requires_handoff_envelope_when_multi_shard(tmp_path: Path) -> None:
    (tmp_path / "coordination").mkdir()
    (tmp_path / "coordination" / "lease_table.json").write_text(
        json.dumps({"leases": [{"lease_id": "lease-a", "lane_id": "x", "active": True}]}),
        encoding="utf-8",
    )
    (tmp_path / "iam").mkdir()
    (tmp_path / "iam" / "permission_matrix.json").write_text(
        json.dumps({"schema_version": "1.0", "roles": [{"name": "implementor"}]}),
        encoding="utf-8",
    )
    (tmp_path / "iam" / "action_audit.jsonl").write_text(
        json.dumps({"risk": "low", "lease_id": "lease-a"}) + "\n",
        encoding="utf-8",
    )
    (tmp_path / "orchestration").mkdir()
    (tmp_path / "orchestration" / "shard_map.json").write_text(json.dumps({"single_shard": False}), encoding="utf-8")
    (tmp_path / "strategy").mkdir()
    (tmp_path / "strategy" / "proposal.json").write_text(json.dumps({"applied_autonomy": False}), encoding="utf-8")
    (tmp_path / "summary.json").write_text(json.dumps({"run_class": "full"}), encoding="utf-8")
    hs = {h["id"]: h["passed"] for h in evaluate_organization_hard_stops(tmp_path)}
    assert hs["HS31"] is False
    (tmp_path / "orchestration" / "handoff_envelope.json").write_text(json.dumps({"ok": True}), encoding="utf-8")
    hs2 = {h["id"]: h["passed"] for h in evaluate_organization_hard_stops(tmp_path)}
    assert hs2["HS31"] is True


def test_hs32_requires_promotion_package_and_proposal_ref(tmp_path: Path) -> None:
    (tmp_path / "coordination").mkdir()
    (tmp_path / "coordination" / "lease_table.json").write_text(
        json.dumps({"leases": [{"lease_id": "lease-a", "lane_id": "x", "active": True}]}),
        encoding="utf-8",
    )
    (tmp_path / "iam").mkdir()
    (tmp_path / "iam" / "permission_matrix.json").write_text(
        json.dumps({"schema_version": "1.0", "roles": [{"name": "implementor"}]}),
        encoding="utf-8",
    )
    (tmp_path / "iam" / "action_audit.jsonl").write_text(
        json.dumps({"risk": "low", "lease_id": "lease-a"}) + "\n",
        encoding="utf-8",
    )
    (tmp_path / "orchestration").mkdir()
    (tmp_path / "orchestration" / "shard_map.json").write_text(json.dumps({"single_shard": True}), encoding="utf-8")
    (tmp_path / "strategy").mkdir()
    (tmp_path / "strategy" / "proposal.json").write_text(
        json.dumps({"applied_autonomy": True, "requires_promotion_package": False}),
        encoding="utf-8",
    )
    (tmp_path / "summary.json").write_text(json.dumps({"run_class": "full"}), encoding="utf-8")
    hs = {h["id"]: h["passed"] for h in evaluate_organization_hard_stops(tmp_path)}
    assert hs["HS32"] is False
    (tmp_path / "strategy" / "proposal.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "actor_id": "strategy-agent",
                "applied_autonomy": True,
                "requires_promotion_package": True,
                "proposal_ref": "lifecycle/promotion_package.json",
            }
        ),
        encoding="utf-8",
    )
    hs2 = {h["id"]: h["passed"] for h in evaluate_organization_hard_stops(tmp_path)}
    assert hs2["HS32"] is True


def test_hs32_fails_when_strategy_proposal_schema_invalid(tmp_path: Path) -> None:
    (tmp_path / "coordination").mkdir()
    (tmp_path / "coordination" / "lease_table.json").write_text(
        json.dumps({"leases": [{"lease_id": "lease-a", "lane_id": "x", "active": True}]}),
        encoding="utf-8",
    )
    (tmp_path / "iam").mkdir()
    (tmp_path / "iam" / "permission_matrix.json").write_text(
        json.dumps({"schema_version": "1.0", "roles": [{"name": "implementor"}]}),
        encoding="utf-8",
    )
    (tmp_path / "iam" / "action_audit.jsonl").write_text(
        json.dumps({"risk": "low", "lease_id": "lease-a"}) + "\n",
        encoding="utf-8",
    )
    (tmp_path / "orchestration").mkdir()
    (tmp_path / "orchestration" / "shard_map.json").write_text(json.dumps({"single_shard": True}), encoding="utf-8")
    (tmp_path / "strategy").mkdir()
    (tmp_path / "strategy" / "proposal.json").write_text(
        json.dumps(
            {
                "schema_version": "2.0",
                "actor_id": "strategy-agent",
                "requires_promotion_package": False,
                "applied_autonomy": False,
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / "summary.json").write_text(json.dumps({"run_class": "full"}), encoding="utf-8")
    hs = {h["id"]: h["passed"] for h in evaluate_organization_hard_stops(tmp_path)}
    assert hs["HS32"] is False
