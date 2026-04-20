"""Structural contract for ``strategy/proposal.json`` (§10 strategy overlay → production handoff, **HS32**)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Final

STRATEGY_OVERLAY_CONTRACT: Final = "sde.strategy_overlay_proposal.v1"


def _errs_schema_actor(body: dict[str, Any]) -> list[str]:
    sv = body.get("schema_version", body.get("schemaVersion"))
    if not isinstance(sv, str) or not sv.strip():
        return ["strategy_overlay_schema_version"]
    aid = body.get("actor_id", body.get("actorId"))
    if not isinstance(aid, str) or not aid.strip():
        return ["strategy_overlay_actor_id"]
    return []


def _errs_bool_flags(body: dict[str, Any]) -> list[str]:
    errs: list[str] = []
    if "requires_promotion_package" not in body or not isinstance(body.get("requires_promotion_package"), bool):
        errs.append("strategy_overlay_requires_promotion_package_type")
    if "applied_autonomy" not in body or not isinstance(body.get("applied_autonomy"), bool):
        errs.append("strategy_overlay_applied_autonomy_type")
    return errs


def _errs_hs32_combo(body: dict[str, Any]) -> list[str]:
    aa = body.get("applied_autonomy")
    rp = body.get("requires_promotion_package")
    if aa is True and rp is not True:
        return ["strategy_overlay_autonomy_requires_promotion"]
    return []


def _errs_proposal_ref(body: dict[str, Any]) -> list[str]:
    aa = body.get("applied_autonomy")
    rp = body.get("requires_promotion_package")
    need_ref = rp is True or aa is True
    if not need_ref:
        return []
    ref = body.get("proposal_ref", body.get("proposalRef"))
    if not isinstance(ref, str) or not ref.strip():
        return ["strategy_overlay_proposal_ref"]
    return []


def validate_strategy_proposal_dict(body: Any) -> list[str]:
    """Return stable error tokens; empty means HS32-compatible strategy proposal shape."""
    if not isinstance(body, dict):
        return ["strategy_overlay_not_object"]
    b = body
    errs: list[str] = []
    errs.extend(_errs_schema_actor(b))
    errs.extend(_errs_bool_flags(b))
    errs.extend(_errs_hs32_combo(b))
    errs.extend(_errs_proposal_ref(b))
    return errs


def validate_strategy_proposal_path(path: Path) -> list[str]:
    """Return stable error tokens for JSON on disk (no raise)."""
    if not path.is_file():
        return ["strategy_overlay_file_missing"]
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return ["strategy_overlay_unreadable"]
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return ["strategy_overlay_json"]
    return validate_strategy_proposal_dict(parsed)
