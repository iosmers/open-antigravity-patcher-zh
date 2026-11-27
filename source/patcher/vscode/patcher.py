import os
import re
import shutil
import filecmp

from patcher.constants import COLOR_CYAN, COLOR_GREEN, COLOR_YELLOW
from patcher.utils.console import (
    color,
    info,
    hint,
    ok,
    warn,
    err,
    step,
    print_panel,
)
from patcher.utils.file import (
    file_hash,
    file_size,
    format_bytes,
    fix_posix_permissions,
)
from patcher.utils.update import handle_patch_failure

BAK_EXT = ".vscodebak"

# ---------------------------------------------------------------------------
# PART 1 —— extension.js 中的标记与原始代码行
PART1_ANCHOR = "outputChannel.appendLine('[INSTALL] Checking Antigravity releases...');"

# PART 1 使用较宽松的正则：允许不同引号和空格，但要求匹配
# 完整的 appendLine 调用 —— 包括右括号和可选的 ';'。
# 这样可以保证插入点位于调用之后，而不是调用内部。
# 分组 1 是整个调用（插入点 = m.end(1)）。
PART1_ANCHOR_RE = re.compile(
    r"(outputChannel\s*\.\s*appendLine\s*\(\s*"            # outputChannel.appendLine(
    r"(['\"])\[INSTALL\]\s*Checking Antigravity releases[^'\"]*\2"  # '标记字符串'
    r"\s*\)\s*;?)"                                         # ) 或 );
)

# 注入逻辑：如果程序文件已下载（targetPathOverride 或 ~/.gemini/bin），
# 则跳过版本检查和重复下载。
PART1_INJECT = (
    "{const __primary=options.targetPathOverride||getInstalledTargetPath();"
    "const __candidates=[__primary,"
    "(0,path_1.join)((0,path_1.dirname)(__primary),'antigravity'+((0,path_1.extname)(__primary)||''))];"
    "for(const __p of __candidates){if(__p&&await pathExists(__p)){"
    "outputChannel.appendLine('[INSTALL] Existing binary found at '+__p+'. "
    "Skipping version check and re-download.');return __p;}}}"
)

# PART 2 —— 把检测渠道变更的表达式替换为常量 false，
# 这样扩展就不会认为渠道已改变，也不会重新下载程序文件。
# 使用严格的正则：恰好三个标识符（manifestFetched、lastInstalledUrl、
# releaseBaseUrl）且顺序固定 —— 不会误匹配其他形如下面的表达式
# `const X = a && b !== c;`.
PART2_RE = re.compile(
    r"const\s+isChannelChanged\s*=\s*"
    r"manifestFetched\s*&&\s*lastInstalledUrl\s*!==\s*releaseBaseUrl\s*;"
)
PART2_DONE_RE = re.compile(r"const\s+isChannelChanged\s*=\s*false\s*;")
PART2_REPLACEMENT = "const isChannelChanged = false;"


def is_already_patched(content):
    """当两部分补丁都已应用到 extension.js 时返回 True。"""
    return (PART1_INJECT in content) and ("const isChannelChanged = false;" in content)


def _apply_part1(content):
    """返回 (新内容, 状态)。状态取值：'applied'|'already'|'not-found'。"""
    if PART1_INJECT in content:
        return content, "already"
    m = PART1_ANCHOR_RE.search(content)
    if m:
        insert_at = m.end(1)
        new_content = content[:insert_at] + PART1_INJECT + content[insert_at:]
        return new_content, "applied"
    # 兜底方案：按标记做精确查找（应对特殊的代码格式）
    idx = content.find(PART1_ANCHOR)
    if idx == -1:
        return content, "not-found"
    insert_at = idx + len(PART1_ANCHOR)
    new_content = content[:insert_at] + PART1_INJECT + content[insert_at:]
    return new_content, "applied"


def _apply_part2(content):
    """返回 (新内容, 状态)。"""
    if PART2_DONE_RE.search(content):
        # 已打过补丁；但若附近仍存在原始写法 —— 说明那是另一个
        # 实例，将在下面继续处理。
        new_content, n = PART2_RE.subn(PART2_REPLACEMENT, content)
        if n:
            return new_content, "applied"
        return content, "already"
    new_content, n = PART2_RE.subn(PART2_REPLACEMENT, content)
    if not n:
        return content, "not-found"
    return new_content, "applied"


def _make_backup(path):
    bak = path + BAK_EXT
    if os.path.exists(bak):
        if filecmp.cmp(path, bak, shallow=False):
            return
        info(f"备份已过期（扩展已更新） —— 正在刷新 {os.path.basename(path)}{BAK_EXT}")
    else:
        info(f"正在创建备份 -> {os.path.basename(path)}{BAK_EXT}")
    shutil.copy2(path, bak)
    fix_posix_permissions(bak)
    ok(f"备份：{os.path.basename(bak)} ({format_bytes(file_size(bak))})")


def do_patch_vscode(extension_js_path):
    """修补 google.google-antigravity 扩展的 extension.js（PART 1 + PART 2）。"""
    from patcher.cli import confirmed

    if not extension_js_path or not os.path.isfile(extension_js_path):
        err("未找到 Antigravity VS Code 的 extension.js。")
        hint("请在 VS Code 中安装 'Google Antigravity' 扩展并运行一次。")
        return False

    path = extension_js_path
    info(f"目标：{color(path, COLOR_CYAN)}")
    hint(f"大小：{color(format_bytes(file_size(path)), COLOR_CYAN)}")
    print()

    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        err(f"读取出错：{e}")
        handle_patch_failure()
        return False

    already = is_already_patched(content)

    new_content, s1 = _apply_part1(content)
    new_content, s2 = _apply_part2(new_content)

    statuses = [s1, s2]
    if all(s == "not-found" for s in statuses):
        err("在 extension.js 中未找到补丁特征（扩展版本不受支持？）。")
        handle_patch_failure()
        return False

    if all(s in ("already", "not-found") for s in statuses) and already:
        hint("extension.js 已打过补丁（两部分均已修补）。")
        if not confirmed("仍要应用补丁吗？"):
            return True
        # 重新打补丁：若存在备份则基于备份重建，否则直接继续
        bak = path + BAK_EXT
        if os.path.isfile(bak):
            try:
                with open(bak, "r", encoding="utf-8") as f:
                    new_content = f.read()
            except Exception as e:
                warn(f"无法读取用于重新打补丁的备份：{e}")
        new_content, s1 = _apply_part1(new_content)
        new_content, s2 = _apply_part2(new_content)

    changed = new_content != content
    if changed:
        try:
            _make_backup(path)
        except (PermissionError, OSError) as e:
            err(f"备份出错：{e}")
            hint("请关闭 VS Code 窗口后重试。若以 root 安装，请用 sudo 重新运行。")
            handle_patch_failure()
            return False
        try:
            with open(path, "w", encoding="utf-8", newline="") as f:
                f.write(new_content)
        except PermissionError as e:
            err(f"写入出错（文件被占用？）：{e}")
            hint("请关闭 VS Code 窗口后重试。")
            handle_patch_failure()
            return False
        except Exception as e:
            err(f"写入出错：{e}")
            handle_patch_failure()
            return False

    applied_parts = sum(1 for s in statuses if s in ("applied", "already"))
    print()
    step("Patch Antigravity VS Code extension", bool(changed or already),
         f"{applied_parts}/2 part(s)")
    print()
    panel_rows = [
        ("Target", os.path.basename(os.path.dirname(path))),
        ("File", os.path.basename(path)),
        ("Part 1", {"applied": "injected skip-download guard",
                    "already": "already patched",
                    "not-found": "pattern not found"}[s1]),
        ("Part 2", {"applied": "isChannelChanged -> false",
                    "already": "already patched",
                    "not-found": "pattern not found"}[s2]),
    ]
    hash_before = file_hash(path)
    panel_rows.append(("Hash", f"{hash_before[:8]}...{hash_before[56:]}" if hash_before else "n/a"))
    print_panel("PATCH COMPLETE" if (changed or already) else "PATCH SKIPPED", panel_rows)
    if changed:
        hint("请重新加载 VS Code 窗口（开发者：重新加载窗口）使改动生效。")
    return True


def do_restore_vscode(extension_js_path):
    """从 .vscodebak 备份还原 extension.js；如果 ~/.gemini/bin 中的
    程序文件（antigravity/agy）曾通过「Antigravity VS Code 补丁」
    菜单项修补过，也会从其 .agybak 备份一并还原。"""
    from patcher.cli import confirmed

    if not extension_js_path or not os.path.isfile(extension_js_path):
        err("未找到 Antigravity VS Code 的 extension.js。")
        return

    path = extension_js_path
    bak = path + BAK_EXT
    if not os.path.exists(bak):
        warn(f"以下目标没有备份：{os.path.basename(path)}（无需还原）。")
        return

    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        err(f"读取出错：{e}")
        return

    if not is_already_patched(content):
        warn("extension.js 未打补丁 —— 跳过还原（备份可能是其他构建版本）。")
        if not confirmed("仍要从备份还原吗？"):
            hint("已取消还原。")
            return

    if not confirmed("是否从备份还原 Antigravity VS Code 的 extension.js？"):
        hint("已取消还原。")
        return

    hash_before = file_hash(path)
    try:
        shutil.copy2(bak, path)
        fix_posix_permissions(path)
    except PermissionError as e:
        err(f"还原出错（文件被占用？）：{e}")
        hint("请关闭 VS Code 窗口后重试。")
        return
    except Exception as e:
        err(f"还原出错：{e}")
        return

    hash_after = file_hash(path)
    print()
    panel_rows = [("Target", os.path.basename(path))]
    if hash_before and hash_after and hash_before != hash_after:
        panel_rows.append(("Before", f"{hash_before[:8]}...{hash_before[56:]}"))
        panel_rows.append(("After", f"{hash_after[:8]}...{hash_after[56:]}"))
    print_panel("RESTORE COMPLETE", panel_rows)
    hint("请重新加载 VS Code 窗口（开发者：重新加载窗口）使改动生效。")

    # --- 还原 ~/.gemini/bin 中的程序文件（由 agy 补丁器修补） ---
    from patcher.vscode.discovery import find_gemini_antigravity_binary
    from patcher.agy.patcher import do_restore_agy

    gemini_bin = find_gemini_antigravity_binary()
    if gemini_bin and os.path.exists(gemini_bin + ".agybak"):
        print()
        info(f"已找到已打补丁的程序备份：{color(gemini_bin, COLOR_CYAN)}")
        do_restore_agy(gemini_bin)
    elif gemini_bin:
        hint(f"程序 {os.path.basename(gemini_bin)}在 ~/.gemini/bin 中没有备份 —— 无需还原。")
