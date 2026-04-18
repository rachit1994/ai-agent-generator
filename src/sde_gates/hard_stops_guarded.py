"""HS07–HS16 checks for guarded_pipeline harness runs (V2+V3 skeleton)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _read_json(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        out: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
        return out
    except json.JSONDecodeError:
        return None


def _hs07_question_policy(output_dir: Path) -> bool:
    path = output_dir / "program" / "question_workbook.jsonl"
    if not path.is_file():
        return False
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            return False
        if row.get("status") == "open":
            return False
    return True


def _hs08_doc_review(output_dir: Path) -> bool:
    body = _read_json(output_dir / "program" / "doc_review.json")
    return bool(body and body.get("passed") is True)


def _hs09_plan_amendment_trace(output_dir: Path) -> bool:
    orch = output_dir / "orchestration.jsonl"
    if not orch.is_file():
        return False
    plan = _read_json(output_dir / "program" / "project_plan.json")
    if not plan:
        return False
    return len(orch.read_text(encoding="utf-8").strip()) > 0


def _hs10_learning(output_dir: Path) -> bool:
    path = output_dir / "program" / "learning_events.jsonl"
    if not path.is_file():
        return False
    required = {"event_id", "type", "refs", "created_at"}
    count = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            return False
        if not required.issubset(row.keys()):
            return False
        count += 1
    return count >= 8


def _hs11_discovery_and_plan(output_dir: Path) -> bool:
    return bool(
        _read_json(output_dir / "program" / "discovery.json")
        and _read_json(output_dir / "program" / "project_plan.json")
    )


def _hs12_doc_pack(output_dir: Path) -> bool:
    body = _read_json(output_dir / "program" / "doc_pack_manifest.json")
    if not body:
        return False
    entries = body.get("entries") or []
    for ent in entries:
        if not isinstance(ent, dict):
            return False
        rel = ent.get("path")
        if not rel:
            return False
        if not (output_dir / rel).is_file() and not (output_dir / rel).is_dir():
            return False
    return True


def _hs13_step_reviews_vs_progress(output_dir: Path) -> bool:
    prog = _read_json(output_dir / "program" / "progress.json")
    if not prog:
        return False
    last = prog.get("last_completed_step_id")
    if not last:
        return True
    order = ["step_planner", "step_implement", "step_verify"]
    if last not in order:
        return False
    idx = order.index(last)
    for sid in order[: idx + 1]:
        rev = _read_json(output_dir / "step_reviews" / f"{sid}.json")
        if not rev or rev.get("passed") is not True:
            return False
    return True


def _hs14_verification_bundle(output_dir: Path) -> bool:
    review = _read_json(output_dir / "review.json")
    dod = review.get("definition_of_done") if review else None
    vb = _read_json(output_dir / "verification_bundle.json")
    if not vb:
        return False
    vb_ok = bool(vb.get("passed"))
    if not dod:
        return vb_ok
    for chk in dod.get("checks") or []:
        if not isinstance(chk, dict):
            continue
        if chk.get("id") == "verification" and chk.get("required"):
            return vb_ok and bool(chk.get("passed"))
    return vb_ok


def _hs15_terminal_honesty(output_dir: Path, events: list[dict[str, Any]]) -> bool:
    review = _read_json(output_dir / "review.json")
    if not review:
        return False
    status = review.get("status")
    dod = review.get("definition_of_done")
    if status == "completed_review_pass":
        if dod and not dod.get("all_required_passed"):
            return False
    for ev in events:
        meta = ev.get("metadata") if isinstance(ev.get("metadata"), dict) else {}
        if meta.get("step_review") == "fail":
            return False
    return True


def _hs16_work_batch(output_dir: Path) -> bool:
    body = _read_json(output_dir / "program" / "work_batch.json")
    if not body:
        return False
    for rel in body.get("paths") or []:
        if not (output_dir / rel).exists():
            return False
    return True


def evaluate_guarded_hard_stops(
    output_dir: Path,
    events: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """HS07–HS16 when ``program/project_plan.json`` exists (guarded harness)."""
    if not (output_dir / "program" / "project_plan.json").is_file():
        return []
    return [
        {"id": "HS07", "passed": _hs07_question_policy(output_dir), "evidence_ref": "program/question_workbook.jsonl"},
        {"id": "HS08", "passed": _hs08_doc_review(output_dir), "evidence_ref": "program/doc_review.json"},
        {"id": "HS09", "passed": _hs09_plan_amendment_trace(output_dir), "evidence_ref": "orchestration.jsonl"},
        {"id": "HS10", "passed": _hs10_learning(output_dir), "evidence_ref": "program/learning_events.jsonl"},
        {"id": "HS11", "passed": _hs11_discovery_and_plan(output_dir), "evidence_ref": "program/discovery.json"},
        {"id": "HS12", "passed": _hs12_doc_pack(output_dir), "evidence_ref": "program/doc_pack_manifest.json"},
        {"id": "HS13", "passed": _hs13_step_reviews_vs_progress(output_dir), "evidence_ref": "program/progress.json"},
        {"id": "HS14", "passed": _hs14_verification_bundle(output_dir), "evidence_ref": "verification_bundle.json"},
        {"id": "HS15", "passed": _hs15_terminal_honesty(output_dir, events), "evidence_ref": "review.json"},
        {"id": "HS16", "passed": _hs16_work_batch(output_dir), "evidence_ref": "program/work_batch.json"},
    ]
