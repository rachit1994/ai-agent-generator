"""Typed contracts and parser for canonical online evaluation records."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class TrafficSplitConfig:
    shadow_ratio: float
    canary_ratio: float


@dataclass(frozen=True)
class OnlineEvalRecord:
    request_id: str
    cohort: str
    baseline_latency_ms: float
    candidate_latency_ms: float
    baseline_outcome: bool
    candidate_outcome: bool
    baseline_quality: float
    candidate_quality: float


def _is_real_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value))


def _to_real_number(value: Any, *, field: str, row: int) -> float:
    if not _is_real_number(value):
        raise ValueError(f"online_eval_records_numeric:{field}:{row}")
    return float(value)


def validate_traffic_split_config(config: TrafficSplitConfig) -> None:
    if config.shadow_ratio < 0.0 or config.shadow_ratio > 1.0:
        raise ValueError("online_eval_traffic_split_shadow_ratio_range")
    if config.canary_ratio < 0.0 or config.canary_ratio > 1.0:
        raise ValueError("online_eval_traffic_split_canary_ratio_range")
    if (config.shadow_ratio + config.canary_ratio) > 1.0:
        raise ValueError("online_eval_traffic_split_ratio_sum")


def parse_online_eval_records_jsonl(path: Path) -> list[OnlineEvalRecord]:
    if not path.is_file():
        raise ValueError("online_eval_records_missing")
    rows = path.read_text(encoding="utf-8").splitlines()
    records: list[OnlineEvalRecord] = []
    request_ids: set[str] = set()
    for idx, raw_line in enumerate(rows, start=1):
        if not raw_line.strip():
            continue
        try:
            body = json.loads(raw_line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"online_eval_records_jsonl:{idx}") from exc
        if not isinstance(body, dict):
            raise ValueError(f"online_eval_records_row_not_object:{idx}")
        request_id = body.get("request_id")
        if not isinstance(request_id, str) or not request_id.strip():
            raise ValueError(f"online_eval_records_request_id:{idx}")
        if request_id in request_ids:
            raise ValueError(f"online_eval_records_duplicate_request_id:{request_id}")
        request_ids.add(request_id)
        cohort = body.get("cohort")
        if cohort not in ("shadow", "canary"):
            raise ValueError(f"online_eval_records_cohort:{idx}")
        baseline_outcome = body.get("baseline_outcome")
        candidate_outcome = body.get("candidate_outcome")
        if not isinstance(baseline_outcome, bool):
            raise ValueError(f"online_eval_records_baseline_outcome:{idx}")
        if not isinstance(candidate_outcome, bool):
            raise ValueError(f"online_eval_records_candidate_outcome:{idx}")
        baseline_latency_ms = _to_real_number(body.get("baseline_latency_ms"), field="baseline_latency_ms", row=idx)
        candidate_latency_ms = _to_real_number(body.get("candidate_latency_ms"), field="candidate_latency_ms", row=idx)
        baseline_quality = _to_real_number(body.get("baseline_quality"), field="baseline_quality", row=idx)
        candidate_quality = _to_real_number(body.get("candidate_quality"), field="candidate_quality", row=idx)
        if baseline_latency_ms < 0.0 or candidate_latency_ms < 0.0:
            raise ValueError(f"online_eval_records_latency_range:{idx}")
        if baseline_quality < 0.0 or baseline_quality > 1.0:
            raise ValueError(f"online_eval_records_baseline_quality_range:{idx}")
        if candidate_quality < 0.0 or candidate_quality > 1.0:
            raise ValueError(f"online_eval_records_candidate_quality_range:{idx}")
        records.append(
            OnlineEvalRecord(
                request_id=request_id,
                cohort=cohort,
                baseline_latency_ms=baseline_latency_ms,
                candidate_latency_ms=candidate_latency_ms,
                baseline_outcome=baseline_outcome,
                candidate_outcome=candidate_outcome,
                baseline_quality=baseline_quality,
                candidate_quality=candidate_quality,
            )
        )
    return records
