"""Guarded pipeline: planner → executor → verifier (+ optional fix pass)."""

from __future__ import annotations

import time

import production_architecture.local_runtime.model_adapter.model_adapter as model_adapter

from .pipeline import run_guarded_pipeline

__all__ = ["model_adapter", "run_guarded_pipeline", "time"]
