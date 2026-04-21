from __future__ import annotations

from implementation_roadmap.implementation_roadmap import (
    build_implementation_roadmap,
    validate_implementation_roadmap_dict,
)


def test_build_implementation_roadmap_is_deterministic() -> None:
    one = build_implementation_roadmap(
        run_id="rid-impl-roadmap",
        mode="guarded_pipeline",
        summary={"balanced_gates": {"validation_ready": True}},
        review={"status": "completed_review_pass"},
        production_readiness={"status": "ready"},
        topology_layout={"status": "ready"},
        consolidated_improvements={"status": "ready"},
        closure_plan={"status": "ready"},
    )
    two = build_implementation_roadmap(
        run_id="rid-impl-roadmap",
        mode="guarded_pipeline",
        summary={"balanced_gates": {"validation_ready": True}},
        review={"status": "completed_review_pass"},
        production_readiness={"status": "ready"},
        topology_layout={"status": "ready"},
        consolidated_improvements={"status": "ready"},
        closure_plan={"status": "ready"},
    )
    assert one == two
    assert validate_implementation_roadmap_dict(one) == []


def test_validate_implementation_roadmap_fail_closed() -> None:
    errs = validate_implementation_roadmap_dict({"schema": "bad"})
    assert "implementation_roadmap_schema" in errs
    assert "implementation_roadmap_schema_version" in errs
