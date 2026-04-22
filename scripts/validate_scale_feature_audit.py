#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
AUDIT_DIR = ROOT / "docs" / "versions" / "2026-04-22-scale-feature-audit"
EXPECTED_FEATURE_DOCS = 24


def _count_checkboxes(section_text: str) -> int:
    return len(re.findall(r"^- \[[ x]\] ", section_text, flags=re.MULTILINE))


def _extract_section(text: str, heading: str) -> str:
    pattern = rf"## {re.escape(heading)}\n(.*?)(?:\n## |\Z)"
    match = re.search(pattern, text, flags=re.DOTALL)
    return match.group(1).strip() if match else ""


def validate() -> list[str]:
    errors: list[str] = []
    if not AUDIT_DIR.exists():
        return [f"Missing audit directory: {AUDIT_DIR}"]

    docs = sorted(
        [
            p
            for p in AUDIT_DIR.glob("*.md")
            if p.name not in {"README.md", "production-grade-audit-prompt.md"}
        ]
    )
    if len(docs) != EXPECTED_FEATURE_DOCS:
        errors.append(
            f"Expected {EXPECTED_FEATURE_DOCS} feature docs, found {len(docs)}"
        )

    required_headings = [
        "Audit scores",
        "Agent A reviewed missing checklist",
        "Agent B reviewed missing checklist",
        "Confirmed missing (both audits)",
        "Review method",
    ]

    for doc in docs:
        text = doc.read_text(encoding="utf-8")
        for heading in required_headings:
            if f"## {heading}" not in text:
                errors.append(f"{doc.name}: missing heading `## {heading}`")

        a_section = _extract_section(text, "Agent A reviewed missing checklist")
        b_section = _extract_section(text, "Agent B reviewed missing checklist")
        c_section = _extract_section(text, "Confirmed missing (both audits)")
        if _count_checkboxes(a_section) < 8:
            errors.append(f"{doc.name}: Agent A checklist has fewer than 8 items")
        if _count_checkboxes(b_section) < 8:
            errors.append(f"{doc.name}: Agent B checklist has fewer than 8 items")
        if _count_checkboxes(c_section) < 8:
            errors.append(
                f"{doc.name}: Confirmed missing checklist has fewer than 8 items"
            )

    return errors


def main() -> int:
    errors = validate()
    if errors:
        print("Scale feature audit validation failed:")
        for err in errors:
            print(f"- {err}")
        return 1
    print("Scale feature audit validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
