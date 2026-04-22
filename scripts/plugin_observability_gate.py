#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from scale_out_api_mcp_plugin_platform_features.feature_19_end_to_end_plugin_observability import (
    build_observability_event_rows,
    build_plugin_observability_contract,
    evaluate_plugin_observability_gate,
    update_plugin_observability_history,
    validate_plugin_observability_report_dict,
)


def _read_json(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must be a JSON object")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Feature 19 plugin observability gate")
    parser.add_argument("--mode", choices=["ci", "preflight"], required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--spans", required=True)
    parser.add_argument("--metrics", required=True)
    parser.add_argument("--retention", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--history", required=True)
    args = parser.parse_args()
    report = evaluate_plugin_observability_gate(
        run_id=args.run_id,
        mode=args.mode,
        spans=_read_json(Path(args.spans)),
        metrics=_read_json(Path(args.metrics)),
        retention_policy=_read_json(Path(args.retention)),
    )
    errors = validate_plugin_observability_report_dict(report)
    if errors:
        print("plugin observability contract invalid:")
        for error in errors:
            print(f"- {error}")
        return 2
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    contract_path = out_path.parent / "observability_contract.json"
    contract_path.write_text(
        json.dumps(build_plugin_observability_contract(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    events_path = out_path.parent / "observability_events.jsonl"
    events = build_observability_event_rows(report=report)
    events_path.write_text("".join(f"{json.dumps(row, sort_keys=True)}\n" for row in events), encoding="utf-8")
    history_path = Path(args.history)
    existing = []
    if history_path.is_file():
        existing = [json.loads(line) for line in history_path.read_text(encoding="utf-8").splitlines() if line]
    updated = update_plugin_observability_history(existing=existing, report=report)
    history_path.parent.mkdir(parents=True, exist_ok=True)
    history_path.write_text("".join(f"{json.dumps(row, sort_keys=True)}\n" for row in updated), encoding="utf-8")
    return 0 if report["release_blocked"] is False else 1


if __name__ == "__main__":
    sys.exit(main())

