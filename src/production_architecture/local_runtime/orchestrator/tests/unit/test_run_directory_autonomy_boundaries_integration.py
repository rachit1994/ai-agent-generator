from __future__ import annotations

import json
from pathlib import Path

from guardrails_and_safety.review_gating_evaluator_authority.review_gating.run_directory import (
    validate_execution_run_directory,
)


def _valid_review() -> dict[str, object]:
    return {
        "schema_version": "1.1",
        "run_id": "rid-1",
        "status": "completed_review_pass",
        "reasons": [],
        "required_fixes": [],
        "gate_snapshot": {},
        "artifact_manifest": [],
        "review_findings": [],
        "completed_at": "2026-01-01T00:00:00Z",
    }


def _baseline_dir(tmp_path: Path) -> Path:
    out = tmp_path / "run"
    (out / "safety").mkdir(parents=True)
    (out / "outputs").mkdir(parents=True)
    (out / "outputs" / "a.txt").write_text("a", encoding="utf-8")
    (out / "outputs" / "b.txt").write_text("b", encoding="utf-8")
    (out / "summary.json").write_text(json.dumps({"runStatus": "ok", "balanced_gates": {}}), encoding="utf-8")
    (out / "token_context.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "run_id": "rid-1",
                "stages": [],
                "autonomy_anchor_at": "2030-01-01T00:00:00+00:00",
                "context_expires_at": "2030-01-01T01:00:00+00:00",
                "context_ttl_seconds": 3600,
            }
        ),
        encoding="utf-8",
    )
    (out / "review.json").write_text(json.dumps(_valid_review()), encoding="utf-8")
    (out / "traces.jsonl").write_text("", encoding="utf-8")
    (out / "safety" / "autonomy_boundaries_tokens_expiry.json").write_text(
        json.dumps(
            {
                "schema": "sde.autonomy_boundaries_tokens_expiry.v1",
                "schema_version": "1.0",
                "run_id": "rid-1",
                "token_context": {
                    "run_id": "rid-1",
                    "stages": [],
                    "autonomy_anchor_at": "2030-01-01T00:00:00+00:00",
                    "context_expires_at": "2030-01-01T01:00:00+00:00",
                    "context_ttl_seconds": 3600,
                },
                "evidence": {"token_context_ref": "token_context.json"},
            }
        ),
        encoding="utf-8",
    )
    return out


def test_run_directory_invalid_autonomy_artifact_surfaces_prefixed_error(tmp_path: Path, monkeypatch) -> None:
    out = _baseline_dir(tmp_path)
    (out / "safety" / "autonomy_boundaries_tokens_expiry.json").write_text(
        json.dumps({"schema": "bad"}),
        encoding="utf-8",
    )
    monkeypatch.setattr(
        "guardrails_and_safety.review_gating_evaluator_authority.review_gating.run_directory.all_required_execution_paths",
        lambda mode, output_dir: [],
    )
    monkeypatch.setattr(
        "guardrails_and_safety.review_gating_evaluator_authority.review_gating.run_directory.evaluate_hard_stops",
        lambda output_dir, events, token_ctx, run_status, mode: [],
    )
    result = validate_execution_run_directory(out, mode="baseline")
    assert "autonomy_boundaries_contract:autonomy_boundaries_schema" in result["errors"]


def test_run_directory_reports_missing_autonomy_artifact(tmp_path: Path, monkeypatch) -> None:
    out = _baseline_dir(tmp_path)
    (out / "safety" / "autonomy_boundaries_tokens_expiry.json").unlink()
    monkeypatch.setattr(
        "guardrails_and_safety.review_gating_evaluator_authority.review_gating.run_directory.evaluate_hard_stops",
        lambda output_dir, events, token_ctx, run_status, mode: [],
    )
    result = validate_execution_run_directory(out, mode="baseline")
    assert "missing:safety/autonomy_boundaries_tokens_expiry.json" in result["errors"]


def test_run_directory_rejects_autonomy_run_id_mismatch(tmp_path: Path, monkeypatch) -> None:
    out = _baseline_dir(tmp_path)
    body = json.loads((out / "safety" / "autonomy_boundaries_tokens_expiry.json").read_text(encoding="utf-8"))
    body["run_id"] = "rid-other"
    (out / "safety" / "autonomy_boundaries_tokens_expiry.json").write_text(json.dumps(body), encoding="utf-8")
    monkeypatch.setattr(
        "guardrails_and_safety.review_gating_evaluator_authority.review_gating.run_directory.evaluate_hard_stops",
        lambda output_dir, events, token_ctx, run_status, mode: [],
    )
    result = validate_execution_run_directory(out, mode="baseline")
    assert "autonomy_boundaries_contract:autonomy_boundaries_run_id_mismatch" in result["errors"]


def test_run_directory_rejects_missing_autonomy_token_context_ref_target(
    tmp_path: Path, monkeypatch
) -> None:
    out = _baseline_dir(tmp_path)
    (out / "token_context.json").unlink()
    monkeypatch.setattr(
        "guardrails_and_safety.review_gating_evaluator_authority.review_gating.run_directory.evaluate_hard_stops",
        lambda output_dir, events, token_ctx, run_status, mode: [],
    )
    result = validate_execution_run_directory(out, mode="baseline")
    assert (
        "autonomy_boundaries_contract:autonomy_boundaries_evidence_ref_missing:token_context_ref"
        in result["errors"]
    )


def test_run_directory_rejects_non_canonical_autonomy_token_context_ref(
    tmp_path: Path, monkeypatch
) -> None:
    out = _baseline_dir(tmp_path)
    body = json.loads((out / "safety" / "autonomy_boundaries_tokens_expiry.json").read_text(encoding="utf-8"))
    body["evidence"]["token_context_ref"] = "./token_context.json"
    (out / "safety" / "autonomy_boundaries_tokens_expiry.json").write_text(json.dumps(body), encoding="utf-8")
    monkeypatch.setattr(
        "guardrails_and_safety.review_gating_evaluator_authority.review_gating.run_directory.evaluate_hard_stops",
        lambda output_dir, events, token_ctx, run_status, mode: [],
    )
    result = validate_execution_run_directory(out, mode="baseline")
    assert "autonomy_boundaries_contract:autonomy_boundaries_evidence_ref:token_context_ref" in result["errors"]


def test_run_directory_rejects_autonomy_token_context_payload_mismatch(
    tmp_path: Path, monkeypatch
) -> None:
    out = _baseline_dir(tmp_path)
    body = json.loads((out / "safety" / "autonomy_boundaries_tokens_expiry.json").read_text(encoding="utf-8"))
    body["token_context"]["context_ttl_seconds"] = 7200
    (out / "safety" / "autonomy_boundaries_tokens_expiry.json").write_text(json.dumps(body), encoding="utf-8")
    monkeypatch.setattr(
        "guardrails_and_safety.review_gating_evaluator_authority.review_gating.run_directory.evaluate_hard_stops",
        lambda output_dir, events, token_ctx, run_status, mode: [],
    )
    result = validate_execution_run_directory(out, mode="baseline")
    assert "autonomy_boundaries_contract:autonomy_boundaries_token_context_mismatch" in result["errors"]
