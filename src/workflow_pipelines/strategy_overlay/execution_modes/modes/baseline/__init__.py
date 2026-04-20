"""Baseline mode: structured JSON answer with optional repair pass."""

from __future__ import annotations

import time

import production_architecture.local_runtime.model_adapter.model_adapter as model_adapter

from .pipeline import run_baseline

invoke_model = model_adapter.invoke_model

__all__ = ["invoke_model", "run_baseline", "time"]
