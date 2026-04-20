"""Regression: public ``__all__`` surfaces and ``libs/`` callables match pre-layout migration (no dropped exports).

Baseline for ``sde_*`` ``__all__`` parity: git ``3ec108e`` (``src/sde_gates``, ``src/sde_pipeline``, ``src/sde_modes``, ``orchestrator.api``).
Baseline for ``sde_foundations`` split: same commit, top-level ``def`` / ``class`` in ``src/sde_foundations/{utils,storage,eval,types,artifacts,model_adapter,safeguards}.py`` plus leaf ``sde_gates`` modules moved to ``libs/``.
Baseline for ``sde_pipeline`` surface: same commit, selected non-underscore symbols from ``config``, ``replay``, ``report``, ``run_logging``, ``runner/*`` (single-task driver + artifact/layer writers + ``persist_traces`` + ``traces_jsonl_event_contract``), ``benchmark/{benchmark_aggregate_summary_contract,benchmark_checkpoint_contract,benchmark_manifest_contract,failure_pipeline_contract,run_benchmark,run_manifest_contract,suite,summary_payload,task_loop}`` (used across orchestrator + pipeline).
Baseline for ``sde_gates`` submodules: same commit, public ``def`` entrypoints on ``review``, ``run_directory``, ``token_context``, ``risk_budgets/*`` (static analysis, balanced gates, metrics, run profile, hard-stop families) re-homed under ``guardrails_and_safety/``.
Baseline for ``sde_modes`` wiring: public ``def`` entrypoints on ``modes/{baseline,guarded,phased}``, ``guarded_pipeline/{pipeline,verify_core}``, ``phased_pipeline/{pipeline,decompose}`` under ``workflow_pipelines.execution_modes``.
Baseline for ``orchestrator.api`` submodules: symbols imported directly (mostly tests + ``gemma_roadmap_review``) from ``orchestrator.api.<module>`` remain on disk after the long-path package move, including names tests monkeypatch on those modules (re-exports such as ``project_driver.execute_single_task``, ``context_pack.build_repo_index``, ``gemma_roadmap_review.invoke_model``), plus root-shimmed surfaces (``project_intake_*``, ``project_remaining_work`` / ``status``, full ``project_plan_lock`` writers).
"""

from __future__ import annotations

import importlib
from typing import Final

import pytest

_GUARDRAILS_AND_SAFETY_EXPORTS: Final = frozenset(
    {
        "REQUIRED_REVIEW_KEYS",
        "REVIEW_SCHEMA",
        "TOKEN_CONTEXT_SCHEMA",
        "all_required_execution_paths",
        "build_review",
        "build_token_context",
        "compute_balanced_gates",
        "evaluate_hard_stops",
        "manifest_paths_for_review",
        "metrics_from_events",
        "reliability_gate",
        "run_static_code_gates",
        "validate_execution_run_directory",
        "validation_ready",
    }
)

_ORCHESTRATOR_API_EXPORTS: Final = frozenset(
    {
        "append_roadmap_learning_line",
        "apply_intake_doc_review_result",
        "build_project_stage1_observability_export",
        "describe_project_session",
        "evaluate_project_plan_lock_readiness",
        "evaluate_remaining_work",
        "execute_single_task",
        "generate_report",
        "intake_merge_anchor_present",
        "lineage_manifest_session_event_snapshot",
        "load_remaining_work_rules",
        "replay_run",
        "render_remaining_work_markdown",
        "roadmap_review",
        "run_benchmark",
        "run_bounded_evolve_loop",
        "run_continuous_project_session",
        "run_continuous_until",
        "run_project_session",
        "scaffold_project_intake",
        "stage1_observability_export_schema_errors",
        "validate_project_session",
        "validate_run",
        "write_intake_lineage_manifest",
        "write_project_plan_lock",
        "write_project_stage1_observability_export",
    }
)

_RUNNER_EXPORTS: Final = frozenset({"execute_single_task", "run_baseline", "run_guarded", "run_phased"})

_BASELINE_MODE_EXPORTS: Final = frozenset({"invoke_model", "run_baseline", "time"})

_GUARDED_PIPELINE_EXPORTS: Final = frozenset({"model_adapter", "run_guarded_pipeline", "time"})

_PHASED_PIPELINE_EXPORTS: Final = frozenset({"run_phased_pipeline"})

_BENCHMARK_EXPORTS: Final = frozenset({"run_benchmark"})

_LIBS_MIGRATED_PUBLIC_NAMES: Final = (
    ("common.utils", ("outputs_base", "create_run_id", "now_iso", "ms_to_iso")),
    (
        "storage.storage",
        ("ensure_dir", "write_json", "append_jsonl", "read_json", "read_jsonl"),
    ),
    (
        "sde_eval.eval",
        (
            "percentile",
            "aggregate_metrics",
            "root_cause_distribution",
            "stage_latency_breakdown",
            "verdict_for",
            "strict_gate_decision",
        ),
    ),
    ("sde_types.types", ("Score", "TraceEvent")),
    ("artifacts.artifacts", ("extract_python_code",)),
    ("model_adapter.model_adapter", ("invoke_model",)),
    (
        "safeguards.safeguards",
        (
            "validate_task_text",
            "validate_task_payload",
            "refusal_for_unsafe",
            "_extract_json",
            "validate_structured_output",
            "classify_output_failure",
        ),
    ),
    (
        "gates_manifest.manifest",
        ("manifest_paths_for_review", "all_required_execution_paths", "manifest_entries"),
    ),
    ("time_and_budget.time_util", ("iso_now",)),
)

_GATES_CONSTANTS_NAMES: Final = frozenset(
    {"REQUIRED_REVIEW_KEYS", "REVIEW_SCHEMA", "TOKEN_CONTEXT_SCHEMA"}
)

_PIPELINE_MIGRATED_PUBLIC_NAMES: Final = (
    (
        "workflow_pipelines.production_pipeline_task_to_promote.config",
        ("DEFAULT_CONFIG", "GuardrailBudgets", "RunConfig", "config_snapshot"),
    ),
    (
        "workflow_pipelines.production_pipeline_task_to_promote.replay",
        (
            "run_dir_for_id",
            "load_traces",
            "format_timeline_text",
            "format_timeline_html",
            "write_trajectory_html",
            "replay_narrative",
            "replay_rerun",
            "replay_run",
        ),
    ),
    (
        "workflow_pipelines.production_pipeline_task_to_promote.report",
        ("generate_report",),
    ),
    (
        "workflow_pipelines.production_pipeline_task_to_promote.runner.single_task",
        ("execute_single_task",),
    ),
    (
        "workflow_pipelines.production_pipeline_task_to_promote.runner.completion_layer",
        ("write_completion_artifacts",),
    ),
    (
        "workflow_pipelines.production_pipeline_task_to_promote.runner.cto_publish",
        ("write_cto_gate_layer",),
    ),
    (
        "workflow_pipelines.production_pipeline_task_to_promote.runner.event_lineage_layer",
        ("write_event_lineage_artifacts",),
    ),
    (
        "workflow_pipelines.production_pipeline_task_to_promote.runner.evolution_layer",
        ("write_evolution_artifacts",),
    ),
    (
        "workflow_pipelines.production_pipeline_task_to_promote.runner.memory_artifact_layer",
        ("write_memory_artifacts",),
    ),
    (
        "workflow_pipelines.production_pipeline_task_to_promote.runner.orchestration_run_end_contract",
        (
            "ORCHESTRATION_RUN_END_CONTRACT",
            "validate_orchestration_run_end_dict",
        ),
    ),
    (
        "workflow_pipelines.production_pipeline_task_to_promote.runner.orchestration_run_error_contract",
        (
            "ORCHESTRATION_RUN_ERROR_CONTRACT",
            "validate_orchestration_run_error_dict",
        ),
    ),
    (
        "workflow_pipelines.production_pipeline_task_to_promote.runner.orchestration_run_start_contract",
        (
            "ORCHESTRATION_RUN_START_CONTRACT",
            "validate_orchestration_run_start_dict",
        ),
    ),
    (
        "workflow_pipelines.production_pipeline_task_to_promote.runner.orchestration_stage_event_contract",
        (
            "ORCHESTRATION_STAGE_EVENT_CONTRACT",
            "validate_orchestration_stage_event_line_dict",
        ),
    ),
    (
        "workflow_pipelines.production_pipeline_task_to_promote.runner.traces_jsonl_event_contract",
        (
            "TRACES_JSONL_EVENT_CONTRACT",
            "validate_traces_jsonl_event_dict",
        ),
    ),
    (
        "workflow_pipelines.production_pipeline_task_to_promote.runner.organization_layer",
        ("write_organization_artifacts",),
    ),
    (
        "workflow_pipelines.production_pipeline_task_to_promote.runner.failure_summary",
        ("write_failure_summary",),
    ),
    (
        "workflow_pipelines.production_pipeline_task_to_promote.runner.persist_traces",
        (
            "append_orchestration_run_start",
            "append_orchestration_stage_events",
            "persist_traces",
        ),
    ),
    (
        "workflow_pipelines.production_pipeline_task_to_promote.runner.success_artifacts",
        ("write_success_artifact_layer",),
    ),
    (
        "workflow_pipelines.production_pipeline_task_to_promote.runner.artifacts",
        ("harvest_pipeline_artifacts",),
    ),
    (
        "workflow_pipelines.production_pipeline_task_to_promote.benchmark.run_benchmark",
        ("run_benchmark",),
    ),
    (
        "workflow_pipelines.production_pipeline_task_to_promote.benchmark.benchmark_aggregate_summary_contract",
        (
            "BENCHMARK_AGGREGATE_SUMMARY_CONTRACT",
            "validate_benchmark_aggregate_summary_dict",
            "validate_benchmark_aggregate_summary_path",
        ),
    ),
    (
        "workflow_pipelines.production_pipeline_task_to_promote.benchmark.benchmark_checkpoint_contract",
        (
            "BENCHMARK_CHECKPOINT_CONTRACT",
            "validate_benchmark_checkpoint_dict",
            "validate_benchmark_checkpoint_path",
        ),
    ),
    (
        "workflow_pipelines.production_pipeline_task_to_promote.benchmark.benchmark_manifest_contract",
        (
            "BENCHMARK_MANIFEST_CONTRACT",
            "validate_benchmark_manifest_dict",
            "validate_benchmark_manifest_path",
        ),
    ),
    (
        "workflow_pipelines.production_pipeline_task_to_promote.benchmark.failure_pipeline_contract",
        (
            "FAILURE_PIPELINE_SUMMARY_CONTRACT",
            "REPLAY_MANIFEST_CONTRACT",
            "validate_failure_summary_dict",
            "validate_failure_summary_path",
            "validate_replay_manifest_dict",
            "validate_replay_manifest_path",
        ),
    ),
    (
        "workflow_pipelines.production_pipeline_task_to_promote.benchmark.offline_eval_contract",
        ("OFFLINE_EVAL_SUITE_CONTRACT", "validate_suite_document", "validate_suite_jsonl"),
    ),
    (
        "workflow_pipelines.production_pipeline_task_to_promote.benchmark.online_eval_shadow_contract",
        (
            "ONLINE_EVAL_SHADOW_CONTRACT",
            "validate_canary_report_dict",
            "validate_canary_report_path",
        ),
    ),
    (
        "workflow_pipelines.production_pipeline_task_to_promote.benchmark.orchestration_benchmark_jsonl_contract",
        (
            "ORCHESTRATION_BENCHMARK_ERROR_CONTRACT",
            "ORCHESTRATION_BENCHMARK_RESUME_CONTRACT",
            "validate_orchestration_benchmark_error_dict",
            "validate_orchestration_benchmark_resume_dict",
        ),
    ),
    (
        "workflow_pipelines.production_pipeline_task_to_promote.benchmark.production_pipeline_plan_contract",
        (
            "PRODUCTION_PIPELINE_PLAN_CONTRACT",
            "validate_harness_project_plan_dict",
            "validate_harness_project_plan_path",
        ),
    ),
    (
        "workflow_pipelines.production_pipeline_task_to_promote.benchmark.promotion_eval_contract",
        (
            "PROMOTION_EVAL_PACKAGE_CONTRACT",
            "validate_promotion_package_dict",
            "validate_promotion_package_path",
        ),
    ),
    (
        "workflow_pipelines.production_pipeline_task_to_promote.benchmark.regression_surface_contract",
        ("REGRESSION_DIMENSION_ANCHORS", "REGRESSION_SURFACE_CONTRACT", "validate_regression_anchors"),
    ),
    (
        "workflow_pipelines.production_pipeline_task_to_promote.benchmark.retry_pipeline_contract",
        ("RETRY_PIPELINE_REPEAT_CONTRACT", "validate_repeat_profile_result"),
    ),
    (
        "workflow_pipelines.production_pipeline_task_to_promote.benchmark.run_manifest_contract",
        (
            "RUN_MANIFEST_CONTRACT",
            "validate_run_manifest_dict",
            "validate_run_manifest_path",
        ),
    ),
    (
        "workflow_pipelines.production_pipeline_task_to_promote.benchmark.strategy_overlay_contract",
        (
            "STRATEGY_OVERLAY_CONTRACT",
            "validate_strategy_proposal_dict",
            "validate_strategy_proposal_path",
        ),
    ),
    (
        "workflow_pipelines.production_pipeline_task_to_promote.benchmark.suite",
        ("read_suite",),
    ),
    (
        "workflow_pipelines.production_pipeline_task_to_promote.run_logging",
        (
            "setup_run_logger",
            "shutdown_run_logger",
            "log_run_banner",
            "log_benchmark_banner",
            "log_benchmark_traces_written",
            "log_benchmark_verdict",
            "log_task_scope",
            "log_trace_narrative",
            "log_traces_persisted",
            "log_orchestration_persisted",
            "log_structured_output_summary",
            "log_success_artifact_layer",
            "log_cto_gate_layer",
            "log_run_error",
            "log_run_failure_context",
            "log_run_end",
        ),
    ),
    (
        "workflow_pipelines.production_pipeline_task_to_promote.benchmark.summary_payload",
        ("build_summary",),
    ),
    (
        "workflow_pipelines.production_pipeline_task_to_promote.benchmark.task_loop",
        ("synthetic_finalize_failure_event", "run_suite_tasks"),
    ),
)

_GUARDRAILS_SUBMODULE_PUBLIC_NAMES: Final = (
    ("guardrails_and_safety.review_gating.review", ("build_review",)),
    (
        "guardrails_and_safety.review_gating.run_directory",
        ("validate_execution_run_directory",),
    ),
    (
        "guardrails_and_safety.review_gating.policy_bundle_rollback",
        ("POLICY_ROLLBACK_SCHEMA", "validate_policy_bundle_rollback"),
    ),
    (
        "guardrails_and_safety.autonomy_boundaries_tokens_expiry.token_context",
        ("build_token_context",),
    ),
    (
        "guardrails_and_safety.risk_budgets.static_analysis",
        ("run_static_code_gates", "blocking_ids"),
    ),
    (
        "guardrails_and_safety.risk_budgets.balanced_gates",
        ("compute_balanced_gates", "validation_ready"),
    ),
    (
        "guardrails_and_safety.risk_budgets.metrics_helpers",
        ("metrics_from_events", "reliability_gate"),
    ),
    ("guardrails_and_safety.risk_budgets.run_profile", ("is_coding_only",)),
    ("guardrails_and_safety.risk_budgets.hard_stop_schedule", ("expected_hard_stop_ids",)),
    ("guardrails_and_safety.risk_budgets.hard_stops", ("evaluate_hard_stops",)),
    (
        "guardrails_and_safety.risk_budgets.hard_stops_guarded",
        ("evaluate_guarded_hard_stops",),
    ),
    (
        "guardrails_and_safety.risk_budgets.hard_stops_events",
        ("evaluate_event_lineage_hard_stops",),
    ),
    (
        "guardrails_and_safety.risk_budgets.hard_stops_memory",
        ("evaluate_memory_hard_stops",),
    ),
    (
        "guardrails_and_safety.risk_budgets.hard_stops_evolution",
        ("evaluate_evolution_hard_stops",),
    ),
    (
        "guardrails_and_safety.risk_budgets.hard_stops_organization",
        ("evaluate_organization_hard_stops",),
    ),
)

_EXECUTION_MODES_SUBMODULE_PUBLIC_NAMES: Final = (
    ("workflow_pipelines.execution_modes.modes.guarded", ("run_guarded",)),
    ("workflow_pipelines.execution_modes.modes.phased", ("run_phased",)),
    (
        "workflow_pipelines.execution_modes.modes.baseline.pipeline",
        ("run_baseline",),
    ),
    (
        "workflow_pipelines.execution_modes.modes.guarded_pipeline.pipeline",
        ("run_guarded_pipeline",),
    ),
    (
        "workflow_pipelines.execution_modes.modes.guarded_pipeline.verify_core",
        ("heuristic_verify", "extract_json_object", "finalize_failure_reason"),
    ),
    (
        "workflow_pipelines.execution_modes.modes.phased_pipeline.pipeline",
        ("run_phased_pipeline",),
    ),
    (
        "workflow_pipelines.execution_modes.modes.phased_pipeline.decompose",
        ("flatten_plan", "fallback_single_todo_plan"),
    ),
)

_ORCHESTRATOR_API_SUBMODULE_PUBLIC_NAMES: Final = (
    (
        "orchestrator.api.project_driver",
        (
            "add_detached_worktree",
            "execute_single_task",
            "evaluate_project_plan_lock_readiness",
            "git_worktree_available",
            "lineage_manifest_session_event_snapshot",
            "remove_worktree",
            "run_project_session",
            "run_step_verification",
        ),
    ),
    (
        "orchestrator.api.project_schema",
        ("validate_project_plan", "validate_progress"),
    ),
    (
        "orchestrator.api.project_workspace",
        (
            "evaluate_workspace_repo_gates",
            "git_head_matches_branch",
            "path_scope_pattern_allowed",
        ),
    ),
    (
        "orchestrator.api.project_plan_lock",
        (
            "evaluate_project_plan_lock_readiness",
            "lineage_manifest_session_event_snapshot",
            "write_intake_lineage_manifest",
            "write_project_plan_lock",
        ),
    ),
    (
        "orchestrator.api.project_events",
        ("SESSION_EVENTS_FILENAME", "append_session_event"),
    ),
    (
        "orchestrator.api.project_stage1_observability_export",
        (
            "STAGE1_OBSERVABILITY_EXPORT_KIND",
            "STAGE1_OBSERVABILITY_EXPORT_SCHEMA_VERSION",
            "build_project_stage1_observability_export",
            "stage1_observability_export_schema_errors",
            "write_project_stage1_observability_export",
        ),
    ),
    (
        "orchestrator.api.project_remaining_work",
        (
            "evaluate_remaining_work",
            "load_remaining_work_rules",
            "render_remaining_work_markdown",
        ),
    ),
    (
        "orchestrator.api.project_aggregate",
        ("write_project_definition_of_done", "write_verification_aggregate"),
    ),
    (
        "orchestrator.api.project_lease",
        (
            "DEFAULT_LEASE_TTL_SEC",
            "prune_stale_leases",
            "resolve_lease_ttl_sec",
            "try_acquire",
        ),
    ),
    (
        "orchestrator.api.project_plan",
        ("detect_dependency_cycle", "plan_step_ids", "runnable_step_ids"),
    ),
    ("orchestrator.api.project_scheduler", ("select_steps_for_tick",)),
    (
        "orchestrator.api.continuous_run",
        (
            "execute_single_task",
            "run_continuous_project_session",
            "run_continuous_until",
            "run_project_session",
            "validate_execution_run_directory",
        ),
    ),
    (
        "orchestrator.api.project_intake_util",
        ("intake_doc_review_errors", "intake_merge_anchor_present"),
    ),
    ("orchestrator.api.project_intake_scaffold", ("scaffold_project_intake",)),
    ("orchestrator.api.project_intake_revise", ("apply_intake_doc_review_result",)),
    (
        "orchestrator.api.gemma_roadmap_review",
        ("append_roadmap_learning_line", "invoke_model", "roadmap_review"),
    ),
    ("orchestrator.api.self_evolve", ("run_bounded_evolve_loop",)),
    ("orchestrator.api.project_status", ("describe_project_session",)),
    (
        "orchestrator.api.status",
        (
            "describe_project_session",
            "evaluate_remaining_work",
            "load_remaining_work_rules",
            "render_remaining_work_markdown",
        ),
    ),
    (
        "orchestrator.api.project_validate",
        (
            "EXIT_VALIDATE_INVALID",
            "EXIT_VALIDATE_OK",
            "EXIT_VALIDATE_WORKSPACE",
            "evaluate_workspace_repo_gates",
            "validate_project_session",
        ),
    ),
    ("orchestrator.api.validate_run", ("validate_run",)),
    (
        "orchestrator.api.project_stop",
        (
            "EXIT_SESSION_BLOCKED_OR_BUDGET",
            "EXIT_SESSION_INVALID",
            "EXIT_SESSION_OK",
            "exit_code_ci_meaning",
            "write_stop_report",
        ),
    ),
    (
        "orchestrator.api.context_pack",
        (
            "build_context_pack",
            "build_repo_index",
            "latest_output_dirs_by_step",
        ),
    ),
)

_EXPORT_MODULES: Final = (
    ("guardrails_and_safety", _GUARDRAILS_AND_SAFETY_EXPORTS),
    ("orchestrator.api", _ORCHESTRATOR_API_EXPORTS),
    (
        "workflow_pipelines.production_pipeline_task_to_promote.runner",
        _RUNNER_EXPORTS,
    ),
    (
        "workflow_pipelines.execution_modes.modes.baseline",
        _BASELINE_MODE_EXPORTS,
    ),
    (
        "workflow_pipelines.execution_modes.modes.guarded_pipeline",
        _GUARDED_PIPELINE_EXPORTS,
    ),
    (
        "workflow_pipelines.execution_modes.modes.phased_pipeline",
        _PHASED_PIPELINE_EXPORTS,
    ),
    (
        "workflow_pipelines.production_pipeline_task_to_promote.benchmark",
        _BENCHMARK_EXPORTS,
    ),
)


@pytest.mark.parametrize("module_name,expected", _EXPORT_MODULES)
def test_module_all_matches_migration_surface(module_name: str, expected: frozenset[str]) -> None:
    mod = importlib.import_module(module_name)
    assert hasattr(mod, "__all__"), f"{module_name} must define __all__"
    assert frozenset(mod.__all__) == expected, (
        f"{module_name}.__all__ drift: missing {expected - frozenset(mod.__all__)} "
        f"extra {frozenset(mod.__all__) - expected}"
    )


@pytest.mark.parametrize("module_name,expected", _EXPORT_MODULES)
def test_module_all_members_are_defined(module_name: str, expected: frozenset[str]) -> None:
    mod = importlib.import_module(module_name)
    for name in expected:
        assert hasattr(mod, name), f"{module_name}.{name} missing on module"


@pytest.mark.parametrize("module_name,expected", _EXPORT_MODULES)
def test_module_all_members_are_gettable(module_name: str, expected: frozenset[str]) -> None:
    mod = importlib.import_module(module_name)
    for name in expected:
        getattr(mod, name)


def test_orchestrator_subpackages_listed_and_importable() -> None:
    import orchestrator

    assert frozenset(orchestrator.__all__) == frozenset({"api", "runtime"})
    importlib.import_module("orchestrator.api")
    importlib.import_module("orchestrator.runtime")


@pytest.mark.parametrize("module_name,names", _LIBS_MIGRATED_PUBLIC_NAMES)
def test_libs_modules_expose_migrated_public_names(module_name: str, names: tuple[str, ...]) -> None:
    mod = importlib.import_module(module_name)
    for name in names:
        assert hasattr(mod, name), f"{module_name}.{name} missing after sde_foundations / gates split"


@pytest.mark.parametrize("module_name,names", _LIBS_MIGRATED_PUBLIC_NAMES)
def test_libs_migrated_names_are_gettable(module_name: str, names: tuple[str, ...]) -> None:
    mod = importlib.import_module(module_name)
    for name in names:
        getattr(mod, name)


def test_gates_constants_module_has_schema_contract_names() -> None:
    mod = importlib.import_module("gates_constants.constants")
    for name in _GATES_CONSTANTS_NAMES:
        assert hasattr(mod, name), f"gates_constants.constants.{name} missing"
        getattr(mod, name)


@pytest.mark.parametrize("module_name,names", _PIPELINE_MIGRATED_PUBLIC_NAMES)
def test_pipeline_modules_expose_migrated_public_names(module_name: str, names: tuple[str, ...]) -> None:
    mod = importlib.import_module(module_name)
    for name in names:
        assert hasattr(mod, name), f"{module_name}.{name} missing after sde_pipeline move"


@pytest.mark.parametrize("module_name,names", _PIPELINE_MIGRATED_PUBLIC_NAMES)
def test_pipeline_migrated_names_are_gettable(module_name: str, names: tuple[str, ...]) -> None:
    mod = importlib.import_module(module_name)
    for name in names:
        getattr(mod, name)


@pytest.mark.parametrize("module_name,names", _GUARDRAILS_SUBMODULE_PUBLIC_NAMES)
def test_guardrails_submodules_expose_migrated_public_names(
    module_name: str, names: tuple[str, ...],
) -> None:
    mod = importlib.import_module(module_name)
    for name in names:
        assert hasattr(mod, name), f"{module_name}.{name} missing after sde_gates move"


@pytest.mark.parametrize("module_name,names", _GUARDRAILS_SUBMODULE_PUBLIC_NAMES)
def test_guardrails_submodule_names_are_gettable(module_name: str, names: tuple[str, ...]) -> None:
    mod = importlib.import_module(module_name)
    for name in names:
        getattr(mod, name)


@pytest.mark.parametrize("module_name,names", _EXECUTION_MODES_SUBMODULE_PUBLIC_NAMES)
def test_execution_modes_submodules_expose_migrated_public_names(
    module_name: str, names: tuple[str, ...],
) -> None:
    mod = importlib.import_module(module_name)
    for name in names:
        assert hasattr(mod, name), f"{module_name}.{name} missing after sde_modes move"


@pytest.mark.parametrize("module_name,names", _EXECUTION_MODES_SUBMODULE_PUBLIC_NAMES)
def test_execution_modes_submodule_names_are_gettable(
    module_name: str, names: tuple[str, ...],
) -> None:
    mod = importlib.import_module(module_name)
    for name in names:
        getattr(mod, name)


@pytest.mark.parametrize("module_name,names", _ORCHESTRATOR_API_SUBMODULE_PUBLIC_NAMES)
def test_orchestrator_api_submodules_expose_direct_import_surface(
    module_name: str, names: tuple[str, ...],
) -> None:
    mod = importlib.import_module(module_name)
    for name in names:
        assert hasattr(mod, name), f"{module_name}.{name} missing after orchestrator path move"


@pytest.mark.parametrize("module_name,names", _ORCHESTRATOR_API_SUBMODULE_PUBLIC_NAMES)
def test_orchestrator_api_submodule_names_are_gettable(
    module_name: str, names: tuple[str, ...],
) -> None:
    mod = importlib.import_module(module_name)
    for name in names:
        getattr(mod, name)
