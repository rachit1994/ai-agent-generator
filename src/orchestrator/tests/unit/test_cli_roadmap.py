from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

import orchestrator.runtime.cli.main as cli_main
from orchestrator.runtime.cli.main import build_parser, main


def test_cli_roadmap_review_parse(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    (tmp_path / "docs" / "sde").mkdir(parents=True)
    (tmp_path / "docs" / "onboarding").mkdir(parents=True)
    for rel in (
        "docs/sde/core-features-and-upstream-parity.md",
        "docs/sde/implementation-contract.md",
        "docs/onboarding/action-plan.md",
    ):
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("# s\n", encoding="utf-8")

    body = {
        "per_version_pct": {f"V{i}": 10 for i in range(1, 8)},
        "overall_pct": 15,
        "code_quality_0_100": 80,
        "done": [],
        "remaining": [],
        "learning_note": "n",
    }
    monkeypatch.setattr(
        "orchestrator.api.gemma_roadmap_review.invoke_model",
        lambda *_a, **_k: {"text": json.dumps(body), "error": None},
    )
    learn = tmp_path / "l.jsonl"
    monkeypatch.setattr(sys, "argv", ["sde", "roadmap-review", "--repo-root", str(tmp_path), "--append-learning", str(learn)])
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 0
    assert learn.is_file()


def test_cli_evolve_exits_zero_at_target(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    (tmp_path / "docs" / "sde").mkdir(parents=True)
    (tmp_path / "docs" / "onboarding").mkdir(parents=True)
    for rel in (
        "docs/sde/core-features-and-upstream-parity.md",
        "docs/sde/implementation-contract.md",
        "docs/onboarding/action-plan.md",
    ):
        p = tmp_path / rel
        p.write_text("# s\n", encoding="utf-8")

    body = {
        "per_version_pct": {f"V{i}": 100 for i in range(1, 8)},
        "overall_pct": 100,
        "code_quality_0_100": 90,
        "done": [],
        "remaining": [],
        "learning_note": "n",
    }
    monkeypatch.setattr(
        "orchestrator.api.gemma_roadmap_review.invoke_model",
        lambda *_a, **_k: {"text": json.dumps(body), "error": None},
    )
    learn = tmp_path / "e.jsonl"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "sde",
            "evolve",
            "--repo-root",
            str(tmp_path),
            "--max-rounds",
            "2",
            "--target-pct",
            "99",
            "--learning-path",
            str(learn),
        ],
    )
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 0
