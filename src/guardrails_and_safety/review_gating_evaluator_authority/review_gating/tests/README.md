# Folder: `src/guardrails_and_safety/review_gating_evaluator_authority/review_gating/tests`

## Why this folder exists
Houses the leaf-level test contract for review-gating evaluator authority behavior.

## What is present
- `test_review_gating_positive.py` (file): Happy-path tests for valid review payloads, evaluator eligibility, and run-directory pass behavior.
- `test_review_gating_negative.py` (file): Failure-path tests for malformed payloads, blocker findings, and pass-ineligible review status.

## Notes
- Positive and negative coverage are intentionally split into separate files.
