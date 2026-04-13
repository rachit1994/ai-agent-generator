"""Phase 0: prove `pytest` executes DeepEval’s evaluation path without external LLM keys."""

from __future__ import annotations

from deepeval import assert_test
from deepeval.metrics.base_metric import BaseMetric
from deepeval.test_case import LLMTestCase, LLMTestCaseParams


class _StringEqualityMetric(BaseMetric):
    """Deterministic stand-in for LLM-backed metrics until compiler fixtures exist (Phase 2+)."""

    _required_params = [
        LLMTestCaseParams.INPUT,
        LLMTestCaseParams.ACTUAL_OUTPUT,
        LLMTestCaseParams.EXPECTED_OUTPUT,
    ]

    def __init__(self, threshold: float = 1.0) -> None:
        self.threshold = threshold
        self.async_mode = True

    def measure(self, test_case: LLMTestCase, *args: object, **kwargs: object) -> float:
        match = test_case.actual_output == test_case.expected_output
        self.score = 1.0 if match else 0.0
        self.success = self.score >= self.threshold
        return self.score

    async def a_measure(self, test_case: LLMTestCase, *args: object, **kwargs: object) -> float:
        return self.measure(test_case, *args, **kwargs)

    def is_successful(self) -> bool:
        return bool(self.success)

    @property
    def __name__(self) -> str:
        return "String Equality"


def test_deepeval_assert_test_runs() -> None:
    case = LLMTestCase(input="ping", actual_output="pong", expected_output="pong")
    assert_test(case, [_StringEqualityMetric()])
