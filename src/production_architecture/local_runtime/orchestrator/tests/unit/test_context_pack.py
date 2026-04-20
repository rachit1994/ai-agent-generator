from __future__ import annotations

import json
from pathlib import Path

import pytest

from orchestrator.api.context_pack import build_context_pack, latest_output_dirs_by_step


def test_latest_output_dirs_by_step_order(tmp_path: Path) -> None:
    sess = tmp_path / "s"
    sess.mkdir()
    jl = sess / "step_runs.jsonl"
    jl.write_text(
        '{"step_id":"a","output_dir":"/first"}\n{"step_id":"a","output_dir":"/second"}\n',
        encoding="utf-8",
    )
    assert latest_output_dirs_by_step(sess) == {"a": "/second"}


def test_build_context_pack_includes_intake_when_present(tmp_path: Path) -> None:
    sess = tmp_path / "session"
    sess.mkdir()
    intake = sess / "intake"
    intake.mkdir()
    (intake / "discovery.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "goal_excerpt": "Ship the widget API",
                "constraints": ["no breaking changes"],
                "non_goals": [],
                "open_questions": ["auth model?"],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    (intake / "research_digest.md").write_text("# Digest\n\nstub\n", encoding="utf-8")
    (intake / "doc_review.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "passed": True,
                "reviewer": "unit-test",
                "findings": [{"id": "f1", "severity": "info", "text": "check TLS"}],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    (intake / "question_workbook.jsonl").write_text(
        "\n".join(
            [
                json.dumps({"id": "early", "status": "open", "topic": "old"}),
                json.dumps({"id": "wb-latest", "status": "open", "topic": "latency"}),
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    step = {
        "step_id": "s1",
        "title": "S",
        "description": "do work",
        "depends_on": [],
        "path_scope": [],
    }
    pack = build_context_pack(
        repo_root=tmp_path,
        session_dir=sess,
        step=step,
        prior_failures=[],
        max_chars=20_000,
    )
    assert pack.get("intake_loaded") is True
    md = pack["markdown"]
    assert "Session intake" in md
    assert "Ship the widget API" in md
    assert "research_digest" in md
    assert "doc_review.json" in md
    assert "unit-test" in md
    assert "TLS" in md
    assert "question_workbook.jsonl" in md
    assert "wb-latest" in md
    assert "latency" in md
    lineage = (sess / "context_pack_lineage.jsonl").read_text(encoding="utf-8").strip().splitlines()
    row = json.loads(lineage[-1])
    assert row.get("intake_loaded") is True


def test_build_context_pack_intake_workbook_only_not_loaded(tmp_path: Path) -> None:
    """Orphan JSONL without discovery/doc_review does not open an intake section."""
    sess = tmp_path / "session"
    sess.mkdir()
    intake = sess / "intake"
    intake.mkdir()
    (intake / "question_workbook.jsonl").write_text(
        json.dumps({"id": "solo", "topic": "orphan"}) + "\n",
        encoding="utf-8",
    )
    step = {
        "step_id": "s1",
        "title": "S",
        "description": "d",
        "depends_on": [],
        "path_scope": [],
    }
    pack = build_context_pack(
        repo_root=tmp_path,
        session_dir=sess,
        step=step,
        prior_failures=[],
        max_chars=20_000,
    )
    assert pack.get("intake_loaded") is False
    assert "Session intake" not in pack["markdown"]
    assert "### question_workbook.jsonl" not in pack["markdown"]


def test_build_context_pack_intake_doc_review_only(tmp_path: Path) -> None:
    sess = tmp_path / "session"
    sess.mkdir()
    intake = sess / "intake"
    intake.mkdir()
    (intake / "doc_review.json").write_text(
        json.dumps(
            {
                "passed": False,
                "reviewer": "design-review",
                "findings": [{"topic": "scope", "detail": "too broad"}],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    (intake / "question_workbook.jsonl").write_text(
        json.dumps({"id": "from-doc-only", "topic": "follow-up"}) + "\n",
        encoding="utf-8",
    )

    step = {
        "step_id": "s1",
        "title": "S",
        "description": "d",
        "depends_on": [],
        "path_scope": [],
    }
    pack = build_context_pack(
        repo_root=tmp_path,
        session_dir=sess,
        step=step,
        prior_failures=[],
        max_chars=20_000,
    )
    assert pack.get("intake_loaded") is True
    md = pack["markdown"]
    assert "doc_review.json" in md
    assert "design-review" in md
    assert "too broad" in md
    assert "question_workbook.jsonl" in md
    assert "from-doc-only" in md


def test_build_context_pack_no_intake_flag(tmp_path: Path) -> None:
    sess = tmp_path / "session"
    sess.mkdir()
    step = {
        "step_id": "s1",
        "title": "S",
        "description": "d",
        "depends_on": [],
        "path_scope": [],
    }
    pack = build_context_pack(
        repo_root=tmp_path,
        session_dir=sess,
        step=step,
        prior_failures=[],
        max_chars=20_000,
    )
    assert pack.get("intake_loaded") is False
    assert "Session intake" not in pack["markdown"]


def test_build_context_pack_prior_dep_excerpts(tmp_path: Path) -> None:
    sess = tmp_path / "session"
    sess.mkdir()
    run_a = tmp_path / "run_a"
    run_a.mkdir()
    (run_a / "summary.json").write_text('{"ok": true, "note": "prior"}', encoding="utf-8")
    (run_a / "report.md").write_text("# Report\nline\n", encoding="utf-8")

    step = {
        "step_id": "b",
        "title": "B",
        "description": "second",
        "depends_on": ["a"],
        "path_scope": [],
    }
    pack = build_context_pack(
        repo_root=tmp_path,
        session_dir=sess,
        step=step,
        prior_failures=[],
        latest_runs_by_step={"a": str(run_a)},
        max_chars=20_000,
    )
    md = pack["markdown"]
    assert "prior" in md or "summary.json" in md
    assert len(pack.get("references") or []) == 1
    assert pack["references"][0]["step_id"] == "a"
    assert pack["schema_version"] == "1.1"


def test_build_context_pack_truncation_hs03(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    sess = tmp_path / "session"
    sess.mkdir()

    def _fat_index(*_a: object, **_kw: object) -> dict:
        return {"paths": [f"src/m{i:04d}.py" for i in range(500)], "file_count": 500}

    monkeypatch.setattr("orchestrator.api.context_pack.build_repo_index", _fat_index)

    step = {
        "step_id": "x",
        "title": "X",
        "description": "d",
        "depends_on": [],
        "path_scope": [],
    }
    pack = build_context_pack(
        repo_root=tmp_path,
        session_dir=sess,
        step=step,
        prior_failures=[],
        max_chars=800,
    )
    assert pack["truncated"] is True
    assert pack["truncation_hs03_ok"] is True
    assert len(pack.get("truncation_events") or []) == 1
    assert len(pack.get("reductions") or []) == 1
    assert pack["truncation_events"][0]["provenance_id"] == pack["reductions"][0]["provenance_id"]
    assert "markdown_sha256_full" in pack
    lineage = (sess / "context_pack_lineage.jsonl").read_text(encoding="utf-8").strip().splitlines()
    assert len(lineage) >= 1
    row = json.loads(lineage[-1])
    assert row["step_id"] == "x"
    assert row["truncated"] is True
    assert row.get("intake_loaded") is False
