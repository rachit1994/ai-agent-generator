# SDE trajectory and replay (local CLI) — design

**Status:** Implemented per this spec. **Scope:** Local `sde` only; no Docker or remote execution backends.

## Goals

1. **Trajectory** — Every run continues to append one JSON object per line to `outputs/runs/<run-id>/traces.jsonl` (`TraceEvent` shape). Runs are inspectable without a server.
2. **Run manifest** — Single-task runs write `run-manifest.json` so a later process knows the original `task` and `mode`.
3. **Benchmark manifest** — Benchmark runs write `benchmark-manifest.json` with resolved suite path, mode, and the task list actually executed (supports `--max-tasks`).
4. **`sde replay`** — Subcommand with:
   - Default: **narrative** — load `traces.jsonl` (+ optional manifests) and print a human timeline (or JSON with `--format json`).
   - **`--rerun`** — Re-invoke `execute_single_task` using `run-manifest.json` only (fresh `run_id`). Does not apply to benchmark-only directories unless extended later.

## Non-goals

- Replaying shell commands inside containers.
- Replaying benchmark suites automatically from one `run-id` (multi-task ambiguity).

## Artifact layout

| File | When |
|------|------|
| `traces.jsonl` | Always when traces are persisted |
| `run-manifest.json` | `sde run` success path start (written before pipeline) |
| `benchmark-manifest.json` | Start of `sde benchmark` after suite load / slice |

## CLI

```
sde replay --run-id <id> [--format text|json] [--rerun]
```

- `--rerun` requires `run-manifest.json` with `schema` `sde.run_manifest.v1`.

## Benchmark batch ergonomics

- `--max-tasks N` — Run at most the first N tasks of the suite (deterministic order).
- `--continue-on-error` — Per-task failures produce synthetic `finalize` events with `metadata.failure_reason` = `task_run_exception` instead of aborting the whole benchmark.

## References

- SWE-agent trajectories / replay concepts (local ideas checkout): `ideas/SWE-agent/docs/usage/trajectories.md`, CLI replay docs.
- License table: [`docs/sde/upstream-harvest-licenses.md`](../sde/upstream-harvest-licenses.md).
