from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _stable_json_dumps(value: Any, *, pretty: bool) -> str:
    if pretty:
        return json.dumps(value, indent=2, sort_keys=True, allow_nan=False)
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def ensure_dir(path: str | Path) -> None:
    Path(path).mkdir(parents=True, exist_ok=True)


def write_json(path: str | Path, value: Any) -> None:
    path_obj = Path(path)
    ensure_dir(path_obj.parent)
    path_obj.write_text(_stable_json_dumps(value, pretty=True), encoding="utf-8")


def append_jsonl(path: str | Path, value: Any) -> None:
    path_obj = Path(path)
    ensure_dir(path_obj.parent)
    with path_obj.open("a", encoding="utf-8") as handle:
        handle.write(_stable_json_dumps(value, pretty=False) + "\n")


def read_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def read_jsonl(path: str | Path) -> list[Any]:
    path_obj = Path(path)
    if not path_obj.is_file():
        return []
    rows: list[Any] = []
    for line in path_obj.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows
