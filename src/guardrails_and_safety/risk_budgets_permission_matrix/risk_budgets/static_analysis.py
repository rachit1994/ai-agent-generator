"""Local static code quality and security gates (SWE-agent / OpenHands–class, no sandbox).

Runs without Docker: AST validation, high-signal dangerous-pattern detection,
optional ``ruff``, ``bandit``, and ``basedpyright`` / ``pyright`` when on PATH.
Results are persisted as ``static_gates_report.json`` for CTO hard-stops and human review.
"""

from __future__ import annotations

import ast
import json
import re
import shutil
import subprocess
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

REPORT_SCHEMA = "1.0"

# High-confidence security anti-patterns (aligned with common agent-harness checks).
_BLOCKING_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("subprocess_shell_true", re.compile(r"subprocess\s*\.\s*(?:call|run|Popen|check_output|check_call)\s*\([^)]*shell\s*=\s*True", re.I)),
    ("os_system", re.compile(r"\bos\.system\s*\(")),
    ("eval_call", re.compile(r"\beval\s*\(")),
    ("exec_call", re.compile(r"\bexec\s*\(")),
    ("compile_dangerous", re.compile(r"\bcompile\s*\([^,]+,\s*[^,]+,\s*['\"]exec['\"]", re.I)),
    ("__import__dynamic", re.compile(r"__import__\s*\(")),
    ("pickle_loads", re.compile(r"pickle\s*\.\s*(?:loads|load)\s*\(")),
    ("marshal_load", re.compile(r"\bmarshal\.load\s*\(")),
    ("pty_spawn", re.compile(r"\bpty\.spawn\s*\(")),
)

# Assignment to likely secrets (heuristic — OpenHands-style “no secrets in code”).
_SECRET_ASSIGN = re.compile(
    r"(?i)\b(?:password|passwd|api[_-]?key|secret|token|bearer|authorization)\b\s*=\s*['\"][^'\"]{4,}['\"]",
)

_WARNING_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("bare_except", re.compile(r"except\s*:")),
    ("except_pass", re.compile(r"except\s+[^:]+\s*:\s*pass\b")),
)


@contextmanager
def _temp_py_file(code: str) -> Iterator[Path]:
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as handle:
        handle.write(code)
        path = Path(handle.name)
    try:
        yield path
    finally:
        path.unlink(missing_ok=True)


def _syntax_ok(code: str) -> tuple[bool, str | None]:
    try:
        ast.parse(code, filename="<executor_output>", mode="exec")
    except SyntaxError as exc:
        return False, f"syntax_error:{exc.msg}:line{exc.lineno or 0}"
    return True, None


def _pattern_hits(code: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    blockers: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    for pid, pat in _BLOCKING_PATTERNS:
        if pat.search(code):
            blockers.append({"id": pid, "severity": "blocker", "pattern": pat.pattern})
    if _SECRET_ASSIGN.search(code):
        blockers.append({"id": "hardcoded_secret_assignment", "severity": "blocker", "pattern": "secret_like_assignment"})
    for wid, pat in _WARNING_PATTERNS:
        if pat.search(code):
            warnings.append({"id": wid, "severity": "warning", "pattern": pat.pattern})
    return blockers, warnings


def _run_ruff_if_available(code: str) -> dict[str, Any]:
    exe = shutil.which("ruff")
    if not exe:
        return {"ran": False, "skipped": "ruff_not_on_path"}
    try:
        with _temp_py_file(code) as tmp:
            proc = subprocess.run(
                [exe, "check", str(tmp), "--output-format", "json"],
                capture_output=True,
                text=True,
                timeout=60,
                check=False,
            )
        findings: list[dict[str, Any]] = []
        if proc.stdout.strip():
            try:
                raw = json.loads(proc.stdout)
                if isinstance(raw, list):
                    for item in raw[:50]:
                        if isinstance(item, dict):
                            findings.append(
                                {
                                    "code": item.get("code"),
                                    "message": item.get("message"),
                                    "location": item.get("location"),
                                }
                            )
            except json.JSONDecodeError:
                findings.append({"code": "ruff_json_parse", "message": proc.stdout[:500]})
        return {
            "ran": True,
            "exit_code": proc.returncode,
            "finding_count": len(findings),
            "findings": findings,
            "passed": proc.returncode == 0,
        }
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"ran": True, "error": type(exc).__name__, "passed": False, "skipped": False}


def _run_bandit_if_available(code: str) -> dict[str, Any]:
    exe = shutil.which("bandit")
    if not exe:
        return {"ran": False, "skipped": "bandit_not_on_path"}
    try:
        with _temp_py_file(code) as tmp:
            proc = subprocess.run(
                [exe, "-f", "json", "-q", str(tmp)],
                capture_output=True,
                text=True,
                timeout=90,
                check=False,
            )
        high_med: list[dict[str, Any]] = []
        low_notes: list[str] = []
        if proc.stdout.strip():
            try:
                data = json.loads(proc.stdout)
                for item in (data.get("results") or [])[:80]:
                    if not isinstance(item, dict):
                        continue
                    sev = str(item.get("issue_severity") or "").upper()
                    row = {
                        "test_id": item.get("test_id"),
                        "issue_severity": sev,
                        "issue_text": item.get("issue_text"),
                        "line_number": item.get("line_number"),
                    }
                    if sev in ("HIGH", "MEDIUM"):
                        high_med.append(row)
                    elif sev == "LOW":
                        low_notes.append(str(item.get("test_id") or "low"))
            except json.JSONDecodeError:
                return {"ran": True, "passed": False, "error": "bandit_json_parse", "stdout_excerpt": proc.stdout[:400]}
        passed = len(high_med) == 0
        return {
            "ran": True,
            "exit_code": proc.returncode,
            "passed": passed,
            "high_medium_findings": high_med,
            "low_severity_count": len(low_notes),
        }
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"ran": True, "error": type(exc).__name__, "passed": False, "skipped": False}


def _run_typechecker_if_available(code: str) -> dict[str, Any]:
    for name in ("basedpyright", "pyright"):
        exe = shutil.which(name)
        if exe:
            break
    else:
        return {"ran": False, "skipped": "basedpyright_or_pyright_not_on_path"}
    try:
        with _temp_py_file(code) as tmp:
            proc = subprocess.run(
                [exe, "--outputjson", str(tmp)],
                capture_output=True,
                text=True,
                timeout=90,
                check=False,
            )
        errors: list[dict[str, Any]] = []
        warns: list[dict[str, Any]] = []
        if proc.stdout.strip():
            try:
                data = json.loads(proc.stdout)
                for d in (data.get("generalDiagnostics") or data.get("diagnostics") or [])[:80]:
                    if not isinstance(d, dict):
                        continue
                    sev = str(d.get("severity") or "").lower()
                    entry = {
                        "message": d.get("message"),
                        "rule": d.get("rule") or d.get("ruleName"),
                        "range": d.get("range"),
                    }
                    if sev == "error":
                        errors.append(entry)
                    elif sev == "warning":
                        warns.append(entry)
            except json.JSONDecodeError:
                return {"ran": True, "tool": name, "passed": False, "error": "typechecker_json_parse"}
        passed = len(errors) == 0
        return {
            "ran": True,
            "tool": name,
            "exit_code": proc.returncode,
            "passed": passed,
            "errors": errors,
            "warnings": warns,
        }
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"ran": True, "tool": name, "error": type(exc).__name__, "passed": False, "skipped": False}


def run_static_code_gates(*, extracted_python: str | None, _answer_text: str = "") -> dict[str, Any]:
    """Analyze executor output. ``extracted_python`` may be None if no fenced / obvious code."""
    code = (extracted_python or "").strip()
    checks: list[dict[str, Any]] = []
    if not code:
        checks.append({"id": "python_present", "passed": True, "note": "no_extracted_python_skipped"})
        empty_tools = {"ran": False, "skipped": "no_python_source"}
        return {
            "schema_version": REPORT_SCHEMA,
            "passed_all": True,
            "blockers": [],
            "warnings": [],
            "checks": checks,
            "ruff": empty_tools,
            "bandit": empty_tools,
            "basedpyright": empty_tools,
        }

    ok, syn_err = _syntax_ok(code)
    checks.append({"id": "python_syntax", "passed": ok, "detail": syn_err})
    blockers, warnings = _pattern_hits(code)
    if not ok:
        blockers = [{"id": "syntax_error", "severity": "blocker", "detail": syn_err}] + blockers

    checks.append({"id": "security_patterns", "passed": len([b for b in blockers if b["id"] != "syntax_error"]) == 0})

    ruff_result = _run_ruff_if_available(code)
    if ruff_result.get("ran") and ruff_result.get("passed") is False:
        blockers.append(
            {
                "id": "ruff_violations",
                "severity": "blocker",
                "detail": f"count={ruff_result.get('finding_count', 0)}",
                "findings": ruff_result.get("findings") or [],
            }
        )
        checks.append({"id": "ruff", "passed": False})
    else:
        checks.append({"id": "ruff", "passed": True, "detail": ruff_result})

    bandit_result = _run_bandit_if_available(code)
    if bandit_result.get("ran") and bandit_result.get("passed") is False:
        hm = bandit_result.get("high_medium_findings") or []
        blockers.append(
            {
                "id": "bandit_high_or_medium",
                "severity": "blocker",
                "detail": f"count={len(hm)}",
                "findings": hm,
            }
        )
        checks.append({"id": "bandit", "passed": False})
    else:
        checks.append({"id": "bandit", "passed": True, "detail": bandit_result})

    br_result = _run_typechecker_if_available(code)
    if br_result.get("ran") and br_result.get("passed") is False:
        errs = br_result.get("errors") or []
        blockers.append(
            {
                "id": "typechecker_errors",
                "severity": "blocker",
                "detail": f"tool={br_result.get('tool')},count={len(errs)}",
                "findings": errs,
            }
        )
        checks.append({"id": "basedpyright", "passed": False})
    else:
        checks.append({"id": "basedpyright", "passed": True, "detail": br_result})

    passed_all = len(blockers) == 0
    return {
        "schema_version": REPORT_SCHEMA,
        "passed_all": passed_all,
        "blockers": blockers,
        "warnings": warnings,
        "checks": checks,
        "ruff": ruff_result,
        "bandit": bandit_result,
        "basedpyright": br_result,
        "source_excerpt": code[:2000] + ("…" if len(code) > 2000 else ""),
    }


def blocking_ids(report: dict[str, Any]) -> list[str]:
    return [str(b.get("id", "?")) for b in report.get("blockers") or [] if isinstance(b, dict)]
