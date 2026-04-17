from pathlib import Path

from orchestrator.runtime.utils import outputs_base


def test_outputs_base_prefers_repo_pyproject(tmp_path, monkeypatch) -> None:
    (tmp_path / "pyproject.toml").write_text("[project]\nname = 'x'\n", encoding="utf-8")
    sub = tmp_path / "nested"
    sub.mkdir()
    monkeypatch.chdir(sub)
    assert outputs_base() == tmp_path / "outputs"


def test_outputs_base_env_override(tmp_path, monkeypatch) -> None:
    target = tmp_path / "custom-out"
    target.mkdir()
    monkeypatch.setenv("SDE_OUTPUTS_ROOT", str(target))
    monkeypatch.chdir(tmp_path)
    assert outputs_base() == target


def test_outputs_base_falls_back_to_cwd_outputs(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    assert outputs_base() == tmp_path / "outputs"
