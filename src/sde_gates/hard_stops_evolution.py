"""HS25–HS28 evolution / lifecycle checks (V6 harness)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .run_profile import is_coding_only

_CLOSURE_KEYS = ("failure_class", "root_cause_evidence", "intervention_mapped", "post_fix_verified")


def _hs25_causal_closure(output_dir: Path) -> bool:
    path = output_dir / "learning" / "reflection_bundle.json"
    if not path.is_file():
        return False
    try:
        body: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False
    chk = body.get("causal_closure_checklist")
    if not isinstance(chk, dict):
        return False
    return all(chk.get(k) is True for k in _CLOSURE_KEYS)


def _hs26_promotion_signals(output_dir: Path) -> bool:
    path = output_dir / "lifecycle" / "promotion_package.json"
    if not path.is_file():
        return False
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False
    sigs = body.get("independent_evaluator_signal_ids")
    return isinstance(sigs, list) and len(sigs) > 0


def _hs27_practice_gap(output_dir: Path) -> bool:
    spec = output_dir / "practice" / "task_spec.json"
    res = output_dir / "practice" / "evaluation_result.json"
    if not spec.is_file() or not res.is_file():
        return False
    try:
        body = json.loads(spec.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False
    ref = body.get("gap_detection_ref")
    return isinstance(ref, str) and len(ref) > 0


def _hs28_canary(output_dir: Path) -> bool:
    path = output_dir / "learning" / "canary_report.json"
    if not path.is_file():
        return False
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False
    if not isinstance(body.get("shadow_metrics"), dict):
        return False
    return isinstance(body.get("promote"), bool)


def evaluate_evolution_hard_stops(output_dir: Path) -> list[dict[str, Any]]:
    if is_coding_only(output_dir):
        return []
    if not (output_dir / "learning" / "reflection_bundle.json").is_file():
        return []
    return [
        {"id": "HS25", "passed": _hs25_causal_closure(output_dir), "evidence_ref": "learning/reflection_bundle.json"},
        {"id": "HS26", "passed": _hs26_promotion_signals(output_dir), "evidence_ref": "lifecycle/promotion_package.json"},
        {"id": "HS27", "passed": _hs27_practice_gap(output_dir), "evidence_ref": "practice/task_spec.json"},
        {"id": "HS28", "passed": _hs28_canary(output_dir), "evidence_ref": "learning/canary_report.json"},
    ]
