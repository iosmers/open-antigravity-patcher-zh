import os
import sys
import ctypes
import re
import unicodedata
from patcher.constants import (
    VERSION, COLOR_RESET, COLOR_CYAN, COLOR_GREEN, COLOR_YELLOW, COLOR_RED,
    COLOR_BOLD, COLOR_DIM, COLOR_GRAY, COLOR_WHITE, COLOR_UNDERLINE,
)

USE_COLOR = False


def enable_ansi():
    if os.name != "nt":
        return True
    try:
        kernel32 = ctypes.windll.kernel32
        handle = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
        mode = ctypes.c_uint32()
        if not kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
            return False
        new_mode = mode.value | 0x0004  # ENABLE_VIRTUAL_TERMINAL_PROCESSING
        if new_mode == mode.value:
            return True
        return bool(kernel32.SetConsoleMode(handle, new_mode))
    except Exception:
        return False


def setup_console():
    global USE_COLOR
    if os.name == "nt":
        os.system("chcp 65001 >nul")
        if hasattr(sys.stdout, "reconfigure"):
            try:
                sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass
        if hasattr(sys.stderr, "reconfigure"):
            try:
                sys.stderr.reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass
    USE_COLOR = enable_ansi()


def color(text, *styles):
    if not USE_COLOR or not styles:
        return text
    return "".join(styles) + text + COLOR_RESET


def link(url, text=None, *styles):
    """将文本格式化为 ANSI OSC 8 终端超链接，可附加样式。"""
    if text is None:
        text = url
    styled_text = color(text, *styles) if styles else text
    if not USE_COLOR:
        return text
    return f"\x1b]8;;{url}\x1b\\{styled_text}\x1b]8;;\x1b\\"


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


# 横幅、菜单分隔线和结果面板共用的布局常量。
# BANNER_INNER_WIDTH 是边框内部的可见宽度。
# MENU_WIDTH 是与之匹配的菜单外部宽度（含边框列）。
BANNER_INNER_WIDTH = 47
MENU_WIDTH = BANNER_INNER_WIDTH + 2


def _char_width(ch):
    """返回单个字符在终端中占用的列数（中日韩全角字符占 2 列）。"""
    if unicodedata.combining(ch):
        return 0
    return 2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1


def _visible_len(text):
    """返回去除 ANSI 转义序列（颜色/超链接）后的文本显示宽度。

    中文等全角字符按 2 列计算，否则带中文的菜单和边框会错位。
    """
    clean = text
    if "\x1b" in clean:
        clean = re.sub(r'\x1b\]8;;.*?(?:\x1b\\|\x07)', '', clean)
        clean = re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', clean)
    return sum(_char_width(ch) for ch in clean)




# 横幅与操作结果面板共用的边框绘制辅助函数。
def _frame_border(left_ch, fill_ch, right_ch, accent=COLOR_CYAN):
    """构建一条水平边框线。"""
    return color(left_ch + fill_ch * BANNER_INNER_WIDTH + right_ch, accent, COLOR_BOLD)


def _frame_row(left, right="", accent=COLOR_CYAN):
    """构建一行边框内容：左侧文本 + 可选的右对齐文本。"""
    left_str = "  " + left
    fill = BANNER_INNER_WIDTH - _visible_len(left_str) - _visible_len(right) - 1
    if fill < 1:
        fill = 1
    body = left_str + (" " * fill) + right + " "
    # 修正到精确的可见宽度，避免 ANSI 转义序列导致填充偏差。
    vis = _visible_len(body)
    if vis < BANNER_INNER_WIDTH:
        body = left_str + (" " * (fill + BANNER_INNER_WIDTH - vis)) + right + " "
    elif vis > BANNER_INNER_WIDTH:
        while _visible_len(body) > BANNER_INNER_WIDTH:
            body = body[:-1]
    return color("║", accent, COLOR_BOLD) + body + color("║", accent, COLOR_BOLD)


def print_banner():
    title_left = color("Open AG Patcher", COLOR_BOLD)
    title_right = color(f"v{VERSION}", COLOR_GREEN, COLOR_BOLD)

    label_col = 12  # 标签列（Telegram/YouTube）宽度，用于对齐网格
    telegram = color("Telegram".ljust(label_col), COLOR_YELLOW) + link("https://t.me/avencoresyt", "t.me/avencoresyt", COLOR_DIM, COLOR_UNDERLINE)
    youtube = color("YouTube".ljust(label_col), COLOR_YELLOW) + link("https://youtube.com/@avencores", "youtube.com/@avencores", COLOR_DIM, COLOR_UNDERLINE)


    print()
    print(f"  {_frame_border('╔', '═', '╗')}")
    print(f"  {_frame_row(title_left, title_right)}")
    print(f"  {_frame_row(color('Antigravity 区域限制解除工具', COLOR_CYAN))}")
    print(f"  {_frame_row(color('纯净 • 无密钥 • 无遥测', COLOR_GREEN))}")
    print(f"  {_frame_border('╟', '─', '╢')}")
    print(f"  {_frame_row(telegram)}")
    print(f"  {_frame_row(youtube)}")
    print(f"  {_frame_border('╚', '═', '╝')}")

    print()


def print_panel(title, rows, accent=COLOR_GREEN):
    """渲染一个紧凑的带边框面板，用于展示操作结果摘要。"""
    print()
    try:
        print(f"  {_frame_border('╔', '═', '╗', accent)}")
        print(f"  {_frame_row(color(title, COLOR_BOLD), accent=accent)}")
        print(f"  {_frame_border('╟', '─', '╢', accent)}")
        for label, value in rows:
            val_str = str(value)
            if "\x1b[" not in val_str:
                val_str = color(val_str, COLOR_CYAN)
            label_text = color(f"{label}:", COLOR_WHITE)
            print(f"  {_frame_row(label_text, val_str, accent=accent)}")
        print(f"  {_frame_border('╚', '═', '╝', accent)}")
    except UnicodeEncodeError:
        print(f"--- {title} ---")
        for label, value in rows:
            print(f"  {label}: {value}")
        print("-" * (len(title) + 8))
    print()


# 所有操作输出共用的标记辅助函数。
def info(msg):
    """中性的进度/状态行。"""
    print(f"  [*] {msg}")


def hint(msg):
    """暗色提示行。"""
    print(color(f"  [i] {msg}", COLOR_DIM))


def ok(msg):
    """绿色成功行。"""
    print(color(f"  [+] {msg}", COLOR_GREEN, COLOR_BOLD))


def warn(msg):
    """黄色警告行。"""
    print(color(f"  [!] {msg}", COLOR_YELLOW))


def err(msg):
    """红色错误行。"""
    print(color(f"  [!] {msg}", COLOR_RED))


def cancel(msg):
    """暗色取消行。"""
    print(color(f"  [x] {msg}", COLOR_DIM))


def step(name, applied, detail=""):
    """清单行：绿色对勾、红色叉号，跳过的步骤使用暗色中性标记。"""
    if applied is None:
        marker = color("•", COLOR_DIM)
    else:
        marker = color("✓", COLOR_GREEN) if applied else color("✗", COLOR_RED)
    line = f"  {marker} {name}"
    if detail:
        line += color(f" — {detail}", COLOR_DIM)
    try:
        print(line)
    except UnicodeEncodeError:
        safe_marker = "[*]" if applied is None else ("[+]" if applied else "[x]")
        safe_line = f"  {safe_marker} {name}"
        if detail:
            safe_line += f" - {detail}"
        print(safe_line)


def _center_line(text, width=MENU_WIDTH):
    """在字符串右侧补空格，直到达到菜单面板的完整宽度。"""
    visible = _visible_len(text)
    if visible >= width:
        return text
    return text + " " * (width - visible)


# ─── 菜单界面辅助函数 ─────────────────────────────────────────────────────────
def print_menu_section(title):
    """菜单分区标题，用细线包围。

    示例:  ── 打补丁 ────────────────────────────────
    整行宽度（含开头的 ─）等于 MENU_WIDTH，
    以便右边缘与分隔线和横幅边框对齐。
    """
    label = f" {title} "
    visible = _visible_len(label)
    dashes = "─" * max(1, MENU_WIDTH - visible - 1)  # -1 留给开头的「─」
    line = color("─", COLOR_GRAY) + color(label, COLOR_CYAN, COLOR_BOLD) + color(dashes, COLOR_GRAY)
    print(f"  {line}")


def print_menu_row(number, label, hint="", accent=COLOR_GREEN):
    """菜单条目行。

    格式:    [1]  应用 Antigravity IDE 补丁      应用 / 启用绕过
    number —— 编号字符串（提示性分隔行可以留空）。
    hint —— 右侧的简短说明，使用暗色绘制。
    accent —— 编号标签的颜色。
    """
    num_part = color(f"[{number}]", accent, COLOR_BOLD) if number != "" else color("  ", COLOR_GRAY)
    label_part = color(label, COLOR_WHITE)
    left = f"  {num_part}  {label_part}"
    if not hint:
        print(left)
        return

    left_visible = _visible_len(left)
    gap = max(2, MENU_WIDTH + 2 - left_visible - _visible_len(hint))
    print(f"{left}{' ' * gap}{color(hint, COLOR_DIM)}")


def print_menu_divider():
    """细的水平分隔线。"""
    print(f"  {color('─' * MENU_WIDTH, COLOR_GRAY)}")


def print_menu_footer(note=""):
    """条目列表下方的页脚：暗色线条和备注。"""
    print(f"  {color('─' * MENU_WIDTH, COLOR_GRAY)}")
    if note:
        print(f"  {color(note, COLOR_DIM)}")
