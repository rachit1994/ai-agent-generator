#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from scale_out_api_mcp_plugin_platform_features.feature_09_plugin_circuit_breakers_retry_budgets import (
    build_transition_event_rows,
    build_plugin_circuit_breaker_contract,
    evaluate_plugin_circuit_breaker_gate,
    update_plugin_circuit_breaker_history,
    validate_plugin_circuit_breaker_report_dict,
)


def _read_json(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Feature 09 plugin circuit breaker gate")
    parser.add_argument("--mode", choices=["ci", "preflight"], required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--runtime", required=True)
    parser.add_argument("--policy", required=True)
    parser.add_argument("--telemetry", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--history", required=True)
    args = parser.parse_args()
    report = evaluate_plugin_circuit_breaker_gate(
        run_id=args.run_id,
        mode=args.mode,
        runtime_state=_read_json(Path(args.runtime)),
        policy=_read_json(Path(args.policy)),
        telemetry=_read_json(Path(args.telemetry)),
    )
    errors = validate_plugin_circuit_breaker_report_dict(report)
    if errors:
        print("plugin circuit breaker contract invalid:")
        for error in errors:
            print(f"- {error}")
        return 2
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    contract_path = out_path.parent / "circuit_breaker_contract.json"
    contract_path.write_text(json.dumps(build_plugin_circuit_breaker_contract(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    events_path = out_path.parent / "transition_events.jsonl"
    events = build_transition_event_rows(report=report)
    events_path.write_text("".join(f"{json.dumps(row, sort_keys=True)}\n" for row in events), encoding="utf-8")
    history_path = Path(args.history)
    existing = []
    if history_path.is_file():
        existing = [json.loads(line) for line in history_path.read_text(encoding="utf-8").splitlines() if line]
    updated = update_plugin_circuit_breaker_history(existing=existing, report=report)
    history_path.parent.mkdir(parents=True, exist_ok=True)
    history_path.write_text("".join(f"{json.dumps(row, sort_keys=True)}\n" for row in updated), encoding="utf-8")
    return 0 if report["release_blocked"] is False else 1


if __name__ == "__main__":
    sys.exit(main())
