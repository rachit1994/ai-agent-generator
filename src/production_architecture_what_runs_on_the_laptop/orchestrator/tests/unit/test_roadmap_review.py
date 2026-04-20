from __future__ import annotations

import json
from pathlib import Path

import pytest

from orchestrator.api.gemma_roadmap_review import append_roadmap_learning_line, roadmap_review
from orchestrator.api.self_evolve import run_bounded_evolve_loop


def test_roadmap_review_parses_model_json(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (tmp_path / "docs" / "architecture").mkdir(parents=True)
    for name in (
        "docs/UNDERSTANDING-THE-CODE.md",
        "docs/architecture/master-architecture-feature-completion.md",
    ):
        p = tmp_path / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("# stub\n", encoding="utf-8")

    review_body = {
        "per_version_pct": {f"V{i}": 50 for i in range(1, 8)},
        "overall_pct": 55,
        "code_quality_0_100": 70,
        "done": ["V1 traces"],
        "remaining": ["V2 target repo"],
        "learning_note": "Keep shipping in slices.",
    }

    def _fake_invoke(*_a, **_k):  # type: ignore[no-untyped-def]
        return {"text": json.dumps(review_body), "error": None}

    monkeypatch.setattr("orchestrator.api.gemma_roadmap_review.invoke_model", _fake_invoke)
    out = roadmap_review(repo_root=tmp_path)
    assert out["ok"] is True
    assert out["review"]["overall_pct"] == 55


def test_append_roadmap_learning_line_writes_jsonl(tmp_path: Path) -> None:
    dest = tmp_path / "learn.jsonl"
    append_roadmap_learning_line(dest, {"ok": True, "review": {"overall_pct": 3}})
    lines = dest.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    row = json.loads(lines[0])
    assert row["type"] == "roadmap_review"
    assert row["payload"]["review"]["overall_pct"] == 3


def test_run_bounded_evolve_loop_stops_at_target(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (tmp_path / "docs" / "architecture").mkdir(parents=True)
    for name in (
        "docs/UNDERSTANDING-THE-CODE.md",
        "docs/architecture/master-architecture-feature-completion.md",
    ):
        p = tmp_path / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("# x\n", encoding="utf-8")

    review_body = {
        "per_version_pct": {f"V{i}": 100 for i in range(1, 8)},
        "overall_pct": 100,
        "code_quality_0_100": 90,
        "done": [],
        "remaining": [],
        "learning_note": "done",
    }

    monkeypatch.setattr(
        "orchestrator.api.gemma_roadmap_review.invoke_model",
        lambda *_a, **_k: {"text": json.dumps(review_body), "error": None},
    )

    learn = tmp_path / "out.jsonl"
    code, last = run_bounded_evolve_loop(
        repo_root=tmp_path,
        max_rounds=5,
        target_pct=99,
        task=None,
        mode="baseline",
        learning_path=learn,
    )
    assert code == 0
    assert last.get("ok") is True
    assert learn.is_file()
