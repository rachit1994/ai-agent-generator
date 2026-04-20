# Folder: `src/guardrails_and_safety/review_gating_evaluator_authority/safeguards`

## Why this folder exists
Implements safeguard primitives used by review/evaluator flow: input validation, unsafe refusal, structured-output parsing, and failure classification.

## What is present
- `safeguards.py` (file): Core safeguard implementation for task text/payload validation and output contract normalization.
- `tests` (folder): Positive/negative leaf tests proving safeguard behavior and failure semantics.
- `__init__.py` (file): Package marker for safeguards leaf.

## Notes
- This folder is the authoritative safeguard implementation for this subheading.
