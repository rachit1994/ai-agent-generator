# Feature 11: plugin discovery/registry compatibility governance

This folder contains isolated plugin registry governance gate logic.

## Components
- `runtime.py`: registry/compatibility/governance checks.
- `contracts.py`: strict report contract and canonical evidence refs.
- `__init__.py`: exported package API.

## Gate behavior
- Enforces registry presence, metadata/version contracts, compatibility matrix automation, publish/rollout gating, deprecation+rollback governance, provenance/signature verification, governance history, and incompatible rejection test coverage.
- Blocks release on any failed governance gate check.
- Runs as one executable command in `preflight` and `ci`.
