"""Schema versions and static gate contracts."""

from __future__ import annotations

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
