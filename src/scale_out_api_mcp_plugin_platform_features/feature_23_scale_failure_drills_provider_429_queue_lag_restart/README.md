# Feature 23: scale failure drills (provider 429, queue lag, restart)

Isolated gate implementation for scale reliability failure drills.

## Components
- `runtime.py`: evaluates drill health and release gating.
- `contracts.py`: validates report structure and evidence refs.
- `__init__.py`: exports feature APIs.

## Gate behavior
- Checks executable drill framework signals, provider 429 + queue lag simulation coverage, restart/crash simulation, SLO-based pass/fail assertions, trend persistence, CI/nightly automation, regression alerting, and remediation verification.
- Fails closed when any expected capability signal is missing.
