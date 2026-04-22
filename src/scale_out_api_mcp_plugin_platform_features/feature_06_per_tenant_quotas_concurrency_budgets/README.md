# Feature 06: per-tenant quotas and concurrency budgets

This folder contains isolated tenant-quota gate logic.

## Components
- `runtime.py`: per-tenant quota/concurrency/fairness/refill/rejection checks.
- `contracts.py`: strict report contract.
- `__init__.py`: exported package API.

## Gate behavior
- Enforces tenant identity propagation, durable quota state, hard concurrency ceilings, fairness policy, quota refill windows, and admin controls.
- Requires tenant-level observability and explicit over-quota rejection semantics.
- Runs as one executable command in `preflight` and `ci`.
