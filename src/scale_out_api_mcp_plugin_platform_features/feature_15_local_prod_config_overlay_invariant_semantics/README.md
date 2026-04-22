# Feature 15: local/prod config overlay with invariant semantics

This folder contains isolated config-overlay invariant gate logic.

## Components
- `runtime.py`: shared-schema, deterministic overlay precedence, invariant/fail-fast, drift, override-allowlist, secret, migration, and adapter test checks.
- `contracts.py`: strict report contract and evidence refs.
- `__init__.py`: exported package API.

## Gate behavior
- Enforces one schema for local/prod, deterministic overlay resolution, invariant fail-fast semantics, drift detection, safe overrides, secret handling, versioned migration readiness, and adapter coverage checks.
- Blocks release on any failed config-overlay gate check.
- Uses one executable command for `preflight` and `ci`.
