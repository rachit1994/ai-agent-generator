# Folder: `src/guardrails_and_safety/review_gating_evaluator_authority/safeguards/tests`

## Why this folder exists
Provides leaf-level behavioral proof for safeguard logic used by review/evaluator authority.

## What is present
- `test_safeguards_positive.py` (file): Positive-path tests for accepted payloads, safe classification, and valid structured outputs.
- `test_safeguards_negative.py` (file): Negative-path tests for invalid inputs, malformed outputs, and schema failure classification.

## Notes
- Positive and negative suites are split by design for clearer signal on failures.
