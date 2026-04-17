from __future__ import annotations

import re


def extract_python_code(text: str) -> str | None:
    stripped = text.strip()
    if not stripped:
        return None
    if stripped.startswith("{") and '"answer"' in stripped[:200]:
        try:
            import json

            parsed = json.loads(stripped)
            if isinstance(parsed, dict) and isinstance(parsed.get("answer"), str):
                candidate = parsed["answer"].strip()
                if candidate:
                    stripped = candidate
        except Exception:
            pass
    fenced = re.search(r"```(?:python|py)\s*([\s\S]*?)\s*```", stripped, flags=re.IGNORECASE)
    if fenced:
        code = fenced.group(1).strip()
        return code if code else None
    if stripped.startswith("#!") or "def " in stripped or "\nimport " in f"\n{stripped}":
        return stripped
    return None

