"""Write deterministic storage architecture artifact."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from production_architecture.storage import (
    STORAGE_CONTRACT_ERROR_PREFIX,
    build_storage_architecture,
    validate_storage_architecture_dict,
)
from production_architecture.storage.config import load_storage_backend_config
from production_architecture.storage.errors import STORAGE_BACKEND_UNAVAILABLE, fail
from production_architecture.storage.storage.storage import ensure_dir, write_json


def _read_json_or_empty(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    body = json.loads(path.read_text(encoding="utf-8"))
    return body if isinstance(body, dict) else {}


def _read_jsonl_or_empty(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if isinstance(row, dict):
            rows.append(row)
    return rows


def _connect_postgres(dsn: str) -> Any:
    try:
        import psycopg  # type: ignore
    except Exception as exc:
        raise fail(STORAGE_BACKEND_UNAVAILABLE, "psycopg is required for postgres storage mode") from exc
    try:
        return psycopg.connect(dsn, autocommit=False)
    except Exception as exc:
        raise fail(STORAGE_BACKEND_UNAVAILABLE, f"postgres connection failed: {exc}") from exc


def _derive_from_postgres(*, dsn: str, run_id: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any], dict[str, Any]]:
    conn = _connect_postgres(dsn)
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT event_id,event_type,payload_sha256,created_at,run_id FROM pa_events WHERE run_id = %s ORDER BY event_seq ASC",
                (run_id,),
            )
            event_rows = cur.fetchall()
            cur.execute(
                "SELECT chunk_id,content,confidence,metadata_json FROM pa_vectors WHERE run_id = %s ORDER BY chunk_id ASC",
                (run_id,),
            )
            vector_rows = cur.fetchall()
            cur.execute(
                "SELECT summary_json FROM pa_projection_run_state WHERE run_id = %s",
                (run_id,),
            )
            projection_row = cur.fetchone()
    except Exception as exc:
        raise fail(STORAGE_BACKEND_UNAVAILABLE, f"postgres query failed: {exc}") from exc
    finally:
        conn.close()
    event_envelopes = [
        {
            "run_id": row[4],
            "payload": {
                "event_id": row[0],
                "type": row[1],
                "sha256": row[2],
                "created_at": str(row[3]),
            },
        }
        for row in event_rows
    ]
    retrieval_bundle = {
        "chunks": [
            {
                "chunk_id": row[0],
                "content": row[1],
                "confidence": float(row[2]),
                "metadata_json": row[3] if isinstance(row[3], dict) else {},
            }
            for row in vector_rows
        ]
    }
    quality_metrics: dict[str, Any] = {}
    if projection_row is not None and isinstance(projection_row[0], dict):
        quality_metrics = dict(projection_row[0])
    required_paths = [
        ("summary.json", projection_row is not None),
        ("review.json", True),
        ("event_store/run_events.jsonl", len(event_rows) > 0),
        ("replay_manifest.json", len(event_rows) > 0),
        ("memory/retrieval_bundle.json", len(vector_rows) > 0),
        ("memory/quality_metrics.json", projection_row is not None),
    ]
    artifact_manifest = [{"path": path, "present": present} for path, present in required_paths]
    return artifact_manifest, event_envelopes, retrieval_bundle, quality_metrics


def write_storage_architecture_artifact(
    *,
    output_dir: Path,
    run_id: str,
    mode: str,
) -> dict[str, Any]:
    cfg = load_storage_backend_config(runtime_mode=mode)
    artifact_manifest: list[dict[str, Any]]
    event_envelopes: list[dict[str, Any]]
    retrieval_bundle: dict[str, Any]
    quality_metrics: dict[str, Any]
    if cfg.mode == "postgres":
        artifact_manifest, event_envelopes, retrieval_bundle, quality_metrics = _derive_from_postgres(
            dsn=cfg.dsn,
            run_id=run_id,
        )
    else:
        review = _read_json_or_empty(output_dir / "review.json")
        manifest = review.get("artifact_manifest")
        artifact_manifest = manifest if isinstance(manifest, list) else []
        event_envelopes = _read_jsonl_or_empty(output_dir / "event_store" / "run_events.jsonl")
        retrieval_bundle = _read_json_or_empty(output_dir / "memory" / "retrieval_bundle.json")
        quality_metrics = _read_json_or_empty(output_dir / "memory" / "quality_metrics.json")
    payload = build_storage_architecture(
        run_id=run_id,
        mode=mode,
        artifact_manifest=artifact_manifest,
        event_envelopes=event_envelopes,
        retrieval_bundle=retrieval_bundle,
        quality_metrics=quality_metrics,
    )
    errs = validate_storage_architecture_dict(payload)
    if errs:
        raise ValueError(f"{STORAGE_CONTRACT_ERROR_PREFIX}{','.join(errs)}")
    ensure_dir(output_dir / "storage")
    write_json(output_dir / "storage" / "storage_architecture.json", payload)
    return payload

