# Feature 08: distributed queue fairness (weighted scheduling)

Isolated gate implementation for weighted queue fairness readiness.

## Components
- `runtime.py`: evaluates weighted scheduling and fairness checks.
- `contracts.py`: validates report schema and evidence references.
- `__init__.py`: exports feature package API.

## Gate behavior
- Verifies distributed weighted queue coverage, tenant/plugin weights, starvation prevention, scheduler persistence/replay, fairness telemetry, safe policy tuning controls, mixed-load validation, and deterministic scheduler test coverage.
- Fails closed for any missing control.
