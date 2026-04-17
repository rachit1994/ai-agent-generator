from __future__ import annotations

from sde.modes.guarded_pipeline import run_guarded_pipeline


def run_guarded(run_id: str, task_id: str, prompt: str, config) -> tuple[str, list[dict]]:
    return run_guarded_pipeline(run_id, task_id, prompt, config)
