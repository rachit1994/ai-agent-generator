import json
from datetime import datetime
from types import SimpleNamespace

from workflow_pipelines.execution_modes.modes import baseline as baseline_mode
from workflow_pipelines.execution_modes.modes import guarded as guarded_mode
from workflow_pipelines.execution_modes.modes import guarded_pipeline as guarded_pipeline_mode


def _dt(iso: str) -> datetime:
    return datetime.fromisoformat(iso)


def test_baseline_trace_event_timestamps_match_latency(monkeypatch) -> None:
    times = iter([1.0, 1.1, 1.3, 1.8])

    def _fake_time() -> float:
        return next(times)

    def _fake_invoke_model(**_kwargs):  # type: ignore[no-untyped-def]
        return {
            "text": json.dumps(
                {
                    "answer": "ok",
                    "checks": [{"name": "schema", "passed": True}],
                    "refusal": None,
                }
            )
        }

    config = SimpleNamespace(
        implementation_model="fake-model",
        provider="fake-provider",
        provider_base_url=None,
        budgets=SimpleNamespace(timeout_ms=10, max_retries=0),
    )

    monkeypatch.setattr(baseline_mode.time, "time", _fake_time)
    monkeypatch.setattr(baseline_mode, "invoke_model", _fake_invoke_model)

    _output, events = baseline_mode.run_baseline("r", "t", "do thing", config)

    finalize = next(e for e in events if e["stage"] == "finalize")
    delta_ms = int((_dt(finalize["ended_at"]) - _dt(finalize["started_at"])).total_seconds() * 1000)
    assert delta_ms == finalize["latency_ms"]

    executor = next(e for e in events if e["stage"] == "executor")
    delta_ms = int((_dt(executor["ended_at"]) - _dt(executor["started_at"])).total_seconds() * 1000)
    assert delta_ms == executor["latency_ms"]


def test_guarded_trace_event_timestamps_match_latency(monkeypatch) -> None:
    times = iter([1.0, 1.01, 1.02, 1.03, 1.04, 1.1, 1.4, 1.45, 1.46, 1.8])

    def _fake_time() -> float:
        return next(times)

    def _fake_invoke_model(**_kwargs):  # type: ignore[no-untyped-def]
        return {
            "text": json.dumps(
                {
                    "answer": "ok",
                    "checks": [{"name": "schema", "passed": True}],
                    "refusal": None,
                }
            )
        }

    config = SimpleNamespace(
        implementation_model="fake-model",
        provider="fake-provider",
        provider_base_url=None,
        budgets=SimpleNamespace(timeout_ms=10, max_retries=0),
    )

    monkeypatch.setattr(guarded_pipeline_mode.time, "time", _fake_time)
    monkeypatch.setattr(guarded_pipeline_mode.model_adapter, "invoke_model", _fake_invoke_model)

    _output, events = guarded_mode.run_guarded("r", "t", "do thing", config)

    finalize = next(e for e in events if e["stage"] == "finalize")
    delta_ms = int((_dt(finalize["ended_at"]) - _dt(finalize["started_at"])).total_seconds() * 1000)
    assert delta_ms == finalize["latency_ms"]

    executor = next(e for e in events if e["stage"] == "executor")
    delta_ms = int((_dt(executor["ended_at"]) - _dt(executor["started_at"])).total_seconds() * 1000)
    assert delta_ms == executor["latency_ms"]

