from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REVIEW_SCHEMA = "1.0"
TOKEN_CONTEXT_SCHEMA = "1.0"

REQUIRED_REVIEW_KEYS = frozenset(
    {
        "schema_version",
        "run_id",
        "status",
        "reasons",
        "required_fixes",
        "gate_snapshot",
        "artifact_manifest",
        "completed_at",
    }
)


def _iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def manifest_paths_for_review(mode: str) -> list[str]:
    """Paths checked in ``review.json`` artifact_manifest (before review file itself exists)."""
    base = [
        "traces.jsonl",
        "orchestration.jsonl",
        "report.md",
        "run.log",
        "answer.txt",
        "outputs/README.txt",
        "outputs/manifest.json",
    ]
    if mode == "guarded_pipeline":
        base.extend(
            [
                "planner_doc.md",
                "executor_prompt.txt",
                "verifier_report.json",
            ]
        )
    return base


def all_required_v1_paths(mode: str) -> list[str]:
    return [
        "summary.json",
        "review.json",
        "token_context.json",
        *manifest_paths_for_review(mode),
    ]


def _manifest_entries(output_dir: Path, relative_paths: list[str]) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for rel in relative_paths:
        p = output_dir / rel
        entries.append({"path": rel, "present": p.is_file() or p.is_dir()})
    return entries


def build_token_context(
    run_id: str,
    events: list[dict[str, Any]],
    *,
    max_tokens: int,
    model_context_limit: int = 8192,
) -> dict[str, Any]:
    policy_items = ["required_instructions", "recent_task_state", "historical_context"]
    policy_hash = hashlib.sha256("|".join(policy_items).encode()).hexdigest()[:16]
    stages_out: list[dict[str, Any]] = []
    for event in events:
        stage = str(event.get("stage", "unknown"))
        ti = int(event.get("token_input", 0) or 0)
        to = int(event.get("token_output", 0) or 0)
        meta = event.get("metadata") if isinstance(event.get("metadata"), dict) else {}
        planned_in = max(len(json.dumps(meta)) // 4, 1)
        budget_in = max_tokens
        budget_out = max_tokens
        over_in = ti > budget_in
        over_out = to > budget_out
        status = "fail_closed" if (over_in or over_out) else "ok"
        stages_out.append(
            {
                "name": stage,
                "input_token_budget": budget_in,
                "output_token_budget": budget_out,
                "planned_input_tokens": planned_in,
                "actual_input_tokens": ti,
                "actual_output_tokens": to,
                "budget_status": status,
            }
        )
    return {
        "schema_version": TOKEN_CONTEXT_SCHEMA,
        "run_id": run_id,
        "model_context_limit": model_context_limit,
        "stages": stages_out,
        "context_policy": {"priority": policy_items, "version_hash": policy_hash},
        "reductions": [],
        "truncation_events": [],
    }


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


def compute_balanced_gates(
    metrics: dict[str, Any],
    hard_stops: list[dict[str, Any]],
    *,
    review_status: str,
    manifest_complete: bool,
) -> dict[str, Any]:
    reliability = int(round(100 * float(metrics.get("reliability", 0))))
    reliability = max(0, min(100, reliability))
    delivery = 100 if review_status == "completed_review_pass" and manifest_complete else 70
    if review_status == "completed_review_fail":
        delivery = 60
    if review_status == "incomplete":
        delivery = 40
    governance = 100 if all(h.get("passed") for h in hard_stops) else 50
    governance = max(0, min(100, governance))
    composite = int(round((reliability + delivery + governance) / 3))
    return {
        "reliability": reliability,
        "delivery": delivery,
        "governance": governance,
        "composite": composite,
        "threshold_profile": "strict",
        "hard_stops": hard_stops,
    }


def build_review(
    run_id: str,
    mode: str,
    parsed: dict[str, Any],
    output_dir: Path,
    events: list[dict[str, Any]],
    *,
    run_status: str,
) -> dict[str, Any]:
    refusal = parsed.get("refusal")
    finals = [e for e in events if e.get("stage") == "finalize"]
    passed = bool(finals and finals[-1].get("score", {}).get("passed"))
    if run_status != "ok":
        status = "incomplete"
        reasons = [f"run_{run_status}"]
    elif isinstance(refusal, dict) and refusal.get("code") == "unsafe_action_refused":
        status = "completed_review_pass"
        reasons = ["safety_refusal_terminal"]
    elif passed:
        status = "completed_review_pass"
        reasons = []
    else:
        status = "completed_review_fail"
        reasons = ["verifier_or_checks_failed"]
    paths = manifest_paths_for_review(mode)
    manifest = _manifest_entries(output_dir, paths)
    manifest_complete = all(m["present"] for m in manifest)
    met = metrics_from_events(events)
    gate_snapshot = {
        "reliability": "pass" if reliability_gate(met) else "validating",
        "safety": "pass" if status in ("completed_review_pass",) or reasons == ["safety_refusal_terminal"] else "validating",
        "replay": "pass" if len(events) > 0 else "fail",
        "resource_budget": "validating",
        "token_context": "validating",
    }
    fixes: list[str] = []
    if not manifest_complete:
        fixes.append("restore_missing_artifacts")
    if status == "completed_review_fail":
        fixes.append("address_verifier_issues")
    return {
        "schema_version": REVIEW_SCHEMA,
        "run_id": run_id,
        "status": status,
        "reasons": reasons,
        "required_fixes": fixes,
        "gate_snapshot": gate_snapshot,
        "artifact_manifest": manifest,
        "completed_at": _iso_now(),
    }


def metrics_from_events(events: list[dict[str, Any]]) -> dict[str, Any]:
    from orchestrator.runtime.eval import aggregate_metrics

    return aggregate_metrics(events)


def reliability_gate(metrics: dict[str, Any]) -> bool:
    return float(metrics.get("reliability", 0)) >= 0.85


def validation_ready(balanced: dict[str, Any]) -> bool:
    if balanced["reliability"] < 85 or balanced["delivery"] < 85 or balanced["governance"] < 85:
        return False
    if balanced["composite"] < 90:
        return False
    return all(h.get("passed") for h in balanced.get("hard_stops", []))


def validate_execution_run_directory(output_dir: Path, *, mode: str) -> dict[str, Any]:
    """Quality gate for tests and CI: verify V1 artifact contract on a completed run directory."""
    errors: list[str] = []
    if not (output_dir / "summary.json").is_file():
        errors.append("missing_summary_json")
    summary = json.loads((output_dir / "summary.json").read_text(encoding="utf-8")) if not errors else {}
    if "balanced_gates" not in summary:
        errors.append("missing_balanced_gates")
    if not (output_dir / "review.json").is_file():
        errors.append("missing_review_json")
    if not (output_dir / "token_context.json").is_file():
        errors.append("missing_token_context_json")
    if not (output_dir / "outputs").is_dir():
        errors.append("missing_outputs_dir")
    out_files = list((output_dir / "outputs").glob("*")) if (output_dir / "outputs").is_dir() else []
    if len(out_files) < 2:
        errors.append("outputs_dir_needs_at_least_two_entries")
    for rel in all_required_v1_paths(mode):
        if not (output_dir / rel).exists():
            errors.append(f"missing:{rel}")
    events: list[dict[str, Any]] = []
    traces = output_dir / "traces.jsonl"
    if traces.is_file():
        events = [json.loads(line) for line in traces.read_text(encoding="utf-8").splitlines() if line.strip()]
    token_path = output_dir / "token_context.json"
    token_ctx = json.loads(token_path.read_text(encoding="utf-8")) if token_path.is_file() else {}
    hard = evaluate_hard_stops(output_dir, events, token_ctx, run_status=summary.get("runStatus", "ok"))
    ready = validation_ready(summary["balanced_gates"]) if summary.get("balanced_gates") else False
    strict_ok = ready and not errors
    return {"ok": strict_ok, "errors": errors, "hard_stops": hard, "validation_ready": ready}
