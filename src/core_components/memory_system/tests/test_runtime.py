from __future__ import annotations

from core_components.memory_system import build_memory_system, validate_memory_system_dict


def test_build_memory_system_is_deterministic() -> None:
    one = build_memory_system(
        run_id="rid-memory-system",
        retrieval_bundle={"chunks": [{"text": "x"}]},
        quality_metrics={"contradiction_rate": 0.0, "staleness_p95_hours": 1.0},
        quarantine_rows=[],
    )
    two = build_memory_system(
        run_id="rid-memory-system",
        retrieval_bundle={"chunks": [{"text": "x"}]},
        quality_metrics={"contradiction_rate": 0.0, "staleness_p95_hours": 1.0},
        quarantine_rows=[],
    )
    assert one == two
    assert validate_memory_system_dict(one) == []


def test_validate_memory_system_fail_closed() -> None:
    errs = validate_memory_system_dict({"schema": "bad"})
    assert "memory_system_schema" in errs
    assert "memory_system_schema_version" in errs
