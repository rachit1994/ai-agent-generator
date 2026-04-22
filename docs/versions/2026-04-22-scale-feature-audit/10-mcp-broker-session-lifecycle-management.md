# MCP broker/session lifecycle management

## Audit scores
- Agent A score: **3%**
- Agent B score: **0%**
- Confirmed score (conservative): **0%**

## Independent completion re-audit (2026-04-22)
- Independent reviewer score: **34%**
- Updated conservative score for current repo state: **34%**

## Agent A reviewed missing checklist
- [ ] Implement MCP broker service for routing and mediation.
- [ ] Define broker session state machine.
- [ ] Implement session lease/heartbeat handling.
- [ ] Implement reconnect/resume semantics.
- [ ] Implement broker-side authn/authz.
- [ ] Persist broker session metadata.
- [ ] Add broker load and failover tests.
- [ ] Add broker session telemetry.

## Agent B reviewed missing checklist
- [ ] Implement broker abstraction for MCP sessions.
- [ ] Implement create/resume/terminate lifecycle APIs.
- [ ] Persist session state with expiry semantics.
- [ ] Add stale-session reclamation.
- [ ] Add broker routing to plugin runtimes.
- [ ] Add disconnect/reconnect integration tests.
- [ ] Add broker latency/failure metrics.
- [ ] Add broker policy enforcement checks.

## Confirmed missing (both audits)
- [ ] Build MCP broker service.
- [x] Define full MCP session lifecycle API.
- [ ] Persist and reclaim sessions safely.
- [x] Support heartbeat and resume behavior.
- [ ] Enforce authz at broker boundary.
- [x] Route sessions to plugin runtime deterministically.
- [ ] Add failover/disconnect integration tests.
- [ ] Ship broker observability and alerts.

## Remaining blockers to 100%
- [ ] Replace static JSON-driven gate scaffolding with real MCP broker runtime service and live session state machine behavior.
- [ ] Implement durable session persistence/reclamation and broker-boundary authn/authz enforcement in runtime paths.
- [ ] Add true disconnect/reconnect/failover integration coverage against running broker sessions.
- [ ] Wire broker observability into executable metrics/alerts pipeline instead of metadata-only flags.

## Additional implemented in latest pass
- [x] Enforce broker/telemetry identity coherence by requiring aligned non-empty `broker_instance_id` across broker-state and telemetry artifacts.
- [x] Extend runtime/script fixtures and persisted data artifacts with explicit broker instance identity evidence.
- [x] Add fail-closed regression coverage for broker instance ID drift between broker and telemetry payloads.

## Review method
- [x] Independent auditor A review complete.
- [x] Independent auditor B review complete.
- [x] Conservative score set to minimum of both auditors.
- [x] Confirmed-missing list created only from overlap themes.
