# Feature 22: progressive rollout/canary/rollback for plugin versions

Isolated gate implementation for plugin progressive rollout behavior.

## Components
- `runtime.py`: evaluates rollout/canary/rollback checks.
- `contracts.py`: validates report schema and evidence references.
- `__init__.py`: exports public feature APIs.

## Gate behavior
- Validates rollout controller availability, canary traffic cohorts, health-gated promotion, auto-rollback behavior, persisted rollout timeline, operator controls, lifecycle test coverage, and observability coupling.
- Fails closed for any missing capability signal.
