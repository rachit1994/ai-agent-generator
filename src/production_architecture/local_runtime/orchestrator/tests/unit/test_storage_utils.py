from __future__ import annotations

import json
from pathlib import Path

import pytest

from production_architecture.storage.storage.storage import (
    append_jsonl,
    read_json,
    read_jsonl,
    write_json,
)


def test_write_json_is_stable_and_creates_parent_dirs(tmp_path: Path) -> None:
    payload = {"z": 1, "a": {"d": 4, "b": 2}}
    out = tmp_path / "nested" / "artifact.json"
    write_json(out, payload)
    assert out.is_file()
    assert read_json(out) == payload
    assert out.read_text(encoding="utf-8") == '{\n  "a": {\n    "b": 2,\n    "d": 4\n  },\n  "z": 1\n}'


def test_append_jsonl_uses_stable_key_order_and_roundtrips(tmp_path: Path) -> None:
    out = tmp_path / "logs" / "events.jsonl"
    append_jsonl(out, {"z": 9, "a": 1})
    append_jsonl(out, {"c": 3, "b": 2})
    assert read_jsonl(out) == [{"a": 1, "z": 9}, {"b": 2, "c": 3}]
    assert out.read_text(encoding="utf-8").splitlines() == ['{"a":1,"z":9}', '{"b":2,"c":3}']


def test_read_jsonl_returns_empty_for_missing_file(tmp_path: Path) -> None:
    assert read_jsonl(tmp_path / "missing.jsonl") == []


def test_read_jsonl_raises_for_invalid_line(tmp_path: Path) -> None:
    out = tmp_path / "bad.jsonl"
    out.write_text('{"ok": true}\nnot-json\n', encoding="utf-8")
    with pytest.raises(json.JSONDecodeError):
        read_jsonl(out)


def test_write_json_rejects_non_finite_numbers(tmp_path: Path) -> None:
    out = tmp_path / "bad.json"
    with pytest.raises(ValueError):
        write_json(out, {"score": float("nan")})


def test_append_jsonl_rejects_non_finite_numbers(tmp_path: Path) -> None:
    out = tmp_path / "bad.jsonl"
    with pytest.raises(ValueError):
        append_jsonl(out, {"score": float("inf")})
