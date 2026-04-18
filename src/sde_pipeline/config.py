from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class GuardrailBudgets:
    max_tokens: int = 4096
    max_retries: int = 1
    planner_timeout_ms: int = 5000
    verifier_timeout_ms: int = 5000
    executor_timeout_ms: int = 8000


@dataclass(frozen=True)
class RunConfig:
    provider: str = "ollama"
    implementation_model: str = "qwen3:14b"
    support_model: str = "gemma4:latest"
    provider_base_url: str = "http://127.0.0.1:11434"
    fallback_triggers: tuple[str, ...] = (
        "validity_rate_below_0_85_after_stabilization",
        "guarded_pass_rate_below_baseline_after_two_iterations",
        "median_latency_impractical_for_local_runtime",
        "fallback_requires_full_ab_rerun_and_report_annotation",
    )
    budgets: GuardrailBudgets = GuardrailBudgets()


DEFAULT_CONFIG = RunConfig()


def config_snapshot() -> dict:
    return asdict(DEFAULT_CONFIG)
