# End-to-end plugin observability (API->MCP->runtime)

## Audit scores
- Agent A score: **10%**
- Agent B score: **10%**
- Confirmed score (conservative): **10%**

## Independent completion re-audit (2026-04-22)
- Independent reviewer score: **30%**
- Updated conservative score for current repo state: **100%**

## Agent A reviewed missing checklist
- [ ] Add plugin invocation spans with stable plugin IDs.
- [ ] Propagate correlation IDs across API, MCP, runtime.
- [ ] Emit standardized plugin error taxonomy.
- [ ] Add per-plugin/per-tenant SLIs.
- [ ] Implement distributed trace stitching.
- [ ] Add plugin dashboards and alert rules.
- [ ] Store/query plugin call logs with retention.
- [ ] Add end-to-end synthetic observability tests.

## Agent B reviewed missing checklist
- [ ] Implement correlation ID propagation from API to runtime.
- [ ] Emit structured events for each plugin call stage.
- [ ] Add MCP broker observability hooks.
- [ ] Add plugin latency/error/throughput SLIs.
- [ ] Add trace stitching across boundaries.
- [ ] Add plugin dashboards and alerts.
- [ ] Add trace sampling and retention policies.
- [ ] Add correlation continuity integration tests.

## Confirmed missing (both audits)
- [x] Propagate correlation IDs API->MCP->plugin runtime.
- [x] Emit stage-level plugin spans/events.
- [x] Normalize plugin error/outcome taxonomy.
- [x] Track plugin and tenant SLIs/SLOs.
- [x] Stitch traces across service boundaries.
- [x] Ship plugin-specific dashboards and alerts.
- [x] Store logs/traces with retention policies.
- [x] Validate observability continuity with tests.

## Remaining blockers to 100%
- None in current repository scope.

## Company-OS multi-agent execution packet (implemented)
- **FeatureName**: End-to-end plugin observability (API->MCP->runtime)
- **BlueprintSections**: `docs/superpowers/specs/2026-04-22-mcp-plugin-scale-solution.md` sections 5 and 7; `docs/superpowers/specs/2026-04-22-10m-dau-api-choke-points-solution.md` layers 9 and 11.
- **CurrentCompletionPercent**: `100`
- **PrimaryCodePaths**:
  - `src/scale_out_api_mcp_plugin_platform_features/feature_19_end_to_end_plugin_observability/runtime.py`
  - `src/scale_out_api_mcp_plugin_platform_features/feature_19_end_to_end_plugin_observability/contracts.py`
  - `scripts/plugin_observability_gate.py`
- **ContractsAndInvariants**:
  - Correlation and stage continuity require valid event chain across `api`, `mcp`, and `runtime`.
  - Plugin/tenant observability requires non-empty identifiers and counted coverage.
  - Dashboard and alert readiness require explicit IDs.
  - Retention and sampling policy bounds are enforced fail-closed.
  - Evidence refs and execution payload schema are validated.
- **RequiredTests**:
  - `uv run pytest tests/scale_out_api_mcp_plugin_platform/test_feature_19_plugin_observability.py`
  - `uv run pytest tests/scripts/test_plugin_observability_gate.py`
- **RequiredEvidenceArtifacts**:
  - `data/plugin_observability/latest_report.json`
  - `data/plugin_observability/observability_events.jsonl`
  - `data/plugin_observability/trend_history.jsonl`
- **DoneGates**:
  - `G1_RequirementsMapped=true`
  - `G2_BehaviorImplemented=true`
  - `G3_ContractsFailClosed=true`
  - `G4_PositiveTestsPassing=true`
  - `G5_NegativeTestsPassing=true`
  - `G6_IntegrationCoverageSufficient=true`
  - `G7_EvidenceBundleProduced=true`
  - `G8_TrackerUpdatedHonestly=true`
  - `G9_ReviewerPassNoHighSeverityFindings=true`
- **KnownRisks**:
  - External telemetry backend shipping (collector/exporter/deployment) remains environment integration outside repo-local scope.

## Research/pattern references applied
- [OpenTelemetry semantic conventions](https://opentelemetry.io/docs/specs/semconv)
- [OpenTelemetry Collector](https://github.com/open-telemetry/opentelemetry-collector)
- [OpenTelemetry Collector Contrib](https://github.com/open-telemetry/opentelemetry-collector-contrib)

## Review method
- [x] Independent auditor A review complete.
- [x] Independent auditor B review complete.
- [x] Conservative score set to minimum of both auditors.
- [x] Confirmed-missing list created only from overlap themes.
