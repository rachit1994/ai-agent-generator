from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class Score:
    passed: bool
    reliability: float
    validity: float


@dataclass
class TraceEvent:
    run_id: str
    task_id: str
    mode: str
    model: str
    provider: str
    stage: str
    started_at: str
    ended_at: str
    latency_ms: int
    token_input: int
    token_output: int
    estimated_cost_usd: float
    retry_count: int
    errors: list[str] = field(default_factory=list)
    score: Score = field(default_factory=lambda: Score(False, 0.0, 0.0))
    metadata: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
