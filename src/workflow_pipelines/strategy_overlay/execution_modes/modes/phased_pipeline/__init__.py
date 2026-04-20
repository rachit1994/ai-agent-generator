"""Phased execution: decompose large goals, then guarded_pipeline per atomic todo."""

from __future__ import annotations

from .pipeline import run_phased_pipeline

__all__ = ["run_phased_pipeline"]
