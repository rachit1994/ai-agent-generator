# Feature 03: control plane / data plane split

This folder contains isolated control-plane/data-plane split gate logic.

## Components
- `runtime.py`: boundary contract and split/isolation gate evaluation.
- `contracts.py`: strict report contract checks with canonical evidence paths.
- `__init__.py`: exported API for scripts and tests.

## Gate behavior
- Enforces separation of services, scaling policy, auth boundary, telemetry partitioning, and failure isolation.
- Blocks release on any failed split check.
- Runs from one executable command in both `preflight` and `ci` modes.
