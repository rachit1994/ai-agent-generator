from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4


def create_run_id() -> str:
    stamp = datetime.now(timezone.utc).isoformat().replace(":", "-").replace(".", "-")
    return f"{stamp}-{uuid4().hex[:8]}"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
