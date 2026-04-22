#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from scale_out_api_mcp_plugin_platform_features.feature_21_artifact_keying_parity_local_mirror_object_store import (
    build_artifact_key_schema_contract,
    evaluate_artifact_key_parity_gate,
    update_artifact_key_parity_history,
    validate_artifact_key_parity_report_dict,
)


def _read_json(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Feature 21 artifact key parity gate")
    parser.add_argument("--mode", choices=["ci", "preflight"], required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--local-index", required=True)
    parser.add_argument("--object-index", required=True)
    parser.add_argument("--migration", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--history", required=True)
    args = parser.parse_args()
    report = evaluate_artifact_key_parity_gate(
        run_id=args.run_id,
        mode=args.mode,
        local_index=_read_json(Path(args.local_index)),
        object_index=_read_json(Path(args.object_index)),
        migration=_read_json(Path(args.migration)),
    )
    errors = validate_artifact_key_parity_report_dict(report)
    if errors:
        print("artifact key parity contract invalid:")
        for error in errors:
            print(f"- {error}")
        return 2
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    contract_path = out_path.parent / "artifact_key_schema_contract.json"
    contract_path.write_text(
        json.dumps(build_artifact_key_schema_contract(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    reconciliation_path = out_path.parent / "reconciliation_details.json"
    reconciliation_path.write_text(
        json.dumps(report["reconciliation"], indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    history_path = Path(args.history)
    existing = []
    if history_path.is_file():
        existing = [json.loads(line) for line in history_path.read_text(encoding="utf-8").splitlines() if line]
    updated = update_artifact_key_parity_history(existing=existing, report=report)
    history_path.parent.mkdir(parents=True, exist_ok=True)
    history_path.write_text("".join(f"{json.dumps(row, sort_keys=True)}\n" for row in updated), encoding="utf-8")
    return 0 if report["release_blocked"] is False else 1


if __name__ == "__main__":
    sys.exit(main())

