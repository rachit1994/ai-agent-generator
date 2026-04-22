# Local and server semantic parity enforcement

## Audit scores
- Agent A score: **8%**
- Agent B score: **12%**
- Confirmed score (conservative): **8%**

## Independent completion re-audit (2026-04-22)
- Independent reviewer score: **68%**
- Updated conservative score for current repo state: **68%**

## Agent A reviewed missing checklist
- [ ] Define canonical local-vs-server parity matrix per API/tool operation.
- [ ] Implement shared conformance harness against both runtimes.
- [ ] Add idempotency parity assertions across adapters.
- [ ] Add authz-decision parity assertions.
- [ ] Add state-transition parity assertions.
- [ ] Add retriable/non-retriable error taxonomy parity assertions.
- [ ] Persist parity results as versioned artifacts.
- [ ] Gate CI and deployment on parity drift.

## Agent B reviewed missing checklist
- [ ] Implement server runtime path that uses local contract validators.
- [ ] Create golden local-vs-server semantic parity test suite.
- [ ] Add idempotency replay parity tests.
- [ ] Add authz decision replay parity tests.
- [ ] Enforce state transition parity matrices in CI.
- [ ] Add parity diff tooling for API responses and error codes.
- [ ] Block deploy on semantic parity drift.
- [ ] Publish shared semantic contract package for both runtimes.

## Confirmed missing (both audits)
- [x] Build executable local-vs-server parity harness.
- [x] Validate authz/idempotency/state transitions for both environments.
- [x] Detect and report semantic response drift automatically.
- [x] Gate release on parity failures.
- [x] Persist parity audit artifacts per run.
- [ ] Share one contract package across runtime adapters.
- [x] Run parity checks continuously in CI.
- [ ] Add remediation playbook for parity failures.

## Remaining blockers to 100%
- [ ] Replace metadata-only `contract_package` field with verifiable shared semantic contract package integration imported by both local and server adapters.
- [ ] Add a parity failure remediation playbook and wire it into gate output/runbook references.
- [ ] Expand negative tests to include dedicated idempotency/state-transition/error-taxonomy drift replay cases and finer-grained drift diffs.
- [ ] Add deploy-stage parity enforcement in addition to CI-level gate execution.

## Review method
- [x] Independent auditor A review complete.
- [x] Independent auditor B review complete.
- [x] Conservative score set to minimum of both auditors.
- [x] Confirmed-missing list created only from overlap themes.
