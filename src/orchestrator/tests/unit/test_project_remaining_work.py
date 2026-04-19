from __future__ import annotations

import json
from pathlib import Path

import pytest

from orchestrator.api.project_remaining_work import evaluate_remaining_work


def _write(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def test_evaluate_remaining_work_hybrid_scoring(tmp_path: Path) -> None:
    _write(tmp_path / "docs/full.md", "- [ ] Stage A\n- [ ] Stage B\n")
    _write(tmp_path / "docs/status.md", "marker:a\nmarker:b\n")
    _write(tmp_path / "src/app/a.py", "pass\n")
    rules = {
        "schema_version": "1.0",
        "checklist_path": "docs/full.md",
        "status_values": {"missing": 0.0, "partial": 0.4, "implemented": 1.0},
        "items": [
            {
                "id": "stage_a",
                "label": "Stage A",
                "weight": 2.0,
                "checklist_marker": "Stage A",
                "doc_evidence": [{"path": "docs/status.md", "contains": ["marker:a"]}],
                "code_evidence": [{"paths_exist": ["src/app/a.py"]}],
            },
            {
                "id": "stage_b",
                "label": "Stage B",
                "weight": 1.0,
                "checklist_marker": "Stage B",
                "doc_evidence": [{"path": "docs/status.md", "contains": ["marker:b"]}],
                "code_evidence": [{"paths_exist": ["src/app/b.py"]}],
            },
        ],
        "gates": [{"id": "gate_a", "required_item_ids": ["stage_a"]}],
    }
    out = evaluate_remaining_work(tmp_path, rules)
    assert out["completion_pct"] == pytest.approx(80.0)
    assert out["remaining_pct"] == pytest.approx(20.0)
    assert out["items"]["stage_a"]["status"] == "implemented"
    assert out["items"]["stage_b"]["status"] == "partial"
    assert out["gates"]["gate_a"]["passed"] is True


def test_evaluate_remaining_work_fails_unmapped_checklist_rows(tmp_path: Path) -> None:
    _write(tmp_path / "docs/full.md", "- [ ] Stage A\n- [ ] Stage Unmapped\n")
    rules = {
        "schema_version": "1.0",
        "checklist_path": "docs/full.md",
        "status_values": {"missing": 0.0, "partial": 0.4, "implemented": 1.0},
        "items": [
            {
                "id": "stage_a",
                "label": "Stage A",
                "weight": 1.0,
                "checklist_marker": "Stage A",
                "doc_evidence": [],
                "code_evidence": [],
            }
        ],
    }
    with pytest.raises(ValueError, match="unmapped_checklist_items"):
        evaluate_remaining_work(tmp_path, rules)


def test_evaluate_remaining_work_report_serialization_is_stable(tmp_path: Path) -> None:
    _write(tmp_path / "docs/full.md", "- [ ] A\n")
    rules = {
        "schema_version": "1.0",
        "checklist_path": "docs/full.md",
        "status_values": {"missing": 0.0, "partial": 0.4, "implemented": 1.0},
        "items": [
            {"id": "a", "label": "A", "weight": 1.0, "checklist_marker": "A", "doc_evidence": [], "code_evidence": []}
        ],
    }
    out = evaluate_remaining_work(tmp_path, rules)
    blob = json.dumps(out, sort_keys=True)
    assert "completion_pct" in blob
    assert out["item_order"] == ["a"]
