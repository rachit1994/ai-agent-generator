# Feature 02: local and server semantic parity enforcement

This folder contains isolated parity enforcement logic for local and server runtime semantics.

## Components
- `runtime.py`: parity matrix, drift detection, gate evaluation, history snapshots.
- `contracts.py`: strict report contract with canonical evidence paths.
- `__init__.py`: exported API surface.

## Gate behavior
- Compares local vs server semantics for idempotency, authz, state transitions, and error taxonomy.
- Marks release as blocked on any parity drift.
- Supports both `preflight` and `ci` modes using one executable command.
