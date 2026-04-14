"""Hardcoded phase contracts for software-engineer persona."""

from __future__ import annotations

from V1.contracts.types import PhaseContract

ROLE_SEQUENCE: tuple[str, ...] = ("architect", "implementer", "validator", "reviewer")
DEFAULT_MARKERS: tuple[str, ...] = ("EVIDENCE:", "VERDICT:")

PHASE_TITLES: tuple[tuple[str, str], ...] = (
    ("phase_00", "Problem validation"),
    ("phase_00_5", "Technical spike"),
    ("phase_01", "Requirements and planning"),
    ("phase_02", "Design and consensus"),
    ("phase_03", "Risk and compliance"),
    ("phase_04", "Execution planning"),
    ("phase_05", "Implementation"),
    ("phase_06", "Code review reality"),
    ("phase_07", "Advanced testing"),
    ("phase_08", "Database safety"),
    ("phase_09", "UX and global readiness"),
    ("phase_10", "CI/CD"),
    ("phase_11", "Launch gate"),
    ("phase_12", "Launch safety"),
    ("phase_13", "Experimentation"),
    ("phase_14", "Production rollout"),
    ("phase_15", "Operational reality"),
    ("phase_16", "Post launch"),
    ("phase_17", "Post-mortem"),
    ("phase_18", "Iteration loop"),
    ("phase_19", "Long-term maintenance"),
)

PHASE_CONTRACTS: tuple[PhaseContract, ...] = tuple(
    PhaseContract(
        phase_id=phase_id,
        phase_title=phase_title,
        required_roles=ROLE_SEQUENCE,
        required_markers=DEFAULT_MARKERS,
    )
    for phase_id, phase_title in PHASE_TITLES
)

PHASE_CONTRACT_BY_ID: dict[str, PhaseContract] = {
    contract.phase_id: contract for contract in PHASE_CONTRACTS
}

