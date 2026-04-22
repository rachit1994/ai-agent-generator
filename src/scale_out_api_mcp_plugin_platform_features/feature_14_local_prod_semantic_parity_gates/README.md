# Feature 14: local vs production semantic parity gates

This folder contains isolated local-vs-production semantic parity gate logic.

## Components
- `runtime.py`: parity comparators and gate evaluation.
- `contracts.py`: strict report contract and evidence refs.
- `__init__.py`: exported package API.

## Gate behavior
- Enforces semantic output, state-transition, error, authz, and idempotency parity checks.
- Emits diagnostics and release-blocks on detected drift.
- Uses one executable command for `preflight` and `ci`.
