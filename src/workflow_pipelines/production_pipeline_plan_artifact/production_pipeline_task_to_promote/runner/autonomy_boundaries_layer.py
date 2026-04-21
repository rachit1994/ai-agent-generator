"""Write deterministic autonomy-boundaries artifact."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from guardrails_and_safety.autonomy_boundaries.autonomy_boundaries_tokens_expiry import (
    AUTONOMY_BOUNDARIES_ERROR_PREFIX,
    build_autonomy_boundaries_runtime_payload,
    validate_autonomy_boundaries_runtime_dict,
)
from production_architecture.storage.storage.storage import ensure_dir, write_json


def write_autonomy_boundaries_artifact(
    *,
    output_dir: Path,
    run_id: str,
    token_context: dict[str, Any],
    now_utc: datetime | None = None,
) -> dict[str, Any]:
    try:
        payload = build_autonomy_boundaries_runtime_payload(
            run_id=run_id,
            token_context=token_context,
            now_utc=now_utc or datetime.now(timezone.utc),
        )
    except ValueError as exc:
        raise ValueError(f"{AUTONOMY_BOUNDARIES_ERROR_PREFIX}{exc}") from exc
    errs = validate_autonomy_boundaries_runtime_dict(payload)
    if errs:
        raise ValueError(f"{AUTONOMY_BOUNDARIES_ERROR_PREFIX}{','.join(errs)}")
    ensure_dir(output_dir / "safety")
    write_json(output_dir / "safety" / "autonomy_boundaries_tokens_expiry.json", payload)
    return payload
