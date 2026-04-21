"""Contracts for reviewer/evaluator local runtime."""

from __future__ import annotations

REVIEW_FINDING_REQUIRED_KEYS: tuple[str, str, str, str] = (
    "severity",
    "code",
    "message",
    "evidence_ref",
)
REVIEW_FINDING_SEVERITIES: frozenset[str] = frozenset({"blocker", "warn", "info"})
REVIEW_STATUSES: frozenset[str] = frozenset(
    {"completed_review_pass", "completed_review_fail", "incomplete"}
)


def review_finding_required_keys() -> tuple[str, str, str, str]:
    return REVIEW_FINDING_REQUIRED_KEYS


def allowed_finding_severities() -> frozenset[str]:
    return REVIEW_FINDING_SEVERITIES


def allowed_review_statuses() -> frozenset[str]:
    return REVIEW_STATUSES
