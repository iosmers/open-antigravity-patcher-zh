import os
import sys
import re
import time
import shutil

from patcher.constants import (
    MIN_AG_VERSION,
)
from patcher.utils.console import (
    info,
    hint,
    ok,
    warn,
    err,
    step,
    print_panel,
)
from patcher.utils.update import handle_patch_failure
from patcher.utils.admin import terminate_processes
from patcher.utils.file import (
    file_hash,
    file_size,
    format_bytes,
    fix_posix_permissions,
    resign_macos_bundle,
    remove_macos_immutable_flags,
    remove_macos_quarantine,
    find_app_bundle,
)
from patcher.ide.discovery import (
    check_ag_version,
    parse_version_safe,
    VersionStatus,
)

IDE_RE = re.compile(r"(resetIsTierGCPTos\(\),)this\.[A-Za-z_$0-9]+\.isGoogleInternal")
IDE_DONE = "resetIsTierGCPTos(),true"


def _ide_cache_dirs():
    """VS Code CachedData / Code Cache dirs to drop after patching main.js, so the IDE
    recompiles the patched bytes instead of replaying a stale compile cache. The user-data
    folder is the product nameLong ('Antigravity IDE') under each OS's app-data root."""
    home = os.path.expanduser("~")
    if os.name == "nt":
        bases = [os.path.expandvars(p) for p in
                 (r"%USERPROFILE%\scoop\persist\antigravity-ide\data\user-data",
                  r"%APPDATA%\Antigravity IDE")]
    elif sys.platform == "darwin":
        bases = [os.path.join(home, "Library", "Application Support", "Antigravity IDE")]
    else:                                                  # Linux (respect XDG_CONFIG_HOME)
        cfg = os.environ.get("XDG_CONFIG_HOME") or os.path.join(home, ".config")
        bases = [os.path.join(cfg, "Antigravity IDE")]
    dirs = []
    for base in bases:
        dirs += [os.path.join(base, "CachedData"),
                 os.path.join(base, "Code Cache", "js")]
    return dirs


def apply_patches(content, ag_version=None):
    """为来自 manager.py 的 IDE 应用 isGoogleInternal 补丁。"""
    results = []
    already = is_already_patched(content)
    matches = [m.group(0) for m in IDE_RE.finditer(content)]
    new_content = IDE_RE.sub(r"\1true", content)
    applied = new_content != content

    if applied:
        detail = f"replaced {len(matches)} occurrences"
    elif already:
        detail = "already patched"
    else:
        detail = "pattern not found"

    results.append({
        "Name": "isGoogleInternal -> true (auth)",
        "Applied": True if (applied or already) else False,
        "Detail": detail,
    })
    return new_content, results


def is_already_patched(content):
    return IDE_DONE in content and not IDE_RE.search(content)


def warn_about_unsafe_backup(main_js_path, installed_version_str=None, current_content=None):
    backup_path = main_js_path + ".bak"
    if not os.path.exists(backup_path):
        return True, False

    backup_size = file_size(backup_path)
    current_size = file_size(main_js_path)
    warnings = []

    if backup_size <= 2048:
        try:
            with open(backup_path, "r", encoding="utf-8") as f:
                backup_content = f.read()
            if len(backup_content.strip()) <= 512:
                warnings.append(
                    f"backup size is only {format_bytes(backup_size)} and it looks almost empty"
                )
        except Exception as e:
            warn(f"备份检查出错：{e}")
            return False, False
    elif backup_size < 4096 or (current_size > 0 and backup_size < current_size // 10):
        warnings.append(
            f"backup is much smaller than expected "
            f"({format_bytes(backup_size)} vs {format_bytes(current_size)})"
        )

    if not warnings:
        return True, False

    for warning in warnings:
        warn(f"备份警告：{warning}")
    warn("还原此备份可能导致 Antigravity IDE 无法正常工作。")
    warn(f"已保留备份：{os.path.basename(backup_path)}")
    return True, True


def do_patch(main_js_path, show_search_line=False):
    from patcher.cli import confirmed
    from patcher.utils.captcha import confirm_with_captcha

    if not main_js_path or not os.path.isfile(main_js_path):
        from patcher.cli import offer_download_and_block
        offer_download_and_block("Antigravity IDE")
        return

    ver_status, ver_str = check_ag_version(main_js_path)
    parsed_version = parse_version_safe(ver_str)

    if ver_status == VersionStatus.TOO_OLD:
        err(f"不支持的版本：{ver_str}")
        err(f"最低要求版本：{MIN_AG_VERSION}")
        hint("请更新 Antigravity IDE 后重试。")
        if not confirmed("仍要继续吗？"):
            return
    elif ver_status == VersionStatus.NOT_FOUND:
        warn("无法检测 Antigravity IDE 版本（未找到注册表项）。")
        if not confirmed("是否跳过版本检查继续？"):
            return
    elif ver_status == VersionStatus.PARSE_ERROR:
        warn(f"无法解析版本号：{ver_str}")
        if not confirmed("仍要继续吗？"):
            return
    # VersionStatus.OK —— 无需询问，直接继续

    try:
        with open(main_js_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        err(f"读取出错：{e}")
        return

    current_is_patched = is_already_patched(content)

    if current_is_patched:
        hint("文件似乎已打过补丁。")
        if not confirm_with_captcha("仍要应用 main.js 补丁吗？"):
            return

    # --- 备份 ---
    backup_path = main_js_path + ".bak"

    if not os.path.exists(backup_path) and not current_is_patched:
        info("正在创建备份……")
        if sys.platform == "darwin":
            app_path = find_app_bundle(main_js_path)
            if app_path:
                remove_macos_immutable_flags(app_path)
                remove_macos_quarantine(app_path)
        try:
            shutil.copy2(main_js_path, backup_path)
            fix_posix_permissions(backup_path)
            ok(f"备份：{os.path.basename(backup_path)} "
               f"({format_bytes(file_size(backup_path))})")
        except PermissionError as e:
            if sys.platform == "darwin":
                warn(f"权限不足，正在移除文件标志后重试……")
                app_path = find_app_bundle(main_js_path)
                if app_path:
                    remove_macos_immutable_flags(app_path)
                    remove_macos_quarantine(app_path)
                try:
                    shutil.copy2(main_js_path, backup_path)
                    fix_posix_permissions(backup_path)
                    ok(f"备份：{os.path.basename(backup_path)} "
                       f"({format_bytes(file_size(backup_path))})")
                except Exception as e2:
                    err(f"备份出错：{e2}")
                    return
            else:
                err(f"备份出错：{e}")
                return
        except Exception as e:
            err(f"备份出错：{e}")
            return
    elif os.path.exists(backup_path):
        hint("备份已存在 —— 跳过")
    elif current_is_patched:
        warn("main.js 已打过补丁 —— 无需备份")

    hash_before = file_hash(main_js_path)

    info("正在应用补丁……")
    print()

    new_content, results = apply_patches(content, ag_version=parsed_version)

    applied = 0
    for r in results:
        if r.get("Applied"):
            applied += 1
        step(r["Name"], r.get("Applied", False), r.get("Detail", ""))
    print()

    if new_content == content and current_is_patched:
        ok("文件已打过补丁 —— 无需改动。")
        return

    if applied == 0:
        err("未应用任何补丁。")
        handle_patch_failure()
        return

    write_success = False
    for attempt in range(2):
        try:
            with open(main_js_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            fix_posix_permissions(main_js_path)
            write_success = True
            break
        except PermissionError as e:
            if attempt == 0:
                if sys.platform == "darwin":
                    warn(f"权限不足，正在移除文件标志后重试……")
                    app_path = find_app_bundle(main_js_path)
                    if app_path:
                        remove_macos_immutable_flags(app_path)
                        remove_macos_quarantine(app_path)
                    time.sleep(0.5)
                    continue
                warn(f"权限不足（文件被占用）：{e}")
                if confirmed("是否自动关闭正在运行的 Antigravity 进程并重试？"):
                    terminate_processes(["Antigravity", "Antigravity IDE", "antigravity", "antigravity-ide"])
                    time.sleep(1.5)
                    continue
            err(f"写入出错（权限不足）：{e}")
            handle_patch_failure()
            return
        except Exception as e:
            err(f"写入出错：{e}")
            handle_patch_failure()
            return

    if not write_success:
        handle_patch_failure()
        return

    # 清理 VS Code 已编译 JS 文件的缓存（CachedData / Code Cache）
    info("正在清理 IDE 编译缓存……")
    for c in _ide_cache_dirs():
        try:
            if os.path.isdir(c):
                shutil.rmtree(c, ignore_errors=True)
        except Exception:
            pass

    hash_after = file_hash(main_js_path)
    resign_macos_bundle(main_js_path)

    panel_rows = [
        ("Target", os.path.basename(main_js_path)),
        ("Patches", f"{applied}/{len(results)} applied"),
    ]
    if os.path.exists(backup_path):
        panel_rows.append(
            ("Backup", f"{os.path.basename(backup_path)} ({format_bytes(file_size(backup_path))})")
        )
    if hash_before and hash_after:
        panel_rows.append(("Before", f"{hash_before[:8]}...{hash_before[56:]}"))
        panel_rows.append(("After", f"{hash_after[:8]}...{hash_after[56:]}"))
    panel_rows.append(("Done", time.strftime('%H:%M:%S')))
    print_panel("PATCH COMPLETE", panel_rows)
    hint("请重启 Antigravity IDE 并登录。")


def do_restore(main_js_path, show_search_line=False):
    from patcher.cli import confirmed

    current_content = None
    try:
        with open(main_js_path, "r", encoding="utf-8") as f:
            current_content = f.read()
    except Exception:
        pass

    backup_ok, backup_has_warnings = warn_about_unsafe_backup(
        main_js_path, current_content=current_content
    )
    if not backup_ok:
        return

    backup_path = main_js_path + ".bak"

    if not os.path.exists(backup_path):
        err(f"未找到备份文件：{backup_path}")
        return
    try:
        with open(backup_path, "r", encoding="utf-8") as f:
            data = f.read()
    except Exception as e:
        err(f"无法读取备份：{e}")
        return

    backup_size = file_size(backup_path)
    if backup_size <= 2048:
        err("备份文件过小 —— 可能已损坏！")
        if not confirmed("仍要还原吗？"):
            hint("已取消还原。")
            return

    if is_already_patched(data):
        warn("备份本身似乎已被打过补丁！")
        if not confirmed("是否还原这个已打补丁的备份？"):
            hint("已取消还原。")
            return

    restore_question = "仍要还原这个备份吗？" if backup_has_warnings else "是否从备份还原？"
    if not confirmed(restore_question):
        hint("已取消还原。")
        return

    hash_before = file_hash(main_js_path)

    tmp_path = main_js_path + ".tmp"
    try:
        if sys.platform == "darwin":
            app_path = find_app_bundle(main_js_path)
            if app_path:
                remove_macos_immutable_flags(app_path)
                remove_macos_quarantine(app_path)
        with open(tmp_path, "w", encoding="utf-8") as f:
            f.write(data)
        os.replace(tmp_path, main_js_path)
        fix_posix_permissions(main_js_path)
    except Exception as e:
        if sys.platform == "darwin":
            warn(f"还原失败，正在移除文件标志后重试……")
            app_path = find_app_bundle(main_js_path)
            if app_path:
                remove_macos_immutable_flags(app_path)
                remove_macos_quarantine(app_path)
            try:
                if not os.path.exists(tmp_path):
                     with open(tmp_path, "w", encoding="utf-8") as f:
                         f.write(data)
                os.replace(tmp_path, main_js_path)
                fix_posix_permissions(main_js_path)
            except Exception as e2:
                err(f"还原出错：{e2}")
                if os.path.exists(tmp_path):
                    try:
                        os.remove(tmp_path)
                    except Exception:
                        pass
                return
        else:
            err(f"还原出错：{e}")
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass
            return

    hash_after = file_hash(main_js_path)
    resign_macos_bundle(main_js_path)

    panel_rows = [("Target", os.path.basename(main_js_path))]
    if hash_before and hash_after and hash_before != hash_after:
        panel_rows.append(("Before", f"{hash_before[:8]}...{hash_before[56:]}"))
        panel_rows.append(("After", f"{hash_after[:8]}...{hash_after[56:]}"))
    panel_rows.append(("Done", time.strftime('%H:%M:%S')))
    print_panel("RESTORE COMPLETE", panel_rows)
