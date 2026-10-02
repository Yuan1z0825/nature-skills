"""配置读写模块。

负责 school.json 的读取、写入、校验、备份。
配置路径：~/.config/lit-dl/school.json
"""

from __future__ import annotations

import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

try:
    import jsonschema  # type: ignore
except ImportError:
    jsonschema = None  # type: ignore

# 配置文件路径（支持环境变量覆盖，便于测试和多 profile）
CONFIG_DIR = Path(os.environ.get("LIT_DL_CONFIG_DIR", Path.home() / ".config" / "lit-dl"))
CONFIG_FILE = CONFIG_DIR / "school.json"

# schema 路径（相对于本文件）
SCHEMA_FILE = Path(__file__).resolve().parent.parent / "data" / "school.schema.json"


def load_schema() -> dict[str, Any]:
    """加载 JSON Schema。"""
    with open(SCHEMA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def config_exists() -> bool:
    """配置文件是否存在。"""
    return CONFIG_FILE.exists()


def validate(config: dict[str, Any]) -> list[str]:
    """校验配置是否符合 schema。

    返回错误消息列表，空列表表示通过。
    若 jsonschema 未安装则跳过 schema 校验，只做基本字段检查。
    """
    errors: list[str] = []

    # 基本字段检查（不依赖 jsonschema）
    if not isinstance(config, dict):
        return ["配置不是合法的 JSON 对象"]
    if "version" not in config:
        errors.append("缺少 version 字段")
    if "school" not in config or "name" not in config.get("school", {}):
        errors.append("缺少 school.name 字段")
    auth = config.get("auth", {})
    if "type" not in auth:
        errors.append("缺少 auth.type 字段")
    if "sso_domain" not in auth or not auth["sso_domain"]:
        errors.append("缺少 auth.sso_domain 字段")
    if not config.get("libraries"):
        errors.append("libraries 不能为空")

    # schema 校验（可选）
    if jsonschema is not None and not errors:
        try:
            jsonschema.validate(instance=config, schema=load_schema())
        except jsonschema.ValidationError as e:  # type: ignore
            errors.append(f"schema 校验失败：{e.message}")

    return errors


def load_config() -> Optional[dict[str, Any]]:
    """读取配置文件。

    返回配置字典，文件不存在返回 None。
    若 JSON 解析失败，自动备份旧文件并返回 None。
    """
    if not CONFIG_FILE.exists():
        return None

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        # 配置文件损坏，备份后返回 None
        backup = CONFIG_FILE.with_suffix(".json.broken")
        shutil.copy2(CONFIG_FILE, backup)
        try:
            CONFIG_FILE.unlink()
        except OSError:
            pass
        print(f"配置文件损坏，已备份到 {backup}，请重新配置。错误：{e}")
        return None


def save_config(config: dict[str, Any]) -> Path:
    """写入配置文件。

    自动创建目录，补充 configured_at 时间戳。
    返回配置文件路径。
    """
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    # 补充时间戳
    if not config.get("school", {}).get("configured_at"):
        config.setdefault("school", {})["configured_at"] = datetime.now().isoformat()

    # 校验
    errors = validate(config)
    if errors:
        raise ValueError(f"配置校验失败：{'; '.join(errors)}")

    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

    # 设置文件权限（仅属主可读写）
    os.chmod(CONFIG_FILE, 0o600)

    return CONFIG_FILE


def backup_config() -> Optional[Path]:
    """备份当前配置文件，返回备份路径。文件不存在返回 None。"""
    if not CONFIG_FILE.exists():
        return None
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = CONFIG_FILE.with_suffix(f".json.{timestamp}.bak")
    shutil.copy2(CONFIG_FILE, backup)
    return backup


def delete_config() -> bool:
    """删除配置文件（用于重新配置）。返回是否删除成功。"""
    if CONFIG_FILE.exists():
        backup_config()
        CONFIG_FILE.unlink()
        return True
    return False


def get_school_name() -> Optional[str]:
    """快捷获取学校名称。未配置返回 None。"""
    cfg = load_config()
    if cfg is None:
        return None
    return cfg.get("school", {}).get("name")


def get_auth_info() -> Optional[dict[str, Any]]:
    """快捷获取认证信息。未配置返回 None。"""
    cfg = load_config()
    if cfg is None:
        return None
    return cfg.get("auth")


if __name__ == "__main__":
    # CLI 自检
    if config_exists():
        cfg = load_config()
        if cfg:
            print(f"已配置学校：{cfg.get('school', {}).get('name', '未知')}")
            print(f"配置路径：{CONFIG_FILE}")
            errors = validate(cfg)
            if errors:
                print(f"校验警告：{errors}")
            else:
                print("配置校验通过")
        else:
            print("配置文件存在但损坏，请重新配置")
    else:
        print(f"尚未配置，配置文件路径：{CONFIG_FILE}")
