from __future__ import annotations

from pathlib import Path

from orchestrator.api.repo_index import build_repo_index


def test_build_repo_index_rejects_malformed_path_scopes(tmp_path: Path) -> None:
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "a.py").write_text("x = 1\n", encoding="utf-8")

    out = build_repo_index(
        tmp_path,
        path_scopes=["src/**", ""],  # malformed: blank entry
        max_files=10,
    )

    assert out["file_count"] == 0
    assert out["paths"] == []


def test_build_repo_index_rejects_invalid_max_files_type_or_value(tmp_path: Path) -> None:
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "a.py").write_text("x = 1\n", encoding="utf-8")

    out_bool = build_repo_index(tmp_path, path_scopes=["src/**"], max_files=True)  # type: ignore[arg-type]
    assert out_bool["file_count"] == 0
    assert out_bool["paths"] == []

    out_zero = build_repo_index(tmp_path, path_scopes=["src/**"], max_files=0)
    assert out_zero["file_count"] == 0
    assert out_zero["paths"] == []
