import os
import sys
import webbrowser
import locale

from patcher.constants import (
    COLOR_CYAN,
    COLOR_GREEN,
    COLOR_YELLOW,
    COLOR_RED,
    COLOR_BOLD,
    COLOR_DIM,
    COLOR_WHITE,
    COLOR_UNDERLINE,
    DOWNLOAD_URL,
    VERSION,
)
from patcher.utils.console import (
    color,
    link,
    clear_screen,
    print_banner,
    print_menu_section,
    print_menu_row,
    print_menu_divider,
    print_menu_footer,
    info,
    hint,
    ok,
    warn,
    err,
    cancel,
    _visible_len,
)

from patcher.utils.file import file_size, format_bytes
from patcher.utils.update import check_for_updates, open_releases_page, print_update_status_notice

from patcher.ide.discovery import (
    find_install_root,
    find_main_js,
    get_ag_version,
    resolve_target_path,
)
from patcher.ide.patcher import is_already_patched, do_patch, do_restore
from patcher.agy.discovery import find_agy_binary, resolve_agy_path
from patcher.agy.patcher import is_already_patched as is_agy_patched, do_patch_agy, do_restore_agy

from patcher.manager.discovery import find_manager_binary, resolve_manager_path, get_antigravity_version
from patcher.manager.patcher import is_already_patched as is_mgr_patched, do_patch_manager, do_restore_manager

from patcher.vscode.discovery import (
    find_extension_js,
    resolve_extension_path,
    find_gemini_antigravity_binary,
    describe_gemini_binary_path,
)
from patcher.vscode.patcher import (
    is_already_patched as is_vscode_patched,
    do_patch_vscode,
    do_restore_vscode,
)


def pause(prompt="  按回车键返回菜单……"):
    print(color(prompt, COLOR_DIM), end="", flush=True)
    if os.name == "nt":
        import msvcrt
        try:
            while msvcrt.kbhit():
                msvcrt.getch()
            while True:
                ch = msvcrt.getch()
                if ch in (b"\r", b"\n"):
                    break
        except Exception:
            input()
    else:
        try:
            import tty
            import termios
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(fd)
                while True:
                    ch = sys.stdin.read(1)
                    if ch in ("\r", "\n"):
                        break
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        except Exception:
            input()
    print()



def print_launch_examples():
    script_name = os.path.basename(sys.argv[0]) or "main.py"
    cmd = script_name if getattr(sys, "frozen", False) else f"python {script_name}"
    windows_example = f'{cmd} "C:\\Path\\To\\Antigravity IDE"'
    macos_example = f'{cmd} "/Applications/Antigravity IDE.app"'
    linux_example = f'{cmd} "/usr/share/antigravity-ide"'

    hint("指定自定义路径的用法示例：")
    print(f"      Windows: {color(windows_example, COLOR_YELLOW)}")
    print(f"      macOS:   {color(macos_example, COLOR_YELLOW)}")
    print(f"      Linux:   {color(linux_example, COLOR_YELLOW)}")


def print_path_examples():
    windows_path = r"C:\Users\Name\AppData\Local\Programs\Antigravity IDE"
    macos_path = "/Applications/Antigravity IDE.app"
    linux_path = "/usr/share/antigravity-ide"

    hint("路径示例：")
    print(f"      Windows: {color(windows_path, COLOR_YELLOW)}")
    print(f"      macOS:   {color(macos_path, COLOR_YELLOW)}")
    print(f"      Linux:   {color(linux_path, COLOR_YELLOW)}")


def _read_console_line(prompt):
    print(prompt, end="", flush=True)

    stdin_buffer = getattr(sys.stdin, "buffer", None)
    if stdin_buffer is None:
        return sys.stdin.readline().rstrip("\r\n")

    raw = stdin_buffer.readline()
    if not raw:
        return ""

    encodings = [
        sys.stdin.encoding,
        locale.getpreferredencoding(False),
        "utf-8",
        "cp1251",
        "latin-1",
    ]
    for encoding in [e for e in encodings if e]:
        try:
            return raw.decode(encoding).rstrip("\r\n")
        except UnicodeDecodeError:
            pass

    return raw.decode("utf-8", errors="replace").rstrip("\r\n")


def prompt_yn(question):
    question = question.rstrip()
    prompt = f"  [?] {question} ({color('y', COLOR_GREEN)}/{color('n', COLOR_RED)}): "
    return _read_console_line(prompt).strip().lower()


def confirmed(question):
    """当用户回答 'y' 时返回 True。"""
    return prompt_yn(question) in ("y", "yes", "\u0434", "\u0434\u0430", "\u662f")


def offer_download_and_block(software_name="Antigravity", target_type=None):
    err(f"未设置 {software_name} 路径，或该软件尚未安装。")
    err("已阻止本次打补丁操作。")
    hint(f"下载地址：{color(DOWNLOAD_URL, COLOR_CYAN)}")
    print()
    print_menu_row("1", "在浏览器中打开下载页面", DOWNLOAD_URL, COLOR_GREEN)
    print_menu_row("2", f"指定已安装的 {software_name} 路径", "手动选择路径", COLOR_CYAN)
    print_menu_row("0", "返回主菜单", "", COLOR_RED)
    print()

    action = input(color("  请选择选项 > ", COLOR_CYAN, COLOR_BOLD)).strip()
    if action == "1":
        webbrowser.open(DOWNLOAD_URL)
        ok(f"正在打开：{color(DOWNLOAD_URL, COLOR_CYAN)}")
        return None
    elif action == "2":
        print()
        hint(f"请输入 {software_name} 的路径。")
        print_path_examples()
        raw = input(color(f"\n  {software_name} 路径 > ", COLOR_CYAN, COLOR_BOLD)).strip()
        if raw:
            if target_type == "ide" or software_name == "Antigravity IDE":
                new_path = resolve_target_path(raw)
                if new_path and os.path.isdir(new_path):
                    new_path = find_main_js(new_path)
                if new_path and os.path.isfile(new_path) and new_path.endswith("main.js"):
                    ok(f"{software_name} 路径已更新！")
                    return new_path
                else:
                    err(f"无法解析有效的 {software_name} 目标（未找到 main.js）。")
            elif target_type == "manager" or software_name == "Antigravity 2.0":
                new_path = resolve_manager_path(raw)
                if new_path and os.path.isfile(new_path):
                    ok(f"{software_name} 路径已更新！")
                    return new_path
                else:
                    err(f"无法解析有效的 {software_name} 目标（未找到 language_server）。")
            elif target_type == "agy" or software_name == "Antigravity CLI":
                new_path = resolve_agy_path(raw)
                if new_path and os.path.isfile(new_path):
                    ok(f"{software_name} 路径已更新！")
                    return new_path
                else:
                    err(f"无法解析有效的 {software_name} 目标。")
            else:
                p = resolve_target_path(raw) or resolve_manager_path(raw) or resolve_agy_path(raw)
                if p and os.path.exists(p):
                    ok("路径已更新！")
                    return p
                else:
                    err("提供的路径无效。")
        return None
    else:
        cancel("已取消。")
        return None


def _kv(label, value_text, value_color):
    """格式化的键/值对，标签列对齐（按显示宽度补齐，兼容中文）。"""
    pad = max(0, 9 - _visible_len(label))
    print(f"      {label}{' ' * pad}{color(value_text, value_color)}")


def print_target_info(main_js_path, manager_path="", agy_path="", vscode_path="", vscode_agy_path="", show_search_line=False):
    if show_search_line:
        info("正在搜索已安装的程序……")

    # 1. Antigravity IDE 信息
    print_menu_section("ANTIGRAVITY IDE")
    _kv("目标:", main_js_path if main_js_path else "未找到", COLOR_CYAN)
    if main_js_path and os.path.exists(main_js_path):
        try:
            with open(main_js_path, "r", encoding="utf-8") as f:
                content = f.read()
            _kv("状态:", "已找到", COLOR_GREEN)
            patched = is_already_patched(content)
            _kv("补丁:", "已打补丁" if patched else "未打补丁",
                COLOR_YELLOW if patched else COLOR_GREEN)
        except Exception:
            _kv("状态:", "无法读取", COLOR_RED)
            _kv("补丁:", "无法读取", COLOR_RED)

        ver_str, _ = get_ag_version(main_js_path)
        _kv("版本:", ver_str if ver_str else "未检测到",
            COLOR_GREEN if ver_str else COLOR_YELLOW)

        size = file_size(main_js_path)
        _kv("大小:", format_bytes(size), COLOR_GREEN if size > 0 else COLOR_YELLOW)
    else:
        _kv("状态:", "未找到", COLOR_RED)

    print()

    # 2. Antigravity 2.0 信息
    print_menu_section("ANTIGRAVITY 2.0")
    _kv("目标:", manager_path if manager_path else "未找到", COLOR_CYAN)
    if manager_path and os.path.isfile(manager_path):
        _kv("状态:", "已找到", COLOR_GREEN)
        patched = is_mgr_patched(manager_path)
        _kv("补丁:", "已打补丁" if patched else "未打补丁",
            COLOR_YELLOW if patched else COLOR_GREEN)
        
        ver_str = get_antigravity_version(manager_path)
        _kv("版本:", ver_str if ver_str else "未检测到",
            COLOR_GREEN if ver_str else COLOR_YELLOW)

        size = file_size(manager_path)
        _kv("大小:", format_bytes(size), COLOR_GREEN if size > 0 else COLOR_YELLOW)
    else:
        _kv("状态:", "未找到", COLOR_YELLOW)

    print()

    # 3. Antigravity CLI 信息
    print_menu_section("ANTIGRAVITY CLI")
    _kv("目标:", agy_path if agy_path else "未找到", COLOR_CYAN)
    if agy_path and os.path.isfile(agy_path):
        _kv("状态:", "已找到", COLOR_GREEN)
        patched = is_agy_patched(agy_path)
        _kv("补丁:", "已打补丁" if patched else "未打补丁",
            COLOR_YELLOW if patched else COLOR_GREEN)
        size = file_size(agy_path)
        _kv("大小:", format_bytes(size), COLOR_GREEN if size > 0 else COLOR_YELLOW)
    else:
        _kv("状态:", "未找到", COLOR_YELLOW)

    print()

    # 4. Antigravity VS Code 扩展信息（extension.js + agy 二进制文件）
    print_menu_section("ANTIGRAVITY VS CODE EXTENSION")
    _kv("目标:", vscode_path if vscode_path else "未找到", COLOR_CYAN)
    if vscode_path and os.path.isfile(vscode_path):
        _kv("状态:", "已找到", COLOR_GREEN)
        try:
            with open(vscode_path, "r", encoding="utf-8") as f:
                content = f.read()
            patched = is_vscode_patched(content)
            _kv("补丁:", "已打补丁" if patched else "未打补丁",
                COLOR_YELLOW if patched else COLOR_GREEN)
        except Exception:
            _kv("补丁:", "无法读取", COLOR_RED)
        size = file_size(vscode_path)
        _kv("大小:", format_bytes(size), COLOR_GREEN if size > 0 else COLOR_YELLOW)
    else:
        _kv("状态:", "未找到", COLOR_YELLOW)

    print()

    _kv("AGY 程序:", vscode_agy_path if vscode_agy_path else "未找到", COLOR_CYAN)
    if vscode_agy_path and os.path.isfile(vscode_agy_path):
        _kv("状态:", "已找到", COLOR_GREEN)
        patched = is_agy_patched(vscode_agy_path)
        _kv("补丁:", "已打补丁" if patched else "未打补丁",
            COLOR_YELLOW if patched else COLOR_GREEN)
        size = file_size(vscode_agy_path)
        _kv("大小:", format_bytes(size), COLOR_GREEN if size > 0 else COLOR_YELLOW)
    else:
        _kv("状态:", "未找到", COLOR_YELLOW)


def show_about():
    clear_screen()
    print_banner()
    print_menu_section("关于 OPEN AG PATCHER")
    print()
    print(f"  {color('Open AG Patcher', COLOR_BOLD, COLOR_CYAN)} v{VERSION}")
    print("  面向 Antigravity 系列产品的开源区域限制解除工具：")
    print("  Antigravity IDE、Antigravity 2.0（language_server）以及 Antigravity CLI（agy）。")
    print("  无需 VPN，也无需更改 Google 账号区域即可使用 Antigravity。")
    print()
    hint("功能特性：")
    print(f"   • {color('Antigravity IDE 补丁', COLOR_GREEN)} —— 绕过 main.js 中的 isGoogleInternal 判断")
    print(f"   • {color('Antigravity 2.0 补丁', COLOR_GREEN)} —— 修补 language_server 二进制文件")
    print(f"   • {color('Antigravity CLI 补丁', COLOR_GREEN)} —— 绕过 agy 的资格校验")
    print(f"   • {color('备份与还原', COLOR_GREEN)}        —— 安全且完全可逆的修改")
    print()
    hint("作者与社区：")
    tg_main = link("https://t.me/avencoresyt", "t.me/avencoresyt", COLOR_CYAN, COLOR_UNDERLINE)
    tg_chat = link("https://t.me/avencoreschat", "t.me/avencoreschat", COLOR_CYAN, COLOR_UNDERLINE)
    yt = link("https://youtube.com/@avencores", "youtube.com/@avencores", COLOR_CYAN, COLOR_UNDERLINE)
    vk = link("https://vk.ru/avencoresreuploads", "vk.ru/avencoresreuploads", COLOR_CYAN, COLOR_UNDERLINE)
    dz = link("https://dzen.ru/avencores", "dzen.ru/avencores", COLOR_CYAN, COLOR_UNDERLINE)
    card_num = link("data:text/plain;charset=utf-8,2202%202050%201464%204675", "2202 2050 1464 4675", COLOR_BOLD, COLOR_WHITE, COLOR_UNDERLINE)
    attr_link = link("https://github.com/QNIX-Dev/eligibility-antigravity-patcher", "eligibility-antigravity-patcher", COLOR_CYAN, COLOR_UNDERLINE)

    print(f"   • 作者:     {color('AvenCores', COLOR_YELLOW)}")
    print(f"   • Telegram: {tg_main} （交流群: {tg_chat}）")
    print(f"   • YouTube:  {yt}")
    print(f"   • VK:       {vk}")
    print(f"   • Dzen:     {dz}")
    print()
    hint("支持作者：")
    print(f"   • {color('SBER:', COLOR_GREEN)} {card_num}")
    print()
    hint("开源许可：")
    print(f"   • GPL-3.0 许可证（署名：{attr_link} / MIT）")



def redraw_main_screen(main_js_path, manager_path="", agy_path="", vscode_path="", vscode_agy_path="", show_search_line=False):

    clear_screen()
    print_banner()
    print_target_info(main_js_path, manager_path, agy_path, vscode_path=vscode_path,
                      vscode_agy_path=vscode_agy_path, show_search_line=show_search_line)
    print()
    print_update_status_notice()


def set_vscode_path(new_path):
    """do_patch_vscode_flow 的回调 —— 通过 sys._getframe 更新
    run_cli 栈帧中的局部变量 vscode_path。"""
    frame = sys._getframe(2)
    if frame.f_code.co_name == "run_cli":
        frame.f_locals["vscode_path"] = new_path


def set_vscode_agy_path(new_path):
    """do_patch_vscode_flow 的回调 —— 通过 sys._getframe 更新
    run_cli 栈帧中的局部变量 vscode_agy_path。"""
    frame = sys._getframe(2)
    if frame.f_code.co_name == "run_cli":
        frame.f_locals["vscode_agy_path"] = new_path


def do_patch_vscode_flow(vscode_path, vscode_agy_path, set_js_cb=None, set_agy_cb=None):
    """通过 agy 补丁器修补 google.google-antigravity 扩展（extension.js）
    以及 ~/.gemini/bin/antigravity（agy）二进制文件。

    只有同时找到 extension.js 和 agy 二进制文件时才会执行补丁。"""
    from patcher.agy.patcher import do_patch_agy

    # --- 0. 预检查：两个文件都必须存在 ---
    if not vscode_path or not os.path.isfile(vscode_path):
        vscode_path = find_extension_js()
        if vscode_path and set_js_cb:
            set_js_cb(vscode_path)

    if not vscode_agy_path or not os.path.isfile(vscode_agy_path):
        vscode_agy_path = find_gemini_antigravity_binary()
        if vscode_agy_path and set_agy_cb:
            set_agy_cb(vscode_agy_path)

    missing = []
    if not vscode_path or not os.path.isfile(vscode_path):
        missing.append("extension.js (VS Code extension 'google.google-antigravity')")
    if not vscode_agy_path or not os.path.isfile(vscode_agy_path):
        missing.append(f"agy binary ({describe_gemini_binary_path()})")

    if missing:
        err("Antigravity VS Code 补丁已阻止 —— 未找到必需的文件：")
        for m in missing:
            err(f"  - {m}")
        hint("请先在 VS Code 中安装 'Google Antigravity' 扩展")
        hint("（扩展面板 -> 搜索 'Antigravity' -> 安装），")
        hint("并运行一次 —— 它会自动把二进制文件下载到 ~/.gemini/bin。")
        return False

    # --- 1. 修补 extension.js ---
    do_patch_vscode(vscode_path)

    # --- 2. 用 agy 补丁器修补 ~/.gemini/bin/antigravity 二进制文件 ---
    print()
    info(f"已找到下载的二进制文件：{color(vscode_agy_path, COLOR_CYAN)}")
    do_patch_agy(vscode_agy_path)
    return True


def run_cli():
    main_js_path = ""
    manager_path = ""
    agy_path = ""
    vscode_path = ""
    vscode_agy_path = ""
    searched = False

    # 1. 检查命令行参数
    if len(sys.argv) > 1:
        args = [a for a in sys.argv[1:] if a not in ("--rollback", "-r")]
        if args:
            arg = " ".join(args)
            # 尝试识别目标类型
            ide_path = resolve_target_path(arg)
            if ide_path and os.path.isdir(ide_path):
                ide_path = find_main_js(ide_path)
            
            if ide_path and os.path.isfile(ide_path) and ide_path.endswith("main.js"):
                main_js_path = ide_path
            else:
                # 尝试作为 Antigravity 2.0（Manager / language_server）处理
                mgr_path = resolve_manager_path(arg)
                if mgr_path and os.path.isfile(mgr_path):
                    manager_path = mgr_path
                else:
                    # 尝试作为 CLI（agy）处理
                    agy_p = resolve_agy_path(arg)
                    if agy_p and os.path.isfile(agy_p):
                        agy_path = agy_p
                    else:
                        err(f"提供的路径不存在或无效：{arg}")

    # 2. 检查当前目录（针对 Antigravity IDE）
    if not main_js_path and not manager_path and not agy_path:
        local = os.path.join(os.getcwd(), "main.js")
        if os.path.exists(local):
            main_js_path = local
            info("在当前目录中找到了 main.js")

    # 3. 在系统中自动搜索
    if not main_js_path and not manager_path and not agy_path:
        info("Searching for installations...")
        searched = True

        ide_root = find_install_root()
        if ide_root:
            main_js_path = find_main_js(ide_root)

        manager_path = find_manager_binary()
        agy_path = find_agy_binary()

    # VS Code 扩展及其 agy 二进制文件始终会被搜索 —— 无论其他目标
    # 是否已找到（它是拥有独立目录的单独产品）。
    if not vscode_path or not vscode_agy_path:
        if not searched:
            info("Searching for installations...")
        if not vscode_path:
            vscode_path = find_extension_js()
        if not vscode_agy_path:
            vscode_agy_path = find_gemini_antigravity_binary()

    # 如果完全没有找到任何目标，则让用户在打开下载页面和手动输入路径之间选择
    if not main_js_path and not manager_path and not agy_path:
        warn("未能自动找到任何已安装的程序。")
        hint(f"Download URL: {color(DOWNLOAD_URL, COLOR_CYAN)}")
        print()
        print_menu_row("1", "Open download page in browser", DOWNLOAD_URL, COLOR_GREEN)
        print_menu_row("2", "指定已安装软件的路径", "手动选择路径", COLOR_CYAN)
        print_menu_row("0", "暂时跳过（进入主菜单）", "", COLOR_YELLOW)
        print()

        act = input(color("  请选择选项 > ", COLOR_CYAN, COLOR_BOLD)).strip()
        if act == "1":
            webbrowser.open(DOWNLOAD_URL)
            ok(f"正在打开：{color(DOWNLOAD_URL, COLOR_CYAN)}")
            print()
        elif act == "2":
            print()
            hint("请指定 Antigravity IDE、Antigravity 2.0 或 agy 的路径。")
            print_path_examples()
            raw = input(color("\n  路径 > ", COLOR_CYAN, COLOR_BOLD)).strip()
            if raw:
                ide_path = resolve_target_path(raw)
                if ide_path and os.path.isdir(ide_path):
                    ide_path = find_main_js(ide_path)
                
                if ide_path and os.path.isfile(ide_path) and ide_path.endswith("main.js"):
                    main_js_path = ide_path
                else:
                    mgr_path = resolve_manager_path(raw)
                    if mgr_path and os.path.isfile(mgr_path):
                        manager_path = mgr_path
                    else:
                        agy_p = resolve_agy_path(raw)
                        if agy_p and os.path.isfile(agy_p):
                            agy_path = agy_p

    # 启动时自动检查更新
    check_for_updates(silent=True)

    redraw_main_screen(main_js_path, manager_path, agy_path, vscode_path=vscode_path,
                       vscode_agy_path=vscode_agy_path, show_search_line=searched)

    while True:
        print_menu_section("打补丁")
        print_menu_row("1", "Antigravity IDE 补丁", "绕过区域限制（isGoogleInternal）", COLOR_GREEN)
        print_menu_row("2", "Antigravity 2.0 补丁", "修补 language_server 程序", COLOR_GREEN)
        print_menu_row("3", "Antigravity CLI（agy）补丁", "解锁 agy 工具", COLOR_GREEN)
        print_menu_row("4", "Antigravity VS Code 补丁", "修补扩展 JS 与 agy 程序", COLOR_GREEN)

        print_menu_section("还原")
        print_menu_row("5", "Antigravity IDE", "从备份还原", COLOR_YELLOW)
        print_menu_row("6", "Antigravity 2.0", "从备份还原", COLOR_YELLOW)
        print_menu_row("7", "Antigravity CLI", "从备份还原", COLOR_YELLOW)
        print_menu_row("8", "Antigravity VS Code 扩展", "从备份还原", COLOR_YELLOW)

        print_menu_section("工具")
        print_menu_row("9", "检查更新", "查看 GitHub 发布页", COLOR_CYAN)
        print_menu_row("10", "打开 GitHub 仓库", "源码与更新", COLOR_CYAN)
        print_menu_row("11", "选择自定义路径", "覆盖自动检测的目标", COLOR_CYAN)
        print_menu_row("12", "关于本程序", "信息与作者链接", COLOR_CYAN)

        print()
        print_menu_row("0", "退出", "退出补丁工具", COLOR_RED)
        print_menu_footer("提示：补丁可逆 —— 随时可使用「还原」功能。")

        choice = input(color("\n  请选择选项 > ", COLOR_CYAN, COLOR_BOLD)).strip()
        print()

        if choice == "0":
            return

        # 输入为空 —— 不退出，只是重绘菜单
        if choice == "":
            redraw_main_screen(main_js_path, manager_path, agy_path, vscode_path,
                               vscode_agy_path, show_search_line=searched)
            continue

        valid_choices = {str(i) for i in range(1, 13)}
        if choice not in valid_choices:
            err("无效的选项")
            print()
            pause()
            redraw_main_screen(main_js_path, manager_path, agy_path, vscode_path,
                               vscode_agy_path, show_search_line=searched)
            continue

        handled = True
        clear_screen()
        print_banner()

        if choice == "1":
            if main_js_path and os.path.isfile(main_js_path):
                do_patch(main_js_path, show_search_line=searched)
            else:
                new_p = offer_download_and_block("Antigravity IDE", target_type="ide")
                if new_p:
                    main_js_path = new_p
                    searched = False
                    do_patch(main_js_path, show_search_line=searched)
        elif choice == "2":
            if manager_path and os.path.isfile(manager_path):
                do_patch_manager(manager_path)
            else:
                new_p = offer_download_and_block("Antigravity 2.0", target_type="manager")
                if new_p:
                    manager_path = new_p
                    searched = False
                    do_patch_manager(manager_path)
        elif choice == "3":
            if agy_path and os.path.isfile(agy_path):
                do_patch_agy(agy_path)
            else:
                new_p = offer_download_and_block("Antigravity CLI", target_type="agy")
                if new_p:
                    agy_path = new_p
                    searched = False
                    do_patch_agy(agy_path)
        elif choice == "4":
            do_patch_vscode_flow(vscode_path, vscode_agy_path,
                                 set_js_cb=set_vscode_path, set_agy_cb=set_vscode_agy_path)
        elif choice == "5":
            if main_js_path:
                do_restore(main_js_path, show_search_line=searched)
            else:
                err("未设置 Antigravity IDE 路径，请先使用「选择自定义路径」（选项 11）。")
        elif choice == "6":
            if manager_path:
                do_restore_manager(manager_path)
            else:
                err("未设置 Antigravity 2.0（language_server）路径，请先使用「选择自定义路径」（选项 11）。")
        elif choice == "7":
            if agy_path:
                do_restore_agy(agy_path)
            else:
                err("未设置 Antigravity CLI 路径，请先使用「选择自定义路径」（选项 11）。")
        elif choice == "8":
            if vscode_path:
                do_restore_vscode(vscode_path)
            else:
                err("未设置 Antigravity VS Code 扩展路径，请先使用「选择自定义路径」（选项 11）。")
        elif choice == "9":
            check_for_updates(silent=False)
        elif choice == "10":
            print_target_info(main_js_path, manager_path, agy_path, vscode_path=vscode_path,
                              vscode_agy_path=vscode_agy_path, show_search_line=searched)
            print()
            if confirmed("是否在浏览器中打开 GitHub 仓库？"):
                url = "https://github.com/AvenCores/open-antigravity-unlock"
                webbrowser.open(url)
                ok(f"正在打开：{color(url, COLOR_CYAN)}")
            else:
                cancel("Cancelled.")
        elif choice == "11":
            while True:
                redraw_main_screen(main_js_path, manager_path, agy_path, vscode_path,
                                   vscode_agy_path, show_search_line=searched)
                print_menu_section("选择自定义路径")
                print_menu_row("1", "Antigravity IDE 路径", "文件夹或 main.js", COLOR_GREEN)
                print_menu_row("2", "Antigravity 2.0 路径", "文件夹或 language_server 程序", COLOR_GREEN)
                print_menu_row("3", "Antigravity CLI 路径", "agy.exe 或文件夹", COLOR_GREEN)
                print_menu_row("4", "VS Code 扩展路径（JS）", "extension.js 或扩展目录", COLOR_GREEN)
                print_menu_row("5", "VS Code 程序路径（agy）", "~/.gemini/bin 下的 agy 程序", COLOR_GREEN)
                print()
                print_menu_row("0", "返回", "回到主菜单", COLOR_RED)
                print_menu_footer("其他目标的自动检测结果将保持不变。")

                sub_choice = input(color("\n  请选择选项 > ", COLOR_CYAN, COLOR_BOLD)).strip()
                if sub_choice == "0":
                    handled = False
                    break

                if sub_choice == "1":
                     print()
                     hint("请输入 Antigravity IDE 文件夹或 main.js 文件的路径。")
                     print_path_examples()
                     raw = input(color("\n  IDE 路径 > ", COLOR_CYAN, COLOR_BOLD)).strip()
                     if raw:
                         new_path = resolve_target_path(raw)
                         if new_path and os.path.exists(new_path):
                             if os.path.isdir(new_path):
                                 new_path = find_main_js(new_path)
                             if new_path and os.path.isfile(new_path):
                                 main_js_path = new_path
                                 searched = False
                                 ok("Antigravity IDE 路径已更新！")
                             else:
                                 err("无法解析有效的 Antigravity IDE 目标（未找到 main.js）。")
                         else:
                             err("路径不存在。")
                     print()
                     pause()
                elif sub_choice == "2":
                     print()
                     hint("请输入 Antigravity 2.0 应用目录或 language_server 程序的路径。")
                     print_path_examples()
                     raw = input(color("\n  Antigravity 2.0 路径 > ", COLOR_CYAN, COLOR_BOLD)).strip()
                     if raw:
                         new_path = resolve_manager_path(raw)
                         if new_path and os.path.isfile(new_path):
                             manager_path = new_path
                             searched = False
                             ok("Antigravity 2.0 路径已更新！")
                         else:
                             err("无法解析有效的 Antigravity 2.0 目标（未找到 language_server）。")
                     print()
                     pause()
                elif sub_choice == "3":
                     print()
                     hint("请输入 agy 程序（agy.exe）或其所在文件夹的路径。")
                     print_path_examples()
                     raw = input(color("\n  AGY 路径 > ", COLOR_CYAN, COLOR_BOLD)).strip()
                     if raw:
                         new_path = resolve_agy_path(raw)
                         if new_path and os.path.isfile(new_path):
                             agy_path = new_path
                             searched = False
                             ok("Antigravity CLI 路径已更新！")
                         else:
                             err("无法解析有效的 Antigravity CLI 目标。")
                     print()
                     pause()
                elif sub_choice == "4":
                     print()
                     hint("请输入 extension.js、google.google-antigravity-* 扩展目录，")
                     hint("或 .vscode/extensions 根目录的路径。")
                     raw = input(color("\n  VS Code 扩展路径（JS） > ", COLOR_CYAN, COLOR_BOLD)).strip()
                     if raw:
                         new_path = resolve_extension_path(raw)
                         if new_path and os.path.isfile(new_path):
                             vscode_path = new_path
                             searched = False
                             ok("Antigravity VS Code 扩展路径已更新！")
                         else:
                             err("无法解析有效的 VS Code 扩展目标（未找到 extension.js）。")
                     print()
                     pause()
                elif sub_choice == "5":
                     print()
                     hint(f"请输入由扩展下载的 agy/antigravity 程序的路径")
                     hint(f"（{describe_gemini_binary_path()}），或任意 agy 文件。")
                     raw = input(color("\n  VS Code 程序路径（agy） > ", COLOR_CYAN, COLOR_BOLD)).strip()
                     if raw:
                         new_path = resolve_agy_path(raw)
                         if new_path and os.path.isfile(new_path):
                             vscode_agy_path = new_path
                             searched = False
                             ok("VS Code agy 程序路径已更新！")
                         else:
                             err("无法解析有效的 VS Code agy 程序目标。")
                     print()
                     pause()
            handled = True
        elif choice == "12":
            show_about()

        print()

        if handled:
            pause()
        redraw_main_screen(main_js_path, manager_path, agy_path, vscode_path,
                           vscode_agy_path, show_search_line=searched)
