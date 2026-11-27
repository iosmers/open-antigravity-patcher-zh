import os
import sys
import json
import subprocess
import string
from enum import Enum
from packaging.version import Version
from patcher.constants import AG_REGISTRY_SUBKEY, MIN_AG_VERSION
from patcher.utils.file import get_posix_invoking_user_home
from patcher.utils.console import ok


class VersionStatus(Enum):
    OK = "ok"
    TOO_OLD = "too_old"
    NOT_FOUND = "not_found"
    PARSE_ERROR = "parse_error"


def clean_path(raw_path):
    return raw_path.strip().strip('"').strip("'")


def find_portable_candidates(search_type="ide"):
    """在用户目录和其他磁盘中搜索便携版。"""
    roots = []

    # 1. 获取用户主目录
    home = ""
    if sys.platform != "win32":
        home = get_posix_invoking_user_home()
    if not home:
        home = os.path.expanduser("~")

    # 添加用户的常用目录（包含中文、俄语本地化名称及小写形式）
    if home and os.path.isdir(home):
        standard_subs = [
            "Downloads", "下载", "Загрузки", "downloads", "загрузки",
            "Desktop", "桌面", "Рабочий стол", "desktop", "рабочий стол",
            "Documents", "文档", "Документы", "documents", "документы"
        ]
        for sub in standard_subs:
            p = os.path.join(home, sub)
            if os.path.isdir(p):
                roots.append(p)

    # 2. 在 Linux 上通过 xdg-user-dir 让系统提供准确路径
    if sys.platform != "win32" and os.name == "posix":
        sudo_user = os.environ.get("SUDO_USER")
        for folder_type in ["DOWNLOAD", "DESKTOP", "DOCUMENTS"]:
            try:
                cmd = ["xdg-user-dir", folder_type]
                if sudo_user:
                    cmd = ["sudo", "-u", sudo_user, "xdg-user-dir", folder_type]
                res = subprocess.run(cmd, capture_output=True, text=True, check=False, timeout=10)
                if res.returncode == 0:
                    path = res.stdout.strip()
                    if path and os.path.isdir(path):
                        roots.append(path)
            except Exception:
                pass

    # 3. 当前运行目录
    cwd = os.getcwd()
    if cwd and os.path.isdir(cwd):
        roots.append(cwd)

    # 4. Windows 上其他磁盘的根目录
    if os.name == "nt":
        for letter in string.ascii_uppercase:
            if letter == "C":
                continue
            drive = f"{letter}:\\"
            if os.path.exists(drive):
                roots.append(drive)

    # 5. 整个主目录（作为最后的兜底方案）
    if home and os.path.isdir(home):
        roots.append(home)

    # 去除重复项，同时保持优先级顺序
    seen = set()
    unique_roots = []
    for r in roots:
        r_abs = os.path.abspath(r)
        if r_abs not in seen:
            seen.add(r_abs)
            unique_roots.append(r_abs)
    roots = unique_roots

    candidates = []
    visited_dirs = 0
    max_dirs = 1500

    # 排除体积大的/系统目录（预先计算小写名称集合）
    prune_dirs = {
        ".git", "node_modules", "AppData", "Application Data", "Library",
        "System Volume Information", "$RECYCLE.BIN", "Windows", "Program Files",
        "Program Files (x86)", "usr", "var", "sys", "proc", "dev", "dist", "build",
        "__pycache__", ".idea", ".vscode"
    }
    prune_lower = {p.lower() for p in prune_dirs}

    for root in roots:
        if not os.path.isdir(root):
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            visited_dirs += 1
            if visited_dirs > max_dirs:
                return candidates

            # 就地过滤 dirnames
            dirnames[:] = [d for d in dirnames if d.lower() not in prune_lower and not d.startswith('.')]

            # 计算相对于搜索根目录的深度
            try:
                rel = os.path.relpath(dirpath, root)
                if rel == ".":
                    depth = 0
                else:
                    depth = len(rel.replace("\\", "/").split("/"))
            except ValueError:
                depth = 999

            if depth >= 3:
                dirnames[:] = []  # 不再向更深层递归

            # 检查该目录是否符合启发式判定条件
            is_match = "antigravity" in dirpath.lower() or dirpath == root

            if is_match:
                if search_type == "ide":
                    # 查找 Antigravity IDE 的特征
                    for sub in [
                        os.path.join("resources", "app", "out", "main.js"),
                        os.path.join("resources", "app", "main.js"),
                        os.path.join("out", "main.js"),
                        "main.js",
                    ]:
                        if os.path.exists(os.path.join(dirpath, sub)):
                            if dirpath not in candidates:
                                candidates.append(dirpath)
                                label = "Antigravity IDE"
                                try:
                                    ok(f"Found portable {label} at: {dirpath}")
                                except Exception:
                                    print(f"  [+] Found portable {label} at: {dirpath}")
                                break
                elif search_type == "antigravity":
                    # 查找 Antigravity 的特征
                    if os.path.exists(os.path.join(dirpath, "resources", "app.asar")) or \
                       os.path.exists(os.path.join(dirpath, "resources", "app1.asar")):
                        if dirpath not in candidates:
                            candidates.append(dirpath)
                            label = "Antigravity"
                            try:
                                ok(f"Found portable {label} at: {dirpath}")
                            except Exception:
                                print(f"  [+] Found portable {label} at: {dirpath}")

    return candidates


def find_install_root():
    candidates = []

    if sys.platform == "darwin":
        # macOS 上应用是 .app 包，main.js 位于 Contents/Resources/app 内
        mac_candidates = [
            "/Applications/Antigravity IDE.app",
            os.path.expanduser("~/Applications/Antigravity IDE.app"),
            "/Applications/antigravity ide.app",
            os.path.expanduser("~/Applications/antigravity ide.app"),
        ]
        for app in mac_candidates:
            candidates.append(os.path.join(app, "Contents", "Resources", "app"))
    elif os.name == "posix":
        candidates.extend([
            "/usr/share/antigravity-ide",
            "/opt/Antigravity IDE",
            "/opt/antigravity-ide",
            "/opt/antigravity ide",
            "/opt/Antigravity IDE/resources/app/out",
        ])

    if os.name == "nt":
        local_app_data = os.environ.get("LOCALAPPDATA")
        if local_app_data:
            candidates.append(os.path.join(local_app_data, "Programs", "Antigravity IDE"))
        pf = os.environ.get("PROGRAMFILES")
        if pf:
            candidates.append(os.path.join(pf, "Antigravity IDE"))
        pfx86 = os.environ.get("PROGRAMFILES(X86)")
        if pfx86:
            candidates.append(os.path.join(pfx86, "Antigravity IDE"))

        try:
            import winreg
            for hive in (winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE):
                try:
                    with winreg.OpenKey(hive, AG_REGISTRY_SUBKEY) as key:
                        install_loc, _ = winreg.QueryValueEx(key, "InstallLocation")
                        if install_loc and install_loc.strip():
                            candidates.append(install_loc.strip())
                except OSError:
                    pass
        except ImportError:
            pass

    for path in candidates:
        for sub in [
            os.path.join("resources", "app", "out", "main.js"),
            os.path.join("resources", "app", "main.js"),
            os.path.join("out", "main.js"),
            "main.js",
        ]:
            if os.path.exists(os.path.join(path, sub)):
                return path

    # Fallback to portable search only if standard paths did not match
    portable = find_portable_candidates("ide")
    if portable:
        return portable[0]

    return ""


def find_main_js(root):
    # macOS：用户可以直接传入 .app 包的路径
    if sys.platform == "darwin" and root.lower().endswith(".app") and os.path.isdir(root):
        root = os.path.join(root, "Contents", "Resources", "app")

    for sub in [
        os.path.join("resources", "app", "out", "main.js"),
        os.path.join("resources", "app", "main.js"),
        os.path.join("out", "main.js"),
        "main.js",
    ]:
        p = os.path.join(root, sub)
        if os.path.exists(p):
            return p
    return ""


def get_ag_version(main_js_path):
    """从 Windows 注册表、macOS 的 Info.plist 或 Linux 的 package.json 读取 Antigravity IDE 版本。
    返回 (version_str, is_pkg_mgr)。
    """
    # macOS：从 Info.plist 读取版本
    if sys.platform == "darwin":
        # 从 main.js 向上查找 .app 包
        app_path = ""
        p = os.path.dirname(main_js_path)
        while p and p != os.path.dirname(p):
            if p.endswith(".app"):
                app_path = p
                break
            p = os.path.dirname(p)

        if app_path:
            plist_path = os.path.join(app_path, "Contents", "Info.plist")
            if os.path.exists(plist_path):
                try:
                    import plistlib
                    with open(plist_path, "rb") as f:
                        plist = plistlib.load(f)
                    ver = plist.get("CFBundleShortVersionString", "").strip()
                    if not ver:
                        ver = plist.get("CFBundleVersion", "").strip()
                    if ver:
                        return ver, False
                except Exception:
                    pass

        # Fallback: package.json
        for rel in (
            os.path.join(os.path.dirname(main_js_path), "..", "package.json"),
            os.path.join(os.path.dirname(main_js_path), "package.json"),
        ):
            pkg = os.path.normpath(rel)
            if os.path.exists(pkg):
                try:
                    with open(pkg, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    ver = data.get("version", "").strip()
                    if ver:
                        return ver, False
                except Exception:
                    pass
        return None, False

    if os.name == "posix":
        # 尝试使用包管理器（apt、rpm）并匹配不同的包名
        pkg_names = ["antigravity-ide", "antigravity-ide-bin", "antigravity-ide-custom"]

        # dpkg-query (Debian/Ubuntu)
        for pkg in pkg_names:
            try:
                result = subprocess.run(
                    ["dpkg-query", "-W", "-f=${Version}", pkg],
                    capture_output=True, text=True, timeout=10,
                )
                if result.returncode == 0:
                    ver = result.stdout.strip()
                    if ver:
                        return ver, True
            except Exception:
                pass

        # rpm (Fedora/RHEL/openSUSE)
        for pkg in pkg_names:
            try:
                result = subprocess.run(
                    ["rpm", "-q", "--queryformat", "%{VERSION}", pkg],
                    capture_output=True, text=True, timeout=10,
                )
                if result.returncode == 0:
                    ver = result.stdout.strip()
                    if ver:
                        return ver, True
            except Exception:
                pass

        # Fallback: package.json (portable / snap / flatpak)
        for rel in (
            os.path.join(os.path.dirname(main_js_path), "..", "package.json"),
            os.path.join(os.path.dirname(main_js_path), "package.json"),
        ):
            pkg = os.path.normpath(rel)
            if os.path.exists(pkg):
                try:
                    with open(pkg, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    ver = data.get("version", "").strip()
                    if ver:
                        return ver, False
                except Exception:
                    pass
        return None, False

    if os.name == "nt":
        try:
            import winreg
            for hive in (winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE):
                try:
                    with winreg.OpenKey(hive, AG_REGISTRY_SUBKEY) as key:
                        display_ver, _ = winreg.QueryValueEx(key, "DisplayVersion")
                        if display_ver and display_ver.strip():
                            return display_ver.strip(), True
                except OSError:
                    pass
        except ImportError:
            pass

    return None, False


def check_ag_version(main_js_path):
    """
    检查 Antigravity IDE 的版本。
    返回 (VersionStatus, detected_version_str | None)。
    """
    ver_str, is_pkg_mgr = get_ag_version(main_js_path)

    if ver_str is None:
        return VersionStatus.NOT_FOUND, None

    try:
        detected = Version(ver_str)

        # 最低版本要求取决于平台：
        # - macOS：1.107.0（通过 Homebrew/DMG 安装的自定义构建）
        # - 无包管理器的 Linux：1.107.0（自定义构建）
        # - 其他情况：MIN_AG_VERSION（来自 Windows 注册表或包管理器）
        min_ver_str = MIN_AG_VERSION
        if sys.platform == "darwin" and not is_pkg_mgr:
            min_ver_str = "1.107.0"
        elif os.name == "posix" and sys.platform != "darwin" and not is_pkg_mgr:
            min_ver_str = "1.107.0"

        minimum = Version(min_ver_str)
        status = VersionStatus.OK if detected >= minimum else VersionStatus.TOO_OLD
        return status, ver_str
    except Exception:
        return VersionStatus.PARSE_ERROR, ver_str


def parse_version_safe(ver_str):
    if not ver_str:
        return None
    try:
        return Version(ver_str)
    except Exception:
        return None


def resolve_target_path(raw_path):
    if not raw_path:
        return ""
    cleaned = clean_path(raw_path)
    if not cleaned:
        return ""
    expanded = os.path.expandvars(os.path.expanduser(cleaned))
    resolved = os.path.abspath(expanded)
    
    # 如果给出的是目录，则尝试在其中查找 main.js
    if os.path.isdir(resolved):
        found = find_main_js(resolved)
        return found if found else resolved
    return resolved

