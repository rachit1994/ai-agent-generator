"""Keep architecture + layout inventory path snapshots honest."""

from __future__ import annotations

from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[5]


def _part_a_py_md_paths(root: Path) -> list[Path]:
    """Same set as ``find src libs ( -name '*.py' -o -name '*.md' ) ! -path '*/__pycache__/*'``."""
    out: list[Path] = []
    for base_name in ("src", "libs"):
        base = root / base_name
        for path in base.rglob("*"):
            if "__pycache__" in path.parts:
                continue
            if path.is_file() and path.suffix in (".py", ".md"):
                out.append(path)
    return out


def test_layout_inventory_part_a_path_count_matches_disk() -> None:
    """Snapshot: **215** ``.py`` / ``.md`` files under ``src/`` + ``libs/`` (see inventory Part A intro)."""
    root = _repo_root()
    paths = _part_a_py_md_paths(root)
    assert len(paths) == 215, (
        "Regenerate docs/architecture/repository-layout-from-completion-inventory.md Part A "
        f"and update this test if the curated tree grew or shrank; got {len(paths)}"
    )


def test_architecture_doc_test_py_inventory_matches_disk() -> None:
    """Snapshot: **69** `test_*.py` files (**68** under orchestrator `tests/`, **1** under repo-root `tests/`)."""
    root = _repo_root()
    orch_tests = root / "src" / "production_architecture_what_runs_on_the_laptop" / "orchestrator" / "tests"
    orch_count = len([p for p in orch_tests.rglob("test_*.py") if p.is_file()])
    top_tests = root / "tests"
    top_count = len([p for p in top_tests.glob("test_*.py") if p.is_file()])
    assert orch_count == 68, (
        "Update docs/architecture/master-architecture-feature-completion.md "
        f"(Python unit tests row + P2 regression row + changelog) and this test if intentional; got {orch_count}"
    )
    assert top_count == 1, (
        "Update docs/architecture/master-architecture-feature-completion.md "
        f"and this test if repo-root tests/ layout changed; got {top_count}"
    )
    assert orch_count + top_count == 69
