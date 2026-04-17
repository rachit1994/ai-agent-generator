# SDE demo (tracked template)

This tree is the **version-controlled seed** for the demo. Runtime demos live under **`demo_apps/`**, which is **gitignored** — copy this folder there to run benchmarks locally:

```bash
mkdir -p demo_apps
cp -R docs/templates/sde-demo demo_apps/sde-demo
```

## Run (from repository root)

```bash
uv run sde benchmark --suite demo_apps/sde-demo/tasks.jsonl --mode both
```

Single guarded run: paste the `prompt` from `tasks.jsonl` into:

```bash
uv run sde run --mode guarded_pipeline --task "<paste prompt here>"
```
