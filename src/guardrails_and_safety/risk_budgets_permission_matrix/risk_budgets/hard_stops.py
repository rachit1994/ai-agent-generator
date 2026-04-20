"""Hard-stop checks HS01–HS06 from on-disk evidence."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from guardrails_and_safety.risk_budgets_permission_matrix.gates_constants.constants import REQUIRED_REVIEW_KEYS, TOKEN_CONTEXT_SCHEMA
from guardrails_and_safety.review_gating_evaluator_authority.review_gating.review import validate_review_payload
from guardrails_and_safety.risk_budgets_permission_matrix.time_and_budget.time_util import parse_iso_utc
from .hard_stops_events import evaluate_event_lineage_hard_stops
from .hard_stops_guarded import evaluate_guarded_hard_stops
from .hard_stops_evolution import evaluate_evolution_hard_stops
from .hard_stops_memory import evaluate_memory_hard_stops
from .hard_stops_organization import evaluate_organization_hard_stops


def _hs01_review(output_dir: Path) -> bool:
    review_path = output_dir / "review.json"
    if not review_path.is_file():
        return False
    try:
        body = json.loads(review_path.read_text(encoding="utf-8"))
        if not isinstance(body, dict):
            return False
        if not REQUIRED_REVIEW_KEYS.issubset(body.keys()):
            return False
        return len(validate_review_payload(body)) == 0
    except json.JSONDecodeError:
        return False


def _hs03_truncation_ok(token_context: dict[str, Any]) -> bool:
    trunc = token_context.get("truncation_events") or []
    reds = token_context.get("reductions") or []
    if len(trunc) == 0:
        return True
    if len(reds) == 0:
        return False
    normalized_reductions: set[str] = set()
    for row in reds:
        if not isinstance(row, dict):
            return False
        provenance_id = row.get("provenance_id")
        if not isinstance(provenance_id, str) or not provenance_id.strip():
            return False
        normalized_reductions.add(provenance_id.strip())
    for row in trunc:
        if not isinstance(row, dict):
            return False
        provenance_id = row.get("provenance_id")
        if not isinstance(provenance_id, str) or not provenance_id.strip():
            return False
        if provenance_id.strip() not in normalized_reductions:
            return False
    return True


def _safe_int(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        raw = value.strip()
        if raw.startswith(("+", "-")):
            sign = raw[0]
            digits = raw[1:]
            if digits.isdigit():
                return int(sign + digits)
            return None
        if raw.isdigit():
            return int(raw)
        return None
    return None


def _hs04_safety(output_dir: Path, events: list[dict[str, Any]]) -> bool:
    for event in events:
        meta = event.get("metadata") if isinstance(event.get("metadata"), dict) else {}
        err = meta.get("model_error")
        if isinstance(err, str) and "unsafe" in err.lower():
            return False
    sg_path = output_dir / "static_gates_report.json"
    if not sg_path.is_file():
        return True
    try:
        sg = json.loads(sg_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False
    if sg.get("schema_version") != "1.0":
        return True
    passed_all = sg.get("passed_all")
    if not isinstance(passed_all, bool):
        return False
    return passed_all


def _hs05_lineage(output_dir: Path, events: list[dict[str, Any]], run_status: str) -> bool:
    orch = output_dir / "orchestration.jsonl"
    traces_ok = (output_dir / "traces.jsonl").is_file()
    orch_ok = orch.is_file()
    if run_status != "ok":
        return traces_ok and len(events) > 0
    return traces_ok and orch_ok and len(events) > 0


def _token_context_window_unexpired(token_context: dict[str, Any]) -> bool:
    raw = token_context.get("context_expires_at")
    if not isinstance(raw, str) or not raw.strip():
        return True
    exp = parse_iso_utc(raw.strip())
    if exp is None:
        return False
    return exp >= datetime.now(timezone.utc)


def _hs06_token_budgets(token_context: dict[str, Any]) -> bool:
    for st in token_context.get("stages") or []:
        if not isinstance(st, dict):
            return False
        if st.get("budget_status") == "fail_closed":
            return False
        actual_input = _safe_int(st.get("actual_input_tokens", 0))
        input_budget = _safe_int(st.get("input_token_budget", 0))
        actual_output = _safe_int(st.get("actual_output_tokens", 0))
        output_budget = _safe_int(st.get("output_token_budget", 0))
        if None in (actual_input, input_budget, actual_output, output_budget):
            return False
        if actual_input > input_budget:
            return False
        if actual_output > output_budget:
            return False
    return _token_context_window_unexpired(token_context)


def evaluate_hard_stops(
    output_dir: Path,
    events: list[dict[str, Any]],
    token_context: dict[str, Any],
    *,
    run_status: str,
    mode: str = "baseline",
) -> list[dict[str, Any]]:
    """Evaluate HS01–HS32; which IDs appear matches ``hard_stop_schedule.expected_hard_stop_ids``."""
    results: list[dict[str, Any]] = []
    results.append({"id": "HS01", "passed": _hs01_review(output_dir), "evidence_ref": "review.json"})

    tc_path = output_dir / "token_context.json"
    hs02 = tc_path.is_file() and token_context.get("schema_version") == TOKEN_CONTEXT_SCHEMA
    results.append({"id": "HS02", "passed": hs02, "evidence_ref": "token_context.json"})

    results.append({"id": "HS03", "passed": _hs03_truncation_ok(token_context), "evidence_ref": "token_context.json#truncation"})

    results.append(
        {
            "id": "HS04",
            "passed": _hs04_safety(output_dir, events),
            "evidence_ref": "traces.jsonl+static_gates_report.json",
        }
    )

    results.append(
        {
            "id": "HS05",
            "passed": _hs05_lineage(output_dir, events, run_status),
            "evidence_ref": "orchestration.jsonl",
        }
    )

    results.append(
        {
            "id": "HS06",
            "passed": _hs06_token_budgets(token_context),
            "evidence_ref": "token_context.json#budgets+expiry",
        }
    )
    if mode in ("guarded_pipeline", "phased_pipeline"):
        results.extend(evaluate_guarded_hard_stops(output_dir, events))
    results.extend(evaluate_event_lineage_hard_stops(output_dir, events))
    results.extend(evaluate_memory_hard_stops(output_dir))
    results.extend(evaluate_evolution_hard_stops(output_dir))
    results.extend(evaluate_organization_hard_stops(output_dir))
    return results
