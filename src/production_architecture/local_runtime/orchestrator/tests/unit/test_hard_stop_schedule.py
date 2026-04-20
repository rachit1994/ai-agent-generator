"""Contract: ``expected_hard_stop_ids`` matches ``evaluate_hard_stops`` ID list."""

from __future__ import annotations

import json
from pathlib import Path

from guardrails_and_safety.risk_budgets_permission_matrix.risk_budgets.hard_stop_schedule import expected_hard_stop_ids
from guardrails_and_safety.risk_budgets_permission_matrix.risk_budgets.hard_stops import evaluate_hard_stops


def _ids(hs: list[dict[str, object]]) -> list[str]:
    return [str(h["id"]) for h in hs]


def test_schedule_empty_baseline_matches_evaluate(tmp_path: Path) -> None:
    hs = evaluate_hard_stops(tmp_path, [], {}, run_status="ok", mode="baseline")
    assert _ids(hs) == expected_hard_stop_ids("baseline", tmp_path)


def test_schedule_coding_only_skips_extension_bands(tmp_path: Path) -> None:
    (tmp_path / "summary.json").write_text(
        json.dumps({"run_class": "coding_only"}),
        encoding="utf-8",
    )
    (tmp_path / "replay_manifest.json").write_text("{}", encoding="utf-8")
    hs = evaluate_hard_stops(tmp_path, [], {}, run_status="ok", mode="baseline")
    assert _ids(hs) == expected_hard_stop_ids("baseline", tmp_path)


def test_schedule_guarded_without_project_plan_no_hs07(tmp_path: Path) -> None:
    (tmp_path / "replay_manifest.json").write_text("{}", encoding="utf-8")
    hs = evaluate_hard_stops(tmp_path, [], {}, run_status="ok", mode="guarded_pipeline")
    assert _ids(hs) == expected_hard_stop_ids("guarded_pipeline", tmp_path)
    assert "HS07" not in _ids(hs)


def test_schedule_full_stack_matches_evaluate(tmp_path: Path) -> None:
    (tmp_path / "program").mkdir(parents=True)
    (tmp_path / "program" / "project_plan.json").write_text("{}", encoding="utf-8")
    (tmp_path / "memory").mkdir(parents=True)
    (tmp_path / "memory" / "retrieval_bundle.json").write_text("{}", encoding="utf-8")
    (tmp_path / "learning").mkdir(parents=True)
    (tmp_path / "learning" / "reflection_bundle.json").write_text("{}", encoding="utf-8")
    (tmp_path / "coordination").mkdir(parents=True)
    (tmp_path / "coordination" / "lease_table.json").write_text("{}", encoding="utf-8")
    (tmp_path / "replay_manifest.json").write_text("{}", encoding="utf-8")
    hs = evaluate_hard_stops(tmp_path, [], {}, run_status="ok", mode="phased_pipeline")
    assert _ids(hs) == expected_hard_stop_ids("phased_pipeline", tmp_path)
    assert _ids(hs) == [f"HS{i:02d}" for i in range(1, 33)]


def test_schedule_baseline_replay_adds_hs17_hs20(tmp_path: Path) -> None:
    (tmp_path / "replay_manifest.json").write_text("{}", encoding="utf-8")
    hs = evaluate_hard_stops(tmp_path, [], {}, run_status="ok", mode="baseline")
    assert _ids(hs) == expected_hard_stop_ids("baseline", tmp_path)
    assert _ids(hs) == [f"HS{i:02d}" for i in list(range(1, 7)) + list(range(17, 21))]


def test_schedule_guarded_with_plan_and_replay(tmp_path: Path) -> None:
    (tmp_path / "program").mkdir(parents=True)
    (tmp_path / "program" / "project_plan.json").write_text("{}", encoding="utf-8")
    (tmp_path / "replay_manifest.json").write_text("{}", encoding="utf-8")
    hs = evaluate_hard_stops(tmp_path, [], {}, run_status="ok", mode="guarded_pipeline")
    assert _ids(hs) == expected_hard_stop_ids("guarded_pipeline", tmp_path)
    assert _ids(hs) == [f"HS{i:02d}" for i in list(range(1, 17)) + list(range(17, 21))]
