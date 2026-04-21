from __future__ import annotations

from pathlib import Path

from guardrails_and_safety.review_gating_evaluator_authority.review_gating.review import build_review


def test_build_review_uses_last_finalize_event_for_status(tmp_path: Path) -> None:
    out = tmp_path / "run"
    out.mkdir()
    events = [
        {"stage": "finalize", "score": {"passed": True}},
        {"stage": "executor", "score": {"passed": False}},
        {"stage": "finalize", "score": {"passed": False}},
    ]
    review = build_review(
        run_id="rid-last-finalize",
        mode="baseline",
        parsed={"answer": "ok", "checks": [{"name": "c", "passed": True}], "refusal": None},
        output_dir=out,
        events=events,
        run_status="ok",
    )
    assert review["status"] == "completed_review_fail"


def test_build_review_run_status_not_ok_overrides_finalize_pass(tmp_path: Path) -> None:
    out = tmp_path / "run2"
    out.mkdir()
    review = build_review(
        run_id="rid-timeout",
        mode="baseline",
        parsed={"answer": "ok", "checks": [{"name": "c", "passed": True}], "refusal": None},
        output_dir=out,
        events=[{"stage": "finalize", "score": {"passed": True}}],
        run_status="timeout",
    )
    assert review["status"] == "incomplete"
    assert review["reasons"] == ["run_timeout"]
