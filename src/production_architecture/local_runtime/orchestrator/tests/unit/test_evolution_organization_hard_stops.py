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


def test_hs29_fails_when_audit_lease_unknown(tmp_path: Path) -> None:
    (tmp_path / "coordination").mkdir()
    (tmp_path / "coordination" / "lease_table.json").write_text(
        json.dumps(
            {"leases": [{"lease_id": "lease-a", "lane_id": "x", "active": True}]},
        ),
        encoding="utf-8",
    )
    (tmp_path / "iam").mkdir()
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
