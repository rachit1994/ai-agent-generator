from __future__ import annotations

from sde_modes.modes.phased_pipeline import run_phased_pipeline


def run_phased(run_id: str, task_id: str, prompt: str, config) -> tuple[str, list[dict]]:
    return run_phased_pipeline(run_id, task_id, prompt, config)
