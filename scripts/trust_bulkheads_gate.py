#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from scale_out_api_mcp_plugin_platform_features.feature_12_plugin_runtime_bulkheads_trust_class import (
    build_bulkhead_event_rows,
    build_trust_bulkhead_contract,
    evaluate_bulkheads_gate,
    update_bulkheads_history,
    validate_bulkheads_report_dict,
)


def _read_json(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must be a JSON object")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Feature 12 trust bulkheads gate")
    parser.add_argument("--mode", choices=["ci", "preflight"], required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--policy", required=True)
    parser.add_argument("--runtime", required=True)
    parser.add_argument("--telemetry", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--history", required=True)
    args = parser.parse_args()
    report = evaluate_bulkheads_gate(
        run_id=args.run_id,
        mode=args.mode,
        policy=_read_json(Path(args.policy)),
        runtime_state=_read_json(Path(args.runtime)),
        telemetry=_read_json(Path(args.telemetry)),
    )
    errors = validate_bulkheads_report_dict(report)
    if errors:
        print("trust bulkheads contract invalid:")
        for error in errors:
            print(f"- {error}")
        return 2
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    contract_path = out_path.parent / "bulkhead_contract.json"
    contract_path.write_text(
        json.dumps(build_trust_bulkhead_contract(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    events_path = out_path.parent / "bulkhead_events.jsonl"
    events = build_bulkhead_event_rows(report=report)
    events_path.write_text("".join(f"{json.dumps(row, sort_keys=True)}\n" for row in events), encoding="utf-8")
    history_path = Path(args.history)
    existing = []
    if history_path.is_file():
        existing = [json.loads(line) for line in history_path.read_text(encoding="utf-8").splitlines() if line]
    updated = update_bulkheads_history(existing=existing, report=report)
    history_path.parent.mkdir(parents=True, exist_ok=True)
    history_path.write_text("".join(f"{json.dumps(row, sort_keys=True)}\n" for row in updated), encoding="utf-8")
    return 0 if report["release_blocked"] is False else 1


if __name__ == "__main__":
    sys.exit(main())

