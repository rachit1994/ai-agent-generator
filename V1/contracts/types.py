"""Types for phase orchestration contracts."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class PhaseStatus(str, Enum):
    PASS = "PASS"
    RETRY = "RETRY"
    BLOCKED = "BLOCKED"


@dataclass(frozen=True)
class PhaseContract:
    phase_id: str
    phase_title: str
    required_roles: tuple[str, ...]
    required_markers: tuple[str, ...]


@dataclass(frozen=True)
class RoleResult:
    role_name: str
    stdout: str
    stderr: str
    exit_code: int


@dataclass(frozen=True)
class PhaseResult:
    phase_id: str
    status: PhaseStatus
    reason: str
    role_results: tuple[RoleResult, ...]

