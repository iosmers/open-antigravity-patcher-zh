import json
import sys
import urllib.request
import urllib.error
import webbrowser

from patcher.constants import VERSION, COLOR_CYAN, COLOR_GREEN, COLOR_YELLOW, COLOR_RED, COLOR_BOLD, COLOR_UNDERLINE
from patcher.utils.console import color, link, info, ok, warn, err, hint, _frame_border, _frame_row


GITHUB_REPO = "AvenCores/open-antigravity-patcher"
RELEASES_URL = f"https://github.com/{GITHUB_REPO}/releases"
ISSUES_URL = f"https://github.com/{GITHUB_REPO}/issues"
API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
GOIDA_VPN_URL = "https://github.com/AvenCores/goida-vpn-configs"

LAST_UPDATE_RESULT = None


def get_last_update_result():
    return LAST_UPDATE_RESULT


def set_last_update_result(result):
    global LAST_UPDATE_RESULT
    LAST_UPDATE_RESULT = result


def print_network_error_warning():
    """当交互式检查更新失败时，打印醒目的警告和 VPN 建议。"""
    warn("无法检查更新（网络错误）。")
    vpn_link = link(GOIDA_VPN_URL, "goida-vpn-configs", COLOR_CYAN, COLOR_UNDERLINE)
    hint("建议：开启 VPN 以连接 GitHub 并检查更新。")
    hint(f"免费 VPN 配置：{vpn_link}（AvenCores 自动更新的 V2Ray/VLESS/Hysteria 配置）")


def print_network_error_banner():
    """当更新检查因网络错误失败时，在主菜单中打印带边框的警告横幅。"""
    vpn_link = link(GOIDA_VPN_URL, "goida-vpn-configs", COLOR_CYAN, COLOR_UNDERLINE)
    print(f"  {_frame_border('╔', '═', '╗', COLOR_YELLOW)}")
    print(f"  {_frame_row(color('警告：检查更新失败（网络错误）', COLOR_YELLOW, COLOR_BOLD), accent=COLOR_YELLOW)}")
    print(f"  {_frame_row(color('请开启 VPN 以在 GitHub 上检查更新', COLOR_CYAN, COLOR_BOLD), accent=COLOR_YELLOW)}")
    print(f"  {_frame_row(color(f'免费 VPN 配置：{vpn_link}', COLOR_CYAN), accent=COLOR_YELLOW)}")
    print(f"  {_frame_border('╚', '═', '╝', COLOR_YELLOW)}")
    print()



def print_update_status_notice():
    """在主菜单中打印更新提示、已是最新状态，或网络错误警告横幅。"""
    if LAST_UPDATE_RESULT == "network_error":
        print_network_error_banner()
    elif isinstance(LAST_UPDATE_RESULT, tuple) and LAST_UPDATE_RESULT[0] == "update_available":
        _, tag, url = LAST_UPDATE_RESULT
        info(f"发现新版本：{color(tag, COLOR_GREEN, COLOR_BOLD)}（当前：{color(VERSION, COLOR_YELLOW)}）")
        hint(f"下载地址：{color(url, COLOR_CYAN)}")
        print()
    elif LAST_UPDATE_RESULT == "up_to_date":
        ok(f"补丁工具已是最新版本（v{VERSION}）")
        print()


def _parse_version(v):
    """将形如 '1.2.6' 的版本字符串解析为整数元组。"""
    v = v.strip().lstrip("vV")
    parts = []
    for p in v.split("."):
        try:
            parts.append(int(p))
        except ValueError:
            break
    return tuple(parts)


def _fetch_latest_release(timeout=5):
    """通过 GitHub API 获取最新发布信息。返回 (tag, html_url) 或 (None, None)。"""
    req = urllib.request.Request(API_URL, headers={
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": f"OpenAGPatcher/{VERSION}",
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            tag = data.get("tag_name", "")
            html_url = data.get("html_url", "")
            return tag, html_url
    except Exception:
        return None, None


def check_for_updates(silent=True, timeout=5):
    """检查更新。若有可用更新则返回 True。

    silent=True 时，仅在发现更新时打印消息。
    silent=False 时，总是打印结果。
    """
    global LAST_UPDATE_RESULT
    tag, url = _fetch_latest_release(timeout=timeout)

    if tag is None:
        LAST_UPDATE_RESULT = "network_error"
        if not silent:
            print_network_error_warning()
        return False

    current = _parse_version(VERSION)
    latest = _parse_version(tag)

    if latest > current:
        LAST_UPDATE_RESULT = ("update_available", tag, url)
        if not silent:
            info(f"发现新版本：{color(tag, COLOR_GREEN, COLOR_BOLD)}（当前：{color(VERSION, COLOR_YELLOW)}）")
            hint(f"下载地址：{color(url, COLOR_CYAN)}")
        return True

    LAST_UPDATE_RESULT = "up_to_date"
    if not silent:
        ok(f"已是最新版本（v{VERSION}）")
    return False


def open_releases_page():
    """在默认浏览器中打开 GitHub 发布页面。"""
    webbrowser.open(RELEASES_URL)
    ok(f"正在打开：{color(RELEASES_URL, COLOR_CYAN)}")


def open_issues_page():
    """在默认浏览器中打开 GitHub issues 页面。"""
    webbrowser.open(ISSUES_URL)
    ok(f"正在打开：{color(ISSUES_URL, COLOR_CYAN)}")


def handle_patch_failure():
    """处理打补丁失败或未找到特征签名的情况。

    会检查更新：
    - 若有可用更新，提示打开发布页面进行安装。
    - 若已是最新版本（或没有更新），提示在 GitHub 上创建 issue。
    """
    from patcher.cli import confirmed

    print()
    info("正在检查补丁工具更新……")
    has_update = check_for_updates(silent=True)

    if has_update and isinstance(LAST_UPDATE_RESULT, tuple) and LAST_UPDATE_RESULT[0] == "update_available":
        _, tag, url = LAST_UPDATE_RESULT
        info(f"Open Antigravity Patcher 有可用更新：{color(tag, COLOR_GREEN, COLOR_BOLD)}（当前：{color(VERSION, COLOR_YELLOW)}）")
        hint(f"下载地址：{color(url, COLOR_CYAN)}")
        if confirmed("补丁工具有可用更新，是否打开发布页面进行安装？"):
            webbrowser.open(url or RELEASES_URL)
            ok(f"正在打开：{color(url or RELEASES_URL, COLOR_CYAN)}")
    else:
        if LAST_UPDATE_RESULT == "up_to_date":
            ok(f"你正在使用最新版本的 Open Antigravity Patcher（v{VERSION}）。")

        hint(f"问题追踪页：{color(ISSUES_URL, COLOR_CYAN)}")
        if confirmed("是否打开 GitHub 创建 issue？"):
            webbrowser.open(ISSUES_URL)
            ok(f"正在打开：{color(ISSUES_URL, COLOR_CYAN)}")

