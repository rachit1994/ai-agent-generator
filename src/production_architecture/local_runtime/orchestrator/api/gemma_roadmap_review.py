"""Support-model (Gemma) roadmap review: V1–V7 completion estimate and learning line."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from production_architecture.local_runtime.model_adapter.model_adapter import invoke_model
from workflow_pipelines.strategy_overlay.execution_modes.modes.guarded_pipeline.verify_core import extract_json_object
from workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.config import DEFAULT_CONFIG

_DEFAULT_CONTEXT_FILES = (
    "docs/UNDERSTANDING-THE-CODE.md",
    "docs/architecture/master-architecture-feature-completion.md",
)

_REVIEW_PROMPT_HEAD = """You are the independent support reviewer (same role as SDE support_model).
You must read ONLY the excerpted specification files below — do not invent shipped features that are not described there.

Score how completely THIS repository implements the SDE roadmap versions V1–V7 **as described in the excerpts** (harness vs full product is OK to distinguish).

Return ONLY a single JSON object (no markdown fences) with exactly these keys:
- "per_version_pct": object with string keys "V1","V2","V3","V4","V5","V6","V7" and integer values 0-100 each
- "overall_pct": integer 0-100 (your honest rollup)
- "code_quality_0_100": integer 0-100 for clarity/maintainability of what is implemented (infer from structure described)
- "done": array of short strings (concrete capabilities present)
- "remaining": array of short strings (largest gaps to "fullest" product in the docs)
- "learning_note": one sentence capturing the main lesson for the team

Context excerpts follow.

"""


def _gather_context(repo_root: Path, extra_doc_paths: list[str] | None) -> str:
    paths = list(extra_doc_paths) if extra_doc_paths else list(_DEFAULT_CONTEXT_FILES)
    chunks: list[str] = []
    for rel in paths:
        p = (repo_root / rel).resolve()
        if not p.is_file():
            chunks.append(f"### FILE: {rel}\n<missing on disk>\n")
            continue
        text = p.read_text(encoding="utf-8")
        if len(text) > 14_000:
            text = text[:14_000] + "\n…[truncated]\n"
        chunks.append(f"### FILE: {rel}\n{text}")
    return "\n\n".join(chunks)


def roadmap_review(
    *,
    repo_root: Path | None = None,
    extra_doc_paths: list[str] | None = None,
) -> dict[str, Any]:
    """Call support_model (default Gemma) with roadmap context; return structured review or parse error."""
    root = repo_root or Path.cwd()
    cfg = DEFAULT_CONFIG
    context = _gather_context(root, extra_doc_paths)
    prompt = _REVIEW_PROMPT_HEAD + context
    started = int(time.time() * 1000)
    resp = invoke_model(
        prompt=prompt,
        model=cfg.support_model,
        provider=cfg.provider,
        provider_base_url=cfg.provider_base_url,
        timeout_ms=max(cfg.budgets.verifier_timeout_ms, 180_000),
        response_format="json",
        options={"num_predict": 512, "num_ctx": 8192, "num_thread": 2, "temperature": 0, "top_p": 1, "seed": 42},
        keep_alive="120s",
    )
    ended = int(time.time() * 1000)
    raw = str(resp.get("text", ""))
    base: dict[str, Any] = {
        "ok": False,
        "support_model": cfg.support_model,
        "model_error": resp.get("error"),
        "latency_ms": ended - started,
    }
    if resp.get("error"):
        base["error"] = "model_invoke_failed"
        base["raw_excerpt"] = raw[:800]
        return base
    try:
        review = extract_json_object(raw)
    except ValueError as exc:
        base["error"] = f"json_parse_failed:{exc}"
        base["raw_excerpt"] = raw[:1200]
        return base
    base["ok"] = True
    base["review"] = review
    return base


def append_roadmap_learning_line(path: Path, payload: dict[str, Any]) -> None:
    """Append one JSONL learning event (V2-style institutional memory)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    line = {
        "event_id": f"learn-roadmap-{int(time.time() * 1000)}",
        "type": "roadmap_review",
        "occurred_at_ms": int(time.time() * 1000),
        "payload": payload,
    }
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(line, ensure_ascii=False) + "\n")
