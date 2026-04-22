# Feature 05: edge admission control (rate limits + Retry-After)

This folder contains isolated edge admission control gate logic.

## Components
- `runtime.py`: admission checks for scope keys, budgets, Retry-After semantics, metrics, outage policy, and policy updates.
- `contracts.py`: strict gate report contract.
- `__init__.py`: exported package interface.

## Gate behavior
- Enforces 429 + Retry-After semantics and scoped limit policy invariants.
- Requires burst+sustained budgets, limiter counters, outage policy, and runtime-safe policy updates.
- Runs as one executable command for both `preflight` and `ci`.
