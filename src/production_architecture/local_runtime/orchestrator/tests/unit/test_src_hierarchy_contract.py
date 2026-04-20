"""Lock src hierarchy to architecture headings/subheadings."""

from __future__ import annotations

from pathlib import Path
import re


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[6]


def _expected_tree() -> dict[str, set[str]]:
    headings = _repo_root() / "docs" / "architecture" / "master-architecture-feature-completion-headings.md"
    out: dict[str, set[str]] = {}
    current: str | None = None
    for line in headings.read_text(encoding="utf-8").splitlines():
        heading = re.match(r"-\s+(\w+)\s*$", line)
        if heading:
            current = heading.group(1).lower()
            out.setdefault(current, set())
            continue
        subheading = re.match(r"\s*\|_\s+(\w+)\s*$", line)
        if subheading and current:
            out[current].add(subheading.group(1).lower())
    return out


def test_src_top_level_folders_match_headings_doc() -> None:
    expected = _expected_tree()
    src = _repo_root() / "src"
    actual = {p.name for p in src.iterdir() if p.is_dir()}
    assert actual == set(expected), (
        "src/ top-level folders must exactly match heading names from "
        "docs/architecture/master-architecture-feature-completion-headings.md"
    )


def test_each_heading_contains_all_documented_subheadings() -> None:
    expected = _expected_tree()
    src = _repo_root() / "src"
    for heading, subheadings in expected.items():
        for subheading in subheadings:
            assert (src / heading / subheading).is_dir(), f"Missing folder: src/{heading}/{subheading}"


def test_legacy_layout_roots_removed() -> None:
    root = _repo_root()
    assert not (root / "libs").exists()
    assert not (root / "src" / "production_architecture_what_runs_on_the_laptop").exists()
