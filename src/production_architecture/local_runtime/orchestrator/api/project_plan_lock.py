"""Stage 1 plan-lock gate for project sessions (OSV-STORY-01)."""

from __future__ import annotations

from datetime import datetime
import hashlib
import json
from pathlib import Path
from typing import Any

from guardrails_and_safety.risk_budgets_permission_matrix.time_and_budget.time_util import iso_now

from .project_intake_util import intake_doc_review_errors, intake_merge_anchor_present
from .project_schema import read_json_dict, validate_project_plan

_LINEAGE_SCHEMA_VERSION = "1.0"
_REVIEWED_AT_SKEW_MAX_SEC = 300
_REVIEWER_IDENTITY_FILENAME = "reviewer_identity.json"
_ALLOWED_ATTESTATION_TYPES = {"local_stub", "agent_signature", "service_token"}
_LOCAL_STUB_ATTESTATION_TYPE = "local_stub"
_LINEAGE_MANIFEST_FILENAME = "lineage_manifest.json"


def _jsonl_has_object_rows(path: Path) -> bool:
    if not path.is_file():
        return False
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return False
    for line in lines:
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(row, dict):
            return True
    return False


def _nonempty_text_file(path: Path) -> bool:
    if not path.is_file():
        return False
    try:
        return bool(path.read_text(encoding="utf-8").strip())
    except OSError:
        return False


def _planner_actor_id(intake_dir: Path) -> str | None:
    try:
        body = read_json_dict(intake_dir / "planner_identity.json")
    except (OSError, ValueError, TypeError):
        return None
    aid = body.get("actor_id")
    if isinstance(aid, str) and aid.strip():
        return aid.strip()
    return None


def _reviewer_identity_actor_id(intake_dir: Path) -> str | None:
    try:
        body = read_json_dict(intake_dir / _REVIEWER_IDENTITY_FILENAME)
    except (OSError, ValueError, TypeError):
        return None
    aid = body.get("actor_id")
    role = body.get("role")
    if not (isinstance(aid, str) and aid.strip()):
        return None
    if not (isinstance(role, str) and role.strip() == "reviewer"):
        return None
    return aid.strip()


def _reviewer_identity_attestation_errors(
    intake_dir: Path,
    *,
    allow_local_stub_attestation: bool,
) -> list[str]:
    try:
        body = read_json_dict(intake_dir / _REVIEWER_IDENTITY_FILENAME)
    except (OSError, ValueError, TypeError):
        return ["reviewer_identity_missing_or_unreadable"]
    errs: list[str] = []
    attestation_type = body.get("attestation_type")
    if not isinstance(attestation_type, str) or not attestation_type.strip():
        errs.append("reviewer_identity_attestation_type_missing")
    elif attestation_type.strip() not in _ALLOWED_ATTESTATION_TYPES:
        errs.append("reviewer_identity_attestation_type_invalid")
    elif not allow_local_stub_attestation and attestation_type.strip() == _LOCAL_STUB_ATTESTATION_TYPE:
        errs.append("reviewer_identity_attestation_stub_disallowed")
    attestation = body.get("attestation")
    if not isinstance(attestation, str) or not attestation.strip():
        errs.append("reviewer_identity_attestation_missing")
    reviewed_at = body.get("reviewed_at")
    if not isinstance(reviewed_at, str) or not reviewed_at.strip():
        errs.append("reviewer_identity_reviewed_at_missing")
    return errs


def _parse_iso_seconds(value: Any) -> int | None:
    if not isinstance(value, str) or not value.strip():
        return None
    txt = value.strip()
    if txt.endswith("Z"):
        txt = txt[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(txt)
    except ValueError:
        return None
    return int(dt.timestamp())


def _reviewed_at_consistency_errors(doc: dict[str, Any], intake_dir: Path) -> list[str]:
    try:
        rid = read_json_dict(intake_dir / _REVIEWER_IDENTITY_FILENAME)
    except (OSError, ValueError, TypeError):
        return []
    doc_reviewed_at = _parse_iso_seconds(doc.get("reviewed_at"))
    rid_reviewed_at = _parse_iso_seconds(rid.get("reviewed_at"))
    errs: list[str] = []
    if doc_reviewed_at is None:
        errs.append("doc_review_reviewed_at_missing_or_invalid")
    if rid_reviewed_at is None:
        errs.append("reviewer_identity_reviewed_at_invalid")
    if doc_reviewed_at is not None and rid_reviewed_at is not None:
        skew = abs(doc_reviewed_at - rid_reviewed_at)
        if skew > _REVIEWED_AT_SKEW_MAX_SEC:
            errs.append("reviewed_at_mismatch_exceeds_skew")
    return errs


def _reviewer_proof_summary(
    doc: dict[str, Any],
    intake_dir: Path,
    *,
    allow_local_stub_attestation: bool,
) -> dict[str, Any]:
    try:
        rid = read_json_dict(intake_dir / _REVIEWER_IDENTITY_FILENAME)
    except (OSError, ValueError, TypeError):
        rid = None
    try:
        planner = read_json_dict(intake_dir / "planner_identity.json")
    except (OSError, ValueError, TypeError):
        planner = None
    doc_reviewer = doc.get("reviewer")
    reviewer_actor = rid.get("actor_id") if isinstance(rid, dict) else None
    planner_actor = planner.get("actor_id") if isinstance(planner, dict) else None
    att_type = rid.get("attestation_type") if isinstance(rid, dict) else None
    doc_reviewed_at = doc.get("reviewed_at")
    reviewer_reviewed_at = rid.get("reviewed_at") if isinstance(rid, dict) else None
    doc_ts = _parse_iso_seconds(doc_reviewed_at)
    rid_ts = _parse_iso_seconds(reviewer_reviewed_at)
    skew = abs(doc_ts - rid_ts) if doc_ts is not None and rid_ts is not None else None
    attestation_allowed = isinstance(att_type, str) and att_type.strip() in _ALLOWED_ATTESTATION_TYPES
    attestation_policy_ok = attestation_allowed and (
        allow_local_stub_attestation or att_type.strip() != _LOCAL_STUB_ATTESTATION_TYPE
    )
    return {
        "doc_review_reviewer": doc_reviewer if isinstance(doc_reviewer, str) else None,
        "reviewer_actor_id": reviewer_actor if isinstance(reviewer_actor, str) else None,
        "planner_actor_id": planner_actor if isinstance(planner_actor, str) else None,
        "attestation_type": att_type if isinstance(att_type, str) else None,
        "attestation_type_allowed": attestation_allowed,
        "local_stub_allowed": allow_local_stub_attestation,
        "attestation_policy_ok": attestation_policy_ok,
        "reviewer_matches_doc_review": (
            isinstance(doc_reviewer, str)
            and isinstance(reviewer_actor, str)
            and bool(doc_reviewer.strip())
            and bool(reviewer_actor.strip())
            and doc_reviewer.strip() == reviewer_actor.strip()
        ),
        "reviewer_differs_from_planner": (
            isinstance(reviewer_actor, str)
            and isinstance(planner_actor, str)
            and bool(reviewer_actor.strip())
            and bool(planner_actor.strip())
            and reviewer_actor.strip() != planner_actor.strip()
        ),
        "doc_reviewed_at_valid": doc_ts is not None,
        "reviewer_reviewed_at_valid": rid_ts is not None,
        "reviewed_at_skew_sec": skew,
        "reviewed_at_skew_ok": (skew is not None and skew <= _REVIEWED_AT_SKEW_MAX_SEC) if skew is not None else None,
    }


def _lineage_required_artifacts(*, require_revise_state: bool) -> list[str]:
    rels = [
        "intake/discovery.json",
        "intake/research_digest.md",
        "intake/question_workbook.jsonl",
        "intake/doc_review.json",
        "intake/planner_identity.json",
        "intake/reviewer_identity.json",
    ]
    if require_revise_state:
        rels.append("intake/revise_state.json")
    return rels


def _sha256_text_file(path: Path) -> str | None:
    if not path.is_file():
        return None
    try:
        body = path.read_bytes()
    except OSError:
        return None
    return hashlib.sha256(body).hexdigest()


def write_intake_lineage_manifest(
    session_dir: Path,
    *,
    require_revise_state: bool = True,
) -> dict[str, Any]:
    """Write ``intake/lineage_manifest.json`` for Stage 1 artifact hash lineage."""
    if not isinstance(require_revise_state, bool):
        return {
            "ok": False,
            "error": "require_revise_state_not_bool",
            "session_dir": str(session_dir),
        }
    session_dir = session_dir.resolve()
    if not session_dir.is_dir():
        return {"ok": False, "error": "session_dir_not_a_directory", "session_dir": str(session_dir)}
    intake_dir = session_dir / "intake"
    if not intake_dir.is_dir():
        return {"ok": False, "error": "intake_dir_missing", "session_dir": str(session_dir)}
    artifacts = _lineage_required_artifacts(require_revise_state=require_revise_state)
    hashes: dict[str, str] = {}
    missing: list[str] = []
    for rel in artifacts:
        digest = _sha256_text_file(session_dir / rel)
        if not digest:
            missing.append(rel)
            continue
        hashes[rel] = digest
    if missing:
        return {"ok": False, "error": "lineage_artifacts_missing_or_unreadable", "details": missing, "session_dir": str(session_dir)}
    manifest = {
        "schema_version": _LINEAGE_SCHEMA_VERSION,
        "created_at": iso_now(),
        "require_revise_state": require_revise_state,
        "artifacts": hashes,
    }
    path = intake_dir / _LINEAGE_MANIFEST_FILENAME
    path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return {"ok": True, "manifest_path": str(path), "artifact_count": len(hashes), "session_dir": str(session_dir)}


def lineage_manifest_session_event_snapshot(session_dir: Path) -> dict[str, Any]:
    """Compact lineage proof for ``session_events`` payloads (OSV-STORY-01 trace hook).

    When ``intake/lineage_manifest.json`` exists and is readable, exposes presence,
    schema metadata, artifact count, and the manifest file's own sha256 so audit
    trails can correlate session events with the hashed intake snapshot.
    """
    path = session_dir / "intake" / _LINEAGE_MANIFEST_FILENAME
    if not path.is_file():
        return {"intake_lineage_manifest_present": False}
    try:
        man = read_json_dict(path)
    except (OSError, ValueError, TypeError):
        return {"intake_lineage_manifest_present": False, "intake_lineage_manifest_unreadable": True}
    artifacts = man.get("artifacts")
    count: int | None = None
    if isinstance(artifacts, dict):
        count = len(artifacts)
    out: dict[str, Any] = {"intake_lineage_manifest_present": True}
    sv = man.get("schema_version")
    if isinstance(sv, str) and sv.strip():
        out["intake_lineage_manifest_schema_version"] = sv.strip()
    created = man.get("created_at")
    if isinstance(created, str) and created.strip():
        out["intake_lineage_manifest_created_at"] = created.strip()
    if count is not None:
        out["intake_lineage_manifest_artifact_count"] = count
    file_digest = _sha256_text_file(path)
    if file_digest:
        out["intake_lineage_manifest_file_sha256"] = file_digest
    return out


def _lineage_manifest_errors(session_dir: Path, *, require_revise_state: bool) -> list[str]:
    intake_dir = session_dir / "intake"
    try:
        man = read_json_dict(intake_dir / _LINEAGE_MANIFEST_FILENAME)
    except (OSError, ValueError, TypeError):
        return ["lineage_manifest_missing_or_unreadable"]
    artifacts = man.get("artifacts")
    if not isinstance(artifacts, dict):
        return ["lineage_manifest_artifacts_missing_or_invalid"]
    reasons: list[str] = []
    for rel in _lineage_required_artifacts(require_revise_state=require_revise_state):
        expected = artifacts.get(rel)
        if not isinstance(expected, str) or not expected.strip():
            reasons.append(f"lineage_entry_missing:{rel}")
            continue
        actual = _sha256_text_file(session_dir / rel)
        if not actual:
            reasons.append(f"lineage_artifact_missing_or_unreadable:{rel}")
            continue
        if actual != expected:
            reasons.append(f"lineage_hash_mismatch:{rel}")
    return reasons


def evaluate_project_plan_lock_readiness(
    session_dir: Path,
    *,
    require_revise_state: bool = True,
    allow_local_stub_attestation: bool = True,
) -> dict[str, Any]:
    """Evaluate whether Stage 1 intake + plan metadata are ready for lock."""
    if not isinstance(require_revise_state, bool):
        return {
            "ok": False,
            "ready": False,
            "error": "require_revise_state_not_bool",
            "session_dir": str(session_dir),
        }
    if not isinstance(allow_local_stub_attestation, bool):
        return {
            "ok": False,
            "ready": False,
            "error": "allow_local_stub_attestation_not_bool",
            "session_dir": str(session_dir),
        }
    session_dir = session_dir.resolve()
    if not session_dir.is_dir():
        return {
            "ok": False,
            "ready": False,
            "error": "session_dir_not_a_directory",
            "session_dir": str(session_dir),
        }
    intake_dir = session_dir / "intake"
    reasons: list[str] = []
    reviewer_summary: dict[str, Any] | None = None
    if not intake_dir.is_dir():
        reasons.append("intake_dir_missing")
    else:
        if not intake_merge_anchor_present(session_dir):
            reasons.append("intake_anchor_missing_or_invalid")
        if not _nonempty_text_file(intake_dir / "research_digest.md"):
            reasons.append("research_digest_missing_or_empty")
        if not _jsonl_has_object_rows(intake_dir / "question_workbook.jsonl"):
            reasons.append("question_workbook_missing_or_empty")
        dre = intake_doc_review_errors(session_dir)
        if dre:
            reasons.extend(dre)
        else:
            try:
                doc = read_json_dict(intake_dir / "doc_review.json")
            except (OSError, ValueError, TypeError):
                reasons.append("doc_review_missing_or_unreadable")
            else:
                reviewer_summary = _reviewer_proof_summary(
                    doc,
                    intake_dir,
                    allow_local_stub_attestation=allow_local_stub_attestation,
                )
                if doc.get("passed") is not True:
                    reasons.append("doc_review_not_passed")
                reviewer = doc.get("reviewer")
                if not isinstance(reviewer, str) or not reviewer.strip():
                    reasons.append("doc_review_reviewer_missing")
                reviewer_id = _reviewer_identity_actor_id(intake_dir)
                if reviewer_id is None:
                    reasons.append("reviewer_identity_missing_or_unreadable")
                elif isinstance(reviewer, str) and reviewer.strip() != reviewer_id:
                    reasons.append("doc_review_reviewer_identity_mismatch")
                reasons.extend(
                    _reviewer_identity_attestation_errors(
                        intake_dir,
                        allow_local_stub_attestation=allow_local_stub_attestation,
                    )
                )
                reasons.extend(_reviewed_at_consistency_errors(doc, intake_dir))
                planner_id = _planner_actor_id(intake_dir)
                if planner_id is None:
                    reasons.append("planner_identity_missing_or_unreadable")
                elif reviewer_id is not None and reviewer_id == planner_id:
                    reasons.append("reviewer_matches_planner_identity")
        if require_revise_state:
            try:
                rev = read_json_dict(intake_dir / "revise_state.json")
            except (OSError, ValueError, TypeError):
                reasons.append("revise_state_missing_or_unreadable")
            else:
                if rev.get("status") != "review_passed":
                    reasons.append("revise_state_not_review_passed")
        reasons.extend(_lineage_manifest_errors(session_dir, require_revise_state=require_revise_state))

    plan_path = session_dir / "project_plan.json"
    plan: dict[str, Any] | None = None
    if not plan_path.is_file():
        reasons.append("project_plan_missing")
    else:
        try:
            plan = read_json_dict(plan_path)
        except (OSError, ValueError, TypeError):
            reasons.append("project_plan_unreadable")
        else:
            perrs = validate_project_plan(plan)
            reasons.extend(perrs)
            steps = plan.get("steps")
            has_contract_step = False
            if isinstance(steps, list):
                for i, row in enumerate(steps):
                    if not isinstance(row, dict):
                        continue
                    sid = row.get("step_id")
                    sid_s = sid if isinstance(sid, str) and sid else f"idx{i}"
                    rb = row.get("rollback_hint")
                    if not isinstance(rb, str) or not rb.strip():
                        reasons.append(f"project_plan_rollback_hint_missing:{sid_s}")
                    if row.get("contract_step") is True:
                        has_contract_step = True
            if not has_contract_step:
                reasons.append("project_plan_contract_step_missing")

    out = {
        "ok": True,
        "ready": len(reasons) == 0,
        "session_dir": str(session_dir),
        "reasons": reasons,
        "require_revise_state": require_revise_state,
        "allow_local_stub_attestation": allow_local_stub_attestation,
    }
    if isinstance(reviewer_summary, dict):
        out["reviewer_proof_summary"] = reviewer_summary
    return out


def write_project_plan_lock(
    session_dir: Path,
    *,
    require_revise_state: bool = True,
    allow_local_stub_attestation: bool = True,
) -> dict[str, Any]:
    """Write ``project_plan_lock.json`` with the readiness verdict; lock when ready."""
    if not isinstance(require_revise_state, bool):
        return {
            "ok": False,
            "error": "require_revise_state_not_bool",
            "session_dir": str(session_dir),
        }
    if not isinstance(allow_local_stub_attestation, bool):
        return {
            "ok": False,
            "error": "allow_local_stub_attestation_not_bool",
            "session_dir": str(session_dir),
        }
    lineage = write_intake_lineage_manifest(
        session_dir,
        require_revise_state=require_revise_state,
    )
    if not lineage.get("ok"):
        return lineage
    verdict = evaluate_project_plan_lock_readiness(
        session_dir,
        require_revise_state=require_revise_state,
        allow_local_stub_attestation=allow_local_stub_attestation,
    )
    if not verdict.get("ok"):
        return verdict
    session_dir = Path(verdict["session_dir"])
    lock_path = session_dir / "project_plan_lock.json"
    body: dict[str, Any] = {
        "schema_version": "1.0",
        "ready": bool(verdict.get("ready")),
        "require_revise_state": bool(verdict.get("require_revise_state")),
        "allow_local_stub_attestation": bool(verdict.get("allow_local_stub_attestation", True)),
        "reasons": list(verdict.get("reasons") or []),
        "reviewer_proof_summary": (
            verdict.get("reviewer_proof_summary")
            if isinstance(verdict.get("reviewer_proof_summary"), dict)
            else None
        ),
        "updated_at": iso_now(),
    }
    if body["ready"]:
        body["locked"] = True
        body["locked_at"] = iso_now()
    else:
        body["locked"] = False
    lock_path.write_text(json.dumps(body, indent=2), encoding="utf-8")
    verdict["lock_path"] = str(lock_path)
    verdict["locked"] = bool(body["locked"])
    return verdict
