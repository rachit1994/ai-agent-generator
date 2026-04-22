#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from scale_out_api_mcp_plugin_platform_features.feature_05_edge_admission_control_rate_limits_retry_after import (
    build_admission_event_rows,
    build_edge_policy_contract,
    evaluate_edge_admission_gate,
    update_edge_admission_history,
    validate_edge_admission_report_dict,
)


def _read_json(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must be a JSON object")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Feature 05 edge admission gate")
    parser.add_argument("--mode", choices=["ci", "preflight"], required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--policy", required=True)
    parser.add_argument("--counters", required=True)
    parser.add_argument("--traffic", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--history", required=True)
    args = parser.parse_args()
    report = evaluate_edge_admission_gate(
        run_id=args.run_id,
        mode=args.mode,
        policy=_read_json(Path(args.policy)),
        counters=_read_json(Path(args.counters)),
        traffic_sample=_read_json(Path(args.traffic)),
    )
    errors = validate_edge_admission_report_dict(report)
    if errors:
        print("edge admission contract invalid:")
        for error in errors:
            print(f"- {error}")
        return 2
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    contract_path = out_path.parent / "policy_contract.json"
    contract_path.write_text(
        json.dumps(build_edge_policy_contract(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    events_path = out_path.parent / "admission_events.jsonl"
    event_rows = build_admission_event_rows(report=report)
    events_path.write_text("".join(f"{json.dumps(row, sort_keys=True)}\n" for row in event_rows), encoding="utf-8")
    history_path = Path(args.history)
    existing = []
    if history_path.is_file():
        existing = [json.loads(line) for line in history_path.read_text(encoding="utf-8").splitlines() if line]
    updated = update_edge_admission_history(existing=existing, report=report)
    history_path.parent.mkdir(parents=True, exist_ok=True)
    history_path.write_text("".join(f"{json.dumps(row, sort_keys=True)}\n" for row in updated), encoding="utf-8")
    return 0 if report["release_blocked"] is False else 1


if __name__ == "__main__":
    sys.exit(main())

