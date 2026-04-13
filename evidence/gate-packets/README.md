# Gate packets (versioned evidence)

Each subdirectory `evidence/gate-packets/<packet_id>/` is one immutable evidence bundle.

## `MANIFEST.json` (required fields)

| Field | Type | Rule |
|-------|------|------|
| `packet_id` | string | Matches directory name. |
| `git_commit` | string | Full SHA of the code revision this packet proves. |
| `covers_workflow_ids` | array | Every `workflow_id` from `docs/implementation/production-workflow-manifest.md` claimed by this packet. |
| `backends` | array | Subset of `["ollama","vllm"]`; production exit requires both. |
| `promptfoo_revision` | string | Config hash or tagged revision. |
| `agentevals_config_hash` | string | Scorer config hash; omit only if substitute path used. |
| `deepeval_run_id` | string | CI or local run identifier. |
| `otel_exporter_version` | string | Exporter library version. |
| `normalization_regex_table_version` | string | Must match `schema_version` in `docs/implementation/schemas/normalization-regex-table.json` used when computing failure signatures. |
| `otel_span_registry_version` | string | Must match `schema_version` in `docs/implementation/schemas/otel-span-stage-registry.json`. |

## Index

Add a row per packet under **Index** in chronological order.

| packet_id | git_commit | purpose |
|-----------|------------|---------|
| _(none yet)_ | — | — |
