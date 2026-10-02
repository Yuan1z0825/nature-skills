"""配置向导模块。

7 步交互式配置流程，供 AI 调用。
每一步返回一个 prompt 给用户，并接收用户输入进行校验。

使用方式（AI 调用）：
    from wizard import Wizard
    w = Wizard()
    # Step 1
    prompt = w.start()                # 返回给用户的提问
    # 用户回答后
    result = w.handle_step1(user_input)
    # result = {"next": "step2"|"retry"|"done", "prompt": str, "data": dict}

发行包不包含任何学校预设；机构名称和入口仅由用户在运行时提供。
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional
from urllib.parse import parse_qs, urlparse

from config import save_config, backup_config, delete_config, CONFIG_FILE
from schools_loader import match_school, list_school_names
from validators import (
    KNOWN_DATABASES,
    validate_carsi_entry,
    validate_ezproxy_url,
    validate_libraries,
    validate_school_name,
    validate_sso_domain,
)


def infer_access_from_url(url: str) -> dict[str, Any]:
    """Infer the likely library access route from a user-provided resource URL."""
    raw_url = url.strip()
    parsed = urlparse(raw_url if "://" in raw_url else f"https://{raw_url}")
    host = parsed.netloc.lower()
    path = parsed.path.lower()
    query = parse_qs(parsed.query)
    service = query.get("service", [""])[0]
    service_host = urlparse(service).netloc.lower() if service else ""

    result: dict[str, Any] = {
        "resource_entry": raw_url,
        "entry_host": host,
        "entry_type": "resource_entry",
        "auth_type": "custom",
        "sso_domain": host,
        "service_host": service_host or None,
        "institution_hint": None,
        "notes": "",
    }

    if "metaersp" in host or "metaauth" in host:
        result.update(
            {
                "entry_type": "resource_portal",
                "auth_type": "cas",
                "sso_domain": host,
                "institution_hint": host.split(".", 1)[0] if "." in host else None,
                "notes": "资源聚合门户；先从该入口进入，必要时由门户跳转到统一身份认证。",
            }
        )
    elif "/authserver/login" in path or host.startswith("cas."):
        hint = None
        if service_host:
            service_parts = urlparse(service).path.strip("/").split("/")
            if len(service_parts) >= 2:
                hint = service_parts[1]
        result.update(
            {
                "entry_type": "cas_login",
                "auth_type": "cas",
                "sso_domain": host,
                "institution_hint": hint,
                "notes": "CAS 登录入口；若 service 指向资源聚合平台，后续应回到该平台继续进入数据库。",
            }
        )
    elif "ezproxy" in host or "libproxy" in host:
        result.update({"entry_type": "ezproxy", "auth_type": "custom", "notes": "图书馆远程访问代理入口。"})
    elif "webvpn" in host or "vpn" in host:
        result.update({"entry_type": "webvpn", "auth_type": "custom", "notes": "WebVPN 入口。"})
    elif "shibboleth" in path or "carsi" in host:
        result.update({"entry_type": "carsi", "auth_type": "sso", "notes": "CARSI/Shibboleth 机构认证入口。"})

    return result


class Wizard:
    """配置向导状态机。

    状态流转：
        step1 (学校名) ->
            命中预设 -> step4 (数据库确认) -> step6 (自检) -> step7 (保存)
            未命中 -> step2 (CARSI自查) -> step3 (SSO域名) -> step4 -> step6 -> step7
                                                   或 step5 (EZproxy) -> step6 -> step7
    """

    def __init__(self) -> None:
        self.state: str = "step1"
        self.data: dict[str, Any] = {}
        self.matched_preset: Optional[dict[str, Any]] = None

    # ===== Step 1: 询问学校名称 =====
    def start(self) -> str:
        """返回首步提问。"""
        self.state = "step1"
        return (
            "你好！我是文献下载助手。首次使用需要先配置你的图书馆资源入口（只需一次）。\n\n"
            "请先发你平时进入图书馆电子资源/数据库的平台链接。\n"
            "可以是资源门户、数据库列表、Web of Science 入口、某个数据库详情页，"
            "或跳转到统一身份认证的登录链接。\n\n"
            "我会先根据链接判断 CAS/CARSI/EZproxy/WebVPN/聚合门户等授权路径；"
            "发行包不内置学校名称或认证地址。"
        )

    def handle_step1(self, user_input: str) -> dict[str, Any]:
        """处理资源入口链接；非 URL 输入按旧的学校名预设兜底。"""
        value = user_input.strip()
        if not value:
            return {"next": "retry", "prompt": "输入不能为空，请粘贴图书馆电子资源或数据库入口链接："}

        if "://" in value or "." in value:
            inferred = infer_access_from_url(value)
            self.data.update(inferred)
            self.data["school_name"] = inferred.get("institution_hint") or inferred["entry_host"]
            self.data["source"] = "resource_url"
            self.data["auth_type"] = inferred["auth_type"]
            self.data["sso_domain"] = inferred["sso_domain"]
            self.data["carsi_entry"] = inferred["resource_entry"]
            self.data["libraries"] = ["Web of Science", "ScienceDirect", "Springer", "IEEE Xplore", "知网", "ACS"]
            self.data["notes"] = inferred.get("notes", "")
            self.data["discovery"] = {"resource_entry_url": inferred["resource_entry"]}
            if inferred["entry_type"] == "resource_portal":
                self.data["discovery"]["resource_portal_url"] = inferred["resource_entry"]
            if inferred.get("service_host"):
                self.data["discovery"]["auth_service_host"] = inferred["service_host"]

            self.state = "step4"
            return {
                "next": "step4",
                "prompt": (
                    "已根据资源链接识别授权路径：\n"
                    f"  入口类型：{inferred['entry_type']}\n"
                    f"  认证类型：{inferred['auth_type']}\n"
                    f"  SSO 域名：{inferred['sso_domain']}\n"
                    f"  资源入口：{inferred['resource_entry']}\n\n"
                    "确认先使用这组配置吗？\n"
                    "  1. 确认，继续自检\n"
                    "  2. 我想调整数据库清单\n"
                    "  3. 改用手动配置"
                ),
                "data": {"inferred": inferred},
            }

        name = value

        ok, msg = validate_school_name(name)
        if not ok:
            return {"next": "retry", "prompt": f"{msg}，请重新输入资源链接或学校名称："}

        # 查预设库
        preset = match_school(name)
        if preset:
            self.matched_preset = preset
            self.data["school_name"] = preset["name"]
            self.data["source"] = "preset"

            # 预填预设库的配置
            auth = preset.get("auth", {})
            self.data["auth_type"] = auth.get("type", "cas")
            self.data["sso_domain"] = auth.get("sso_domain", "")
            self.data["carsi_entry"] = auth.get("carsi_entry", "")
            self.data["libraries"] = preset.get("libraries", [])
            self.data["notes"] = preset.get("notes", "")

            self.state = "step4"
            return {
                "next": "step4",
                "prompt": (
                    f"已匹配到预设学校：{preset['name']}\n"
                    f"  认证类型：{auth.get('type', '未知')}\n"
                    f"  SSO 域名：{auth.get('sso_domain', '未知')}\n"
                    f"  CARSI 入口：{auth.get('carsi_entry', '未配置')}\n"
                    f"  预设数据库：{', '.join(preset.get('libraries', []))}\n\n"
                    "确认使用以上配置吗？\n"
                    "  1. 确认，直接完成配置\n"
                    "  2. 我想调整数据库清单\n"
                    "  3. 这不是我的学校，重新输入"
                ),
                "data": {"matched": preset["name"]},
            }

        # 未命中预设，进入自助填写
        self.data["school_name"] = name
        self.data["source"] = "manual"
        self.state = "step2"
        return {
            "next": "step2",
            "prompt": (
                f"未在预设库中匹配到「{name}」，进入自助配置向导。\n\n"
                "Step 2: 你的学校/单位是否接入 CARSI 联邦认证？\n"
                "（CARSI 是高校统一身份认证联邦，查询入口：https://www.carsi.edu.cn/）\n\n"
                "  1. 是，已接入 CARSI\n"
                "  2. 否 / 不清楚，走图书馆远程访问（EZproxy）\n"
                "  3. 都没有，我用 VPN 连校园网"
            ),
        }

    # ===== Step 2: CARSI 自查 =====
    def handle_step2(self, user_input: str) -> dict[str, Any]:
        """处理 CARSI 选择。"""
        choice = user_input.strip()
        if choice == "1":
            self.data["use_carsi"] = True
            self.state = "step2b"
            return {
                "next": "step2b",
                "prompt": (
                    "请粘贴贵校的 CARSI 入口 URL。\n"
                    "（可在 https://www.carsi.edu.cn/ 成员机构列表中找到，"
                    "例如 https://login.university.example/idp/shibboleth；请使用本机构实际入口）\n\n"
                    "如果找不到，输入「跳过」留空，后续可手动补充。"
                ),
            }
        elif choice == "2":
            self.data["use_carsi"] = False
            self.state = "step3"
            return {
                "next": "step3",
                "prompt": (
                    "你选择了图书馆远程访问（EZproxy）方式。\n\n"
                    "Step 3: 请输入贵校统一身份认证域名。\n"
                    "（例如 login.university.example；请以本机构实际页面为准）"
                ),
            }
        elif choice == "3":
            self.data["use_carsi"] = False
            self.data["use_vpn"] = True
            self.state = "step3"
            return {
                "next": "step3",
                "prompt": (
                    "好的，使用 VPN 方式。\n"
                    "请先确保已连接校园 VPN，然后输入贵校统一身份认证域名。\n"
                    "（例如 login.university.example；请使用本机构实际域名）"
                ),
            }
        return {"next": "retry", "prompt": "请输入 1、2 或 3："}

    # ===== Step 2b: CARSI 入口 URL =====
    def handle_step2b(self, user_input: str) -> dict[str, Any]:
        """处理 CARSI 入口 URL 输入。"""
        url = user_input.strip()
        if url in ("跳过", "skip", ""):
            self.data["carsi_entry"] = ""
            self.state = "step3"
            return {
                "next": "step3",
                "prompt": (
                    "已跳过 CARSI 入口（后续可补充）。\n\n"
                    "Step 3: 请输入贵校统一身份认证域名。\n"
                    "（例如 login.university.example；请使用本机构实际域名）"
                ),
            }

        # 校验
        ok, msg = validate_carsi_entry(url)
        if not ok:
            return {
                "next": "retry",
                "prompt": f"{msg}\n\n请重新输入 CARSI 入口 URL，或输入「跳过」留空：",
            }

        self.data["carsi_entry"] = url
        self.state = "step3"
        return {
            "next": "step3",
            "prompt": (
                f"CARSI 入口校验通过。\n\n"
                "Step 3: 请输入贵校统一身份认证域名。\n"
                "（例如 login.university.example；请使用本机构实际域名）"
            ),
        }

    # ===== Step 3: SSO 域名 =====
    def handle_step3(self, user_input: str) -> dict[str, Any]:
        """处理 SSO 域名输入。"""
        domain = user_input.strip()
        if not domain:
            return {"next": "retry", "prompt": "域名不能为空，请重新输入："}

        ok, msg = validate_sso_domain(domain)
        if not ok:
            return {
                "next": "retry",
                "prompt": f"{msg}\n\n请重新输入本机构的 SSO 域名（如 login.university.example）：",
            }

        self.data["sso_domain"] = domain.split("://")[-1].split("/")[0]
        # 如果还没设 auth_type，默认 cas
        if "auth_type" not in self.data:
            self.data["auth_type"] = "cas"

        # 如果走 EZproxy 路径
        if not self.data.get("use_carsi", True) and not self.data.get("use_vpn"):
            self.state = "step5"
            return {
                "next": "step5",
                "prompt": (
                    f"SSO 域名校验通过：{msg}\n\n"
                    "Step 5: 请输入贵校图书馆 EZproxy 登录地址。\n"
                    "（提示：使用 EZproxy 前通常需先在图书馆网站开通「远程访问」权限）\n\n"
                    "如果不确定，输入「跳过」可稍后补充。"
                ),
            }

        self.state = "step4"
        return {
            "next": "step4",
            "prompt": (
                f"SSO 域名校验通过：{msg}\n\n"
                "Step 4: 你常下载的数据库有哪些？\n"
                f"可选：{', '.join(KNOWN_DATABASES[:10])} ...\n\n"
                "请输入数据库名称，多个用逗号或空格分隔："
            ),
        }

    # ===== Step 4: 数据库多选 =====
    def handle_step4(self, user_input: str) -> dict[str, Any]:
        """处理数据库选择。"""
        if user_input.strip() in ("确认", "1", "ok", "yes", "好"):
            # 预设学校确认流程
            if not self.data.get("libraries"):
                return {"next": "retry", "prompt": "请输入数据库名称："}
        else:
            # 解析输入
            libs = [s.strip() for s in user_input.replace(",", " ").split() if s.strip()]
            if libs:
                self.data["libraries"] = libs

        ok, msg = validate_libraries(self.data.get("libraries", []))
        if not ok:
            return {"next": "retry", "prompt": f"{msg}，请重新输入："}

        self.state = "step6"
        return {
            "next": "step6",
            "prompt": (
                f"已记录 {len(self.data['libraries'])} 个数据库。\n\n"
                "Step 6: 正在进行连通性自检..."
            ),
        }

    # ===== Step 5: EZproxy 地址 =====
    def handle_step5(self, user_input: str) -> dict[str, Any]:
        """处理 EZproxy 地址输入。"""
        url = user_input.strip()
        if url in ("跳过", "skip", ""):
            self.data["ezproxy_url"] = None
            self.state = "step4"
            return {
                "next": "step4",
                "prompt": (
                    "已跳过 EZproxy。\n\n"
                    "Step 4: 你常下载的数据库有哪些？\n"
                    "请输入数据库名称，多个用逗号或空格分隔："
                ),
            }

        ok, msg = validate_ezproxy_url(url)
        if not ok:
            return {
                "next": "retry",
                "prompt": f"{msg}\n\n请重新输入 EZproxy 地址，或输入「跳过」：",
            }

        self.data["ezproxy_url"] = url
        self.state = "step4"
        return {
            "next": "step4",
            "prompt": (
                f"EZproxy 校验通过：{msg}\n\n"
                "Step 4: 你常下载的数据库有哪些？\n"
                "请输入数据库名称，多个用逗号或空格分隔："
            ),
        }

    # ===== Step 6: 连通性自检 =====
    def handle_step6(self, user_input: str = "") -> dict[str, Any]:
        """执行连通性自检。"""
        # 延迟导入避免循环依赖
        from health_check import health_check, clear_cache

        # 先保存临时配置再做自检
        try:
            temp_config = self._build_config()
        except ValueError as e:
            return {"next": "retry", "prompt": f"配置构建失败：{e}"}

        # 临时保存用于自检
        clear_cache()
        save_config(temp_config)
        result = health_check(force=True)

        self.state = "step7"
        details_text = "\n".join(f"  {d}" for d in result.get("details", []))
        if result["ok"]:
            return {
                "next": "step7",
                "prompt": (
                    f"连通性自检通过：\n{details_text}\n\n"
                    "Step 7: 确认保存配置吗？\n  1. 确认保存\n  2. 重新配置"
                ),
            }
        else:
            suggestions = "\n".join(f"  {s}" for s in result.get("suggestions", []))
            return {
                "next": "step7",
                "prompt": (
                    f"连通性自检未完全通过：\n{details_text}\n\n"
                    f"{suggestions}\n\n"
                    "Step 7: 如何处理？\n"
                    "  1. 仍然保存（可后续修正）\n"
                    "  2. 重新配置"
                ),
                "data": {"warnings": result.get("details", [])},
            }

    # ===== Step 7: 持久化 =====
    def handle_step7(self, user_input: str) -> dict[str, Any]:
        """处理最终保存确认。"""
        choice = user_input.strip()
        if choice in ("2", "重新配置", "重新"):
            delete_config()
            self.__init__()
            return {"next": "step1", "prompt": self.start()}

        # 保存
        try:
            config = self._build_config()
            # 附加警告（如有）
            if self.data.get("warnings"):
                config["_warnings"] = self.data["warnings"]
            path = save_config(config)
            return {
                "next": "done",
                "prompt": (
                    f"已为「{self.data['school_name']}」完成配置！\n"
                    f"配置文件：{path}\n\n"
                    "现在可以直接下载文献了。如需切换学校，随时说「换学校」或「/reconfig」。"
                ),
                "data": {"school": self.data["school_name"], "path": str(path)},
            }
        except ValueError as e:
            return {"next": "retry", "prompt": f"保存失败：{e}\n请检查后重试："}

    # ===== 调度入口 =====
    def handle(self, user_input: str) -> dict[str, Any]:
        """根据当前状态调度到对应处理函数。"""
        handlers = {
            "step1": self.handle_step1,
            "step2": self.handle_step2,
            "step2b": self.handle_step2b,
            "step3": self.handle_step3,
            "step4": self.handle_step4,
            "step5": self.handle_step5,
            "step6": self.handle_step6,
            "step7": self.handle_step7,
        }
        handler = handlers.get(self.state)
        if handler is None:
            self.state = "step1"
            return {"next": "step1", "prompt": self.start()}
        return handler(user_input)

    # ===== 非交互式：预设学校一键配置 =====
    def configure_from_preset(self, school_name: str) -> dict[str, Any]:
        """预设学校一键配置（非交互式）。

        成功返回保存后的配置字典，失败抛 ValueError。
        """
        preset = match_school(school_name)
        if not preset:
            raise ValueError(f"预设库中未找到「{school_name}」")

        auth = preset.get("auth", {})
        config = {
            "version": 1,
            "school": {
                "name": preset["name"],
                "code": preset.get("aliases", [""])[0] if preset.get("aliases") else None,
                "configured_at": datetime.now().isoformat(),
                "source": "preset",
            },
            "auth": {
                "type": auth.get("type", "cas"),
                "sso_domain": auth.get("sso_domain", ""),
                "carsi_entry": auth.get("carsi_entry") or None,
                "carsi_sp_entity_id": None,
            },
            "proxy": {
                "type": None,
                "ezproxy_url": None,
            },
            "libraries": preset.get("libraries", []),
            "discovery": preset.get("discovery", {}),
            "notes": preset.get("notes", ""),
        }

        path = save_config(config)
        return {"config": config, "path": str(path)}

    # ===== 非交互式：资源入口链接配置 =====
    def configure_from_resource_url(self, resource_url: str) -> dict[str, Any]:
        """Configure from a library resource portal or authentication URL."""
        inferred = infer_access_from_url(resource_url)
        self.data.update(inferred)
        self.data["school_name"] = inferred.get("institution_hint") or inferred["entry_host"]
        self.data["source"] = "resource_url"
        self.data["auth_type"] = inferred["auth_type"]
        self.data["sso_domain"] = inferred["sso_domain"]
        self.data["carsi_entry"] = inferred["resource_entry"]
        self.data["libraries"] = ["Web of Science", "ScienceDirect", "Springer", "IEEE Xplore", "知网", "ACS"]
        self.data["notes"] = inferred.get("notes", "")
        self.data["discovery"] = {"resource_entry_url": inferred["resource_entry"]}
        if inferred["entry_type"] == "resource_portal":
            self.data["discovery"]["resource_portal_url"] = inferred["resource_entry"]
        if inferred.get("service_host"):
            self.data["discovery"]["auth_service_host"] = inferred["service_host"]

        config = self._build_config()
        path = save_config(config)
        return {"config": config, "path": str(path), "inferred": inferred}

    # ===== 内部：构建配置字典 =====
    def _build_config(self) -> dict[str, Any]:
        """从向导收集的数据构建配置字典。"""
        if not self.data.get("school_name"):
            raise ValueError("学校名称未设置")
        if not self.data.get("sso_domain"):
            raise ValueError("SSO 域名未设置")
        if not self.data.get("libraries"):
            raise ValueError("数据库清单未设置")

        return {
            "version": 1,
            "school": {
                "name": self.data["school_name"],
                "code": None,
                "configured_at": datetime.now().isoformat(),
                "source": self.data.get("source", "manual"),
            },
            "auth": {
                "type": self.data.get("auth_type", "cas"),
                "sso_domain": self.data["sso_domain"],
                "carsi_entry": self.data.get("carsi_entry") or None,
                "carsi_sp_entity_id": None,
            },
            "proxy": {
                "type": "ezproxy" if self.data.get("ezproxy_url") else None,
                "ezproxy_url": self.data.get("ezproxy_url") or None,
            },
            "libraries": self.data["libraries"],
            "discovery": self.data.get("discovery", {}),
            "notes": self.data.get("notes", ""),
        }


if __name__ == "__main__":
    # 非交互式一键配置示例
    w = Wizard()
    try:
        result = w.configure_from_preset("交大")
        print(f"配置成功：{result['config']['school']['name']}")
        print(f"配置文件：{result['path']}")
    except ValueError as e:
        print(f"配置失败：{e}")
        print(f"配置文件路径：{CONFIG_FILE}")
