"""Optional user-maintained institution preset loader.

The distributed schools.yaml is intentionally empty.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

try:
    import yaml  # type: ignore
except ImportError:
    yaml = None  # type: ignore

SCHOOLS_FILE = Path(__file__).resolve().parent.parent / "data" / "schools.yaml"


def _parse_scalar(value: str) -> Any:
    value = value.strip()
    if value in ("", "null", "None"):
        return None
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [part.strip().strip('"') for part in inner.split(",")]
    return value


def _load_schools_without_yaml(text: str) -> list[dict[str, Any]]:
    """读取本仓库固定格式的 schools.yaml，避免 PyYAML 缺失时预设库失效。"""
    schools: list[dict[str, Any]] = []
    current: Optional[dict[str, Any]] = None
    section: Optional[str] = None

    for raw in text.splitlines():
        stripped = raw.strip()
        if not stripped or stripped.startswith("#") or stripped == "schools:":
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        if stripped.startswith("- name:"):
            if current:
                schools.append(current)
            current = {"name": _parse_scalar(stripped.split(":", 1)[1]), "auth": {}}
            section = None
            continue
        if current is None:
            continue
        if indent == 4 and stripped.endswith(":"):
            section = stripped[:-1]
            current.setdefault(section, {})
            continue
        if ":" not in stripped:
            continue

        key, value = stripped.split(":", 1)
        if section and indent >= 6:
            current.setdefault(section, {})[key.strip()] = _parse_scalar(value)
        else:
            section = None
            current[key.strip()] = _parse_scalar(value)

    if current:
        schools.append(current)
    return schools


def load_schools() -> list[dict[str, Any]]:
    """加载预设学校库。优先用 PyYAML，缺失时使用内置简易解析器。"""
    if not SCHOOLS_FILE.exists():
        return []
    text = SCHOOLS_FILE.read_text(encoding="utf-8")
    if yaml is None:
        return _load_schools_without_yaml(text)
    data = yaml.safe_load(text)
    return data.get("schools", []) if data else []


def match_school(query: str) -> Optional[dict[str, Any]]:
    """模糊匹配学校。

    匹配顺序：精确名称 → 别名精确 → 包含匹配。
    返回匹配到的学校字典，未匹配返回 None。
    """
    query = query.strip().lower()
    if not query:
        return None

    schools = load_schools()
    if not schools:
        return None

    # 1. 精确匹配 name
    for s in schools:
        if s["name"].lower() == query:
            return s

    # 2. 别名精确匹配
    for s in schools:
        for alias in s.get("aliases", []):
            if alias.lower() == query:
                return s

    # 3. name 包含匹配
    for s in schools:
        if query in s["name"].lower():
            return s

    # 4. 别名包含匹配
    for s in schools:
        for alias in s.get("aliases", []):
            if query in alias.lower():
                return s

    return None


def list_school_names() -> list[str]:
    """返回所有预设学校名称列表。"""
    return [s["name"] for s in load_schools()]


if __name__ == "__main__":
    schools = load_schools()
    print(f"用户维护的机构预设数量：{len(schools)}")
