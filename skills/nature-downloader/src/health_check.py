"""连通性自检模块。

下载前对配置做轻量可达性探测，结果缓存 10 分钟。
失败时给出具体排查建议。
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Optional

from config import CONFIG_DIR, load_config
from validators import validate_carsi_entry, validate_sso_domain

# 缓存文件
CACHE_FILE = CONFIG_DIR / "health_cache.json"
CACHE_TTL = 600  # 10 分钟


def _load_cache() -> Optional[dict[str, Any]]:
    if not CACHE_FILE.exists():
        return None
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def _save_cache(data: dict[str, Any]) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _clear_cache() -> None:
    if CACHE_FILE.exists():
        CACHE_FILE.unlink()


def _diagnose_failure(cfg: dict[str, Any]) -> list[str]:
    """根据配置内容给出排查建议。"""
    suggestions: list[str] = []
    auth = cfg.get("auth", {})
    sso_domain = auth.get("sso_domain", "")
    carsi_entry = auth.get("carsi_entry", "")

    suggestions.append("可能原因与建议：")

    if sso_domain:
        suggestions.append(
            f"1. 检查网络：当前是否在校园网内或已连 VPN？"
            f"校外访问 {sso_domain} 可能需要 VPN。"
        )
    if carsi_entry:
        suggestions.append(
            f"2. CARSI 入口可能变更：访问 https://www.carsi.edu.cn/ "
            f"确认贵校当前入口，或说「换学校」重新配置。"
        )
    suggestions.append("3. 学校认证服务可能临时不可用，稍后重试。")
    suggestions.append("4. 如持续失败，说「重新配置」进入向导修正参数。")

    return suggestions


def health_check(force: bool = False) -> dict[str, Any]:
    """执行连通性自检。

    参数：
        force: 是否跳过缓存强制检测

    返回：
        {
            "ok": bool,
            "checked_at": str,
            "cached": bool,
            "details": [...],
            "suggestions": [...]  # 仅失败时
        }
    """
    # 检查缓存
    if not force:
        cache = _load_cache()
        if cache and (time.time() - cache.get("checked_at_ts", 0)) < CACHE_TTL:
            cache["cached"] = True
            return cache

    cfg = load_config()
    if cfg is None:
        return {
            "ok": False,
            "checked_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "cached": False,
            "details": ["未找到配置，请先运行配置向导"],
            "suggestions": ["说「配置学校」或「/reconfig」进入配置向导"],
        }

    details: list[str] = []
    all_ok = True

    auth = cfg.get("auth", {})
    sso_domain = auth.get("sso_domain", "")
    carsi_entry = auth.get("carsi_entry", "")

    # 1. SSO 域名探测
    if sso_domain:
        ok, msg = validate_sso_domain(sso_domain)
        details.append(f"[SSO] {msg}")
        if not ok:
            all_ok = False
    else:
        details.append("[SSO] 未配置 sso_domain")
        all_ok = False

    # 2. CARSI 入口探测（如配置了）
    if carsi_entry:
        ok, msg = validate_carsi_entry(carsi_entry)
        details.append(f"[CARSI] {msg}")
        if not ok:
            all_ok = False
    else:
        details.append("[CARSI] 未配置 CARSI 入口（如该校无 CARSI 可忽略）")

    result: dict[str, Any] = {
        "ok": all_ok,
        "checked_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "checked_at_ts": time.time(),
        "cached": False,
        "details": details,
    }

    if not all_ok:
        result["suggestions"] = _diagnose_failure(cfg)

    # 写缓存
    _save_cache(result)

    return result


def clear_cache() -> None:
    """清除自检缓存（配置变更后调用）。"""
    _clear_cache()


if __name__ == "__main__":
    result = health_check(force=True)
    print(f"自检结果：{'通过' if result['ok'] else '失败'}")
    print(f"检测时间：{result['checked_at']}")
    for d in result.get("details", []):
        print(f"  {d}")
    for s in result.get("suggestions", []):
        print(f"  {s}")
