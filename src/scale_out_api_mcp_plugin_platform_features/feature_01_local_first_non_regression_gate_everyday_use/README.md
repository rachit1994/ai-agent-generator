# Feature 01: local-first non-regression gate

This folder contains an isolated, fail-closed local non-regression gate for scale work.

## Components
- `runtime.py`: deterministic gate derivation for startup/workflow/resource/SLO checks.
- `contracts.py`: strict artifact contract validation.
- `__init__.py`: exported API for tests and scripts.

## Inputs and outputs
- Inputs: current metrics + baseline metrics + mode (`ci` or `preflight`) + feature flag.
- Output: report artifact with binary gate status and canonical evidence references.

## Non-regression contract
- Any SLO/resource regression marks `status=fail`.
- `release_blocked=true` on any failed gate.
- History snapshots preserve local quality trend signals.
