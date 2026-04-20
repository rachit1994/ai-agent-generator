"""Enforce cross-heading import boundaries outside orchestrator/pipeline hubs."""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Final


_EXEMPT_PREFIXES: Final[tuple[tuple[str, ...], ...]] = (
    ("production_architecture", "local_runtime", "orchestrator"),
    ("workflow_pipelines", "production_pipeline_plan_artifact", "production_pipeline_task_to_promote"),
    ("workflow_pipelines", "strategy_overlay", "execution_modes"),
    ("workflow_pipelines", "traces_jsonl"),
)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[6]


def _is_exempt(parts: tuple[str, ...]) -> bool:
    return any(parts[: len(prefix)] == prefix for prefix in _EXEMPT_PREFIXES)


def _collect_heading_violations(src: Path, headings: set[str]) -> list[str]:
    violations: list[str] = []
    for py_path in src.rglob("*.py"):
        rel = py_path.relative_to(src)
        parts = rel.parts
        if "tests" in parts or _is_exempt(parts):
            continue
        violations.extend(_violations_for_file(py_path, rel, headings))
    return violations


def _violations_for_file(py_path: Path, rel: Path, headings: set[str]) -> list[str]:
    owner = rel.parts[0]
    tree = ast.parse(py_path.read_text(encoding="utf-8"))
    violations: list[str] = []
    for node in ast.walk(tree):
        violations.extend(_violations_for_node(node, owner, headings, rel))
    return violations


def _violations_for_node(node: ast.AST, owner: str, headings: set[str], rel: Path) -> list[str]:
    if isinstance(node, ast.Import):
        return _import_violations(node, owner, headings, rel)
    if isinstance(node, ast.ImportFrom):
        return _import_from_violations(node, owner, headings, rel)
    return []


def _import_violations(node: ast.Import, owner: str, headings: set[str], rel: Path) -> list[str]:
    violations: list[str] = []
    for alias in node.names:
        top = alias.name.split(".")[0]
        if top in headings and top != owner:
            violations.append(f"{rel}: import {alias.name}")
    return violations


def _import_from_violations(
    node: ast.ImportFrom, owner: str, headings: set[str], rel: Path,
) -> list[str]:
    if node.level != 0 or not node.module:
        return []
    top = node.module.split(".")[0]
    if top in headings and top != owner:
        return [f"{rel}: from {node.module} import ..."]
    return []


def test_cross_heading_imports_outside_exempt_hubs() -> None:
    src = _repo_root() / "src"
    headings = {path.name for path in src.iterdir() if path.is_dir()}
    violations = _collect_heading_violations(src, headings)
    assert not violations, "Cross-heading imports found:\\n" + "\\n".join(sorted(violations))
