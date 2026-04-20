# Folder: `src/guardrails_and_safety/review_gating_evaluator_authority`

## Why this folder exists
Implements master-architecture §11.A Review Gating + Evaluator Authority for the local repository scope.

## What is present
- `review_gating` (folder): Builds/validates `review.json`, enforces evaluator-pass eligibility, and validates run-directory review gates.
- `safeguards` (folder): Validates task payload/output structure and applies unsafe-action refusal policy used by review/eval flow.
- `__init__.py` (file): Exposes the public Python surface for this subheading boundary.

## Notes
- Tests are intentionally colocated at the deepest module leaves:
  - `review_gating/tests` for review gate behavior
  - `safeguards/tests` for safeguard behavior
