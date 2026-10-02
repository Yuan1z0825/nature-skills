"""字段校验模块。

对用户填写的配置字段做实时可达性探测：
- sso_domain: DNS 解析 + TCP 443 + HTTPS 证书
- carsi_entry: HTTP GET 探测
- ezproxy_url: HTTP GET 探测登录表单

所有校验函数返回 (ok: bool, message: str)。
"""

from __future__ import annotations

import socket
import ssl
import urllib.parse
import urllib.request


def validate_sso_domain(domain: str, timeout: float = 5.0) -> tuple[bool, str]:
    """校验 SSO 域名：DNS 解析 + TCP 443 + HTTPS 证书。

    返回 (是否通过, 说明消息)。
    """
    domain = domain.strip().lower()
    if not domain:
        return False, "域名为空"

    # 去掉协议前缀
    for prefix in ("https://", "http://"):
        if domain.startswith(prefix):
            domain = domain[len(prefix):]
    domain = domain.split("/")[0]

    # DNS 解析
    try:
        addrs = socket.getaddrinfo(domain, 443, socket.AF_UNSPEC, socket.SOCK_STREAM)
    except socket.gaierror:
        return False, f"DNS 解析失败：{domain}，请检查域名拼写"

    # TCP 443 连接 + TLS 握手
    last_err = ""
    for family, socktype, proto, _, sockaddr in addrs:
        try:
            with socket.create_connection(sockaddr, timeout=timeout) as sock:
                ctx = ssl.create_default_context()
                with ctx.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert = ssock.getpeercert()
                    if cert is None:
                        return False, f"HTTPS 证书无效：{domain}"
            return True, f"SSO 域名可达：https://{domain}"
        except (socket.timeout, ConnectionRefusedError, OSError) as e:
            last_err = str(e)
            continue

    return False, f"无法连接到 https://{domain}（443 端口）：{last_err}"


def validate_carsi_entry(url: str, timeout: float = 8.0) -> tuple[bool, str]:
    """校验 CARSI 入口：HTTP GET 探测。

    判断标准：返回 2xx/3xx，且页面内容含「CARSI」「Shibboleth」或 SSO 跳转特征。
    """
    url = url.strip()
    if not url:
        return False, "CARSI 入口 URL 为空"

    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    try:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (lit-dl-config-validator)",
                "Accept": "text/html",
            },
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            status = resp.getcode()
            body = resp.read(4096).decode("utf-8", errors="ignore").lower()

            if status >= 400:
                return False, f"CARSI 入口返回 HTTP {status}"

            # 内容特征检查
            keywords = ["carsi", "shibboleth", "idp", "sso", "login", "登录", "统一身份"]
            matched = [k for k in keywords if k in body]
            if matched:
                return True, f"CARSI 入口可达，检测到特征：{', '.join(matched[:3])}"

            # 3xx 跳转也算通过（可能跳到 SSO）
            if 300 <= status < 400:
                location = resp.headers.get("Location", "")
                return True, f"CARSI 入口跳转到：{location}"

            return True, f"CARSI 入口可达（HTTP {status}），但未检测到明显 SSO 特征"

    except urllib.error.URLError as e:
        return False, f"CARSI 入口不可达：{e.reason}"
    except Exception as e:
        return False, f"CARSI 入口探测异常：{e}"


def validate_ezproxy_url(url: str, timeout: float = 8.0) -> tuple[bool, str]:
    """校验 EZproxy 地址：HTTP GET 探测登录表单。

    判断标准：页面含 password 输入框。
    """
    url = url.strip()
    if not url:
        return False, "EZproxy URL 为空"

    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    try:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (lit-dl-config-validator)",
                "Accept": "text/html",
            },
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            status = resp.getcode()
            body = resp.read(8192).decode("utf-8", errors="ignore").lower()

            if status >= 400:
                return False, f"EZproxy 返回 HTTP {status}"

            if "password" in body or "密码" in body:
                return True, "EZproxy 登录页可达，检测到密码输入框"

            return True, f"EZproxy 页面可达（HTTP {status}），但未检测到登录表单"

    except urllib.error.URLError as e:
        return False, f"EZproxy 不可达：{e.reason}"
    except Exception as e:
        return False, f"EZproxy 探测异常：{e}"


def validate_school_name(name: str) -> tuple[bool, str]:
    """校验学校名称基本格式。"""
    name = name.strip()
    if len(name) < 2:
        return False, "学校名称太短"
    if len(name) > 100:
        return False, "学校名称太长"
    return True, name


def validate_libraries(libraries: list[str]) -> tuple[bool, str]:
    """校验数据库清单。"""
    if not libraries:
        return False, "数据库清单不能为空"
    if len(libraries) > 50:
        return False, "数据库清单过长"
    return True, f"已选择 {len(libraries)} 个数据库"


# 已知数据库清单（用于向导多选提示）
KNOWN_DATABASES = [
    "知网 (CNKI)",
    "万方",
    "维普",
    "Web of Science",
    "Scopus",
    "IEEE Xplore",
    "ScienceDirect",
    "Springer Link",
    "Wiley Online Library",
    "ACS Publications",
    "RSC Publishing",
    "Nature",
    "Science",
    "Elsevier ScienceDirect",
    "Taylor & Francis",
    "SAGE Journals",
    "EBSCO",
    "ProQuest",
    "JSTOR",
    "中国知网",
]


if __name__ == "__main__":
    # 自检示例
    print("=== SSO 域名校验 ===")
    ok, msg = validate_sso_domain("login.university.example")
    print(f"  {ok}: {msg}")

    print("\n=== CARSI 入口校验 ===")
    ok, msg = validate_carsi_entry("https://www.carsi.edu.cn/")
    print(f"  {ok}: {msg}")
