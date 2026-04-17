"""Hard-stop checks HS01–HS06 from on-disk evidence."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .constants import REQUIRED_REVIEW_KEYS, TOKEN_CONTEXT_SCHEMA


def evaluate_hard_stops(
    output_dir: Path,
    events: list[dict[str, Any]],
    token_context: dict[str, Any],
    *,
    run_status: str,
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    review_path = output_dir / "review.json"
    hs01 = False
    if review_path.is_file():
        try:
            body = json.loads(review_path.read_text(encoding="utf-8"))
            hs01 = REQUIRED_REVIEW_KEYS.issubset(body.keys())
        except json.JSONDecodeError:
            hs01 = False
    results.append({"id": "HS01", "passed": hs01, "evidence_ref": "review.json"})

    tc_path = output_dir / "token_context.json"
    hs02 = tc_path.is_file() and token_context.get("schema_version") == TOKEN_CONTEXT_SCHEMA
    results.append({"id": "HS02", "passed": hs02, "evidence_ref": "token_context.json"})

    trunc = token_context.get("truncation_events") or []
    reds = token_context.get("reductions") or []
    hs03 = len(trunc) == 0 or (
        len(reds) > 0
        and all(
            any(r.get("provenance_id") == t.get("provenance_id") for r in reds)
            for t in trunc
            if isinstance(t, dict)
        )
    )
    results.append({"id": "HS03", "passed": hs03, "evidence_ref": "token_context.json#truncation"})

    hs04 = True
    for event in events:
        meta = event.get("metadata") if isinstance(event.get("metadata"), dict) else {}
        err = meta.get("model_error")
        if isinstance(err, str) and "unsafe" in err.lower():
            hs04 = False
            break
    results.append({"id": "HS04", "passed": hs04, "evidence_ref": "traces.jsonl"})

    orch = output_dir / "orchestration.jsonl"
    orch_ok = orch.is_file()
    traces_ok = (output_dir / "traces.jsonl").is_file()
    hs05 = traces_ok and orch_ok and len(events) > 0
    if run_status != "ok":
        hs05 = traces_ok and len(events) > 0
    results.append({"id": "HS05", "passed": hs05, "evidence_ref": "orchestration.jsonl"})

    hs06 = True
    for st in token_context.get("stages") or []:
        if not isinstance(st, dict):
            continue
        if st.get("budget_status") == "fail_closed":
            hs06 = False
            break
        if int(st.get("actual_input_tokens", 0)) > int(st.get("input_token_budget", 0)):
            hs06 = False
            break
        if int(st.get("actual_output_tokens", 0)) > int(st.get("output_token_budget", 0)):
            hs06 = False
            break
    results.append({"id": "HS06", "passed": hs06, "evidence_ref": "token_context.json#stages"})
    return results
