# Contract-version negotiation for MCP/plugins

## Audit scores
- Agent A score: **2%**
- Agent B score: **0%**
- Confirmed score (conservative): **0%**

## Independent completion re-audit (2026-04-22)
- Independent reviewer score: **65%**
- Updated conservative score for current repo state: **65%**

## Agent A reviewed missing checklist
- [ ] Define MCP/plugin version negotiation handshake.
- [ ] Implement supported-version advertisement.
- [ ] Implement compatibility fallback strategy.
- [ ] Implement hard rejection for unsafe incompatible versions.
- [ ] Implement deprecation windows.
- [ ] Add negotiation outcome telemetry.
- [ ] Add dual-version serving for rollback safety.
- [ ] Add mixed-version integration tests.

## Agent B reviewed missing checklist
- [ ] Define protocol negotiation handshake.
- [ ] Advertise supported version ranges.
- [ ] Implement client-side downgrade selection.
- [ ] Hard-fail on incompatible intersections.
- [ ] Add compatibility matrix tests.
- [ ] Add rollback-safe staged negotiation behavior.
- [ ] Emit negotiated version/failure telemetry.
- [ ] Enforce runtime deprecation windows.

## Confirmed missing (both audits)
- [x] Implement MCP/plugin contract version negotiation.
- [x] Advertise and select compatible version ranges.
- [x] Reject unsafe incompatible versions deterministically.
- [x] Support rollback-safe dual-version behavior.
- [x] Enforce and test deprecation windows.
- [x] Track negotiated versions in telemetry.
- [x] Exercise mixed-version fleet scenarios.
- [x] Gate rollout on compatibility failures.

## Remaining blockers to 100%
- [ ] Integrate version negotiation into live MCP/plugin runtime call paths (not gate-only artifact evaluation).
- [ ] Replace boolean marker inputs with computed range intersection and downgrade selection over actual plugin contracts/manifests.
- [ ] Generate compatibility matrix outcomes from real runtime/plugin metadata instead of static fixtures.

## Review method
- [x] Independent auditor A review complete.
- [x] Independent auditor B review complete.
- [x] Conservative score set to minimum of both auditors.
- [x] Confirmed-missing list created only from overlap themes.
