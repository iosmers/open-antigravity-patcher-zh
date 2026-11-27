import os
import hashlib
import time
import shutil
import subprocess

try:
    import pwd
except ImportError:
    pwd = None


def file_hash(path):
    """返回文件的 SHA-256 值，出错时返回 None。"""
    try:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(1024 * 1024), b""):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return None


def file_size(path):
    try:
        return os.path.getsize(path)
    except Exception:
        return 0


def format_bytes(size_bytes):
    if size_bytes >= 1024 * 1024:
        return f"{size_bytes / 1024 / 1024:.1f} MB"
    if size_bytes >= 1024:
        return f"{size_bytes / 1024:.1f} KB"
    return f"{size_bytes} B"


def fix_posix_permissions(path):
    """在 POSIX 上通过 sudo 运行时，确保路径及其内容归属于调用者用户。"""
    if os.name != "posix" or os.getuid() != 0:
        return

    sudo_uid = os.environ.get("SUDO_UID")
    sudo_gid = os.environ.get("SUDO_GID")

    if sudo_uid and sudo_gid:
        try:
            subprocess.run(["chown", "-R", f"{sudo_uid}:{sudo_gid}", path], check=False, timeout=30)
        except Exception:
            pass


def get_posix_invoking_user_home():
    """返回 POSIX 下调用者用户的主目录，即使通过 sudo 运行也能正确获取。"""
    if os.name != "posix":
        return ""

    if pwd is not None:
        sudo_uid = os.environ.get("SUDO_UID")
        if sudo_uid:
            try:
                return pwd.getpwuid(int(sudo_uid)).pw_dir
            except Exception:
                pass

        sudo_user = os.environ.get("SUDO_USER")
        if sudo_user:
            try:
                return pwd.getpwnam(sudo_user).pw_dir
            except Exception:
                pass

    home = os.environ.get("HOME")
    if home:
        return home

    return os.path.expanduser("~")


def backup_json_file(path):
    if not os.path.exists(path):
        return ""

    base = f"{path}.bak-{time.strftime('%Y%m%d-%H%M%S')}"
    backup_path = base
    counter = 1
    while os.path.exists(backup_path):
        counter += 1
        backup_path = f"{base}-{counter}"

    shutil.copy2(path, backup_path)
    fix_posix_permissions(backup_path)
    return backup_path


def find_app_bundle(path):
    """从 path 向上查找第一个以 .app 结尾的目录。

    仅在 macOS 上使用，用于确定 .app 包的根目录，
    以便在修改 main.js 后重新签名。
    """
    p = os.path.abspath(path)
    while p and p != os.path.dirname(p):
        if p.endswith(".app"):
            return p
        p = os.path.dirname(p)
    return ""


def remove_macos_immutable_flags(path):
    """在 macOS 上移除文件或目录的 uchg/schg 标志。

    macOS 上 .app 包内的文件可能带有 immutable 标志，
    即使是 root 也无法写入（在包内执行 shutil.copy2 / 创建备份时
    会出现 Errno 1 Operation not permitted）。
    在尝试写入 .app 包之前调用本函数。

    如果 chflags 执行成功（或平台不是 darwin），返回 True。
    """
    import sys
    if sys.platform != "darwin":
        return True
    ok_flag = False
    # -R 对单个文件和目录都有效。
    # 先尝试 nouchg,noschg 组合，然后分别尝试
    # （没有恢复模式时 noschg 可能无法移除，这是正常现象）。
    # 使用绝对路径 /usr/bin/chflags：在 frozen 构建中 PATH 可能为空。
    for args in (
        ["/usr/bin/chflags", "-R", "nouchg,noschg", path],
        ["/usr/bin/chflags", "-R", "nouchg", path],
        ["/usr/bin/chflags", "nouchg", path],
    ):
        try:
            res = subprocess.run(
                args,
                check=False, capture_output=True, timeout=30,
            )
            if res.returncode == 0:
                ok_flag = True
                break
        except FileNotFoundError:
            break
        except Exception:
            continue
    return ok_flag


def ensure_macos_writable(path):
    """在 macOS 上为写入 .app 包内的路径做好准备。

    移除文件本身和 .app 包根目录的 immutable 标志，
    并移除包的 quarantine 属性。在其他操作系统上安全（空操作）。
    必须在创建备份之前和原子替换之前调用，
    因为这两个操作都会写入包内部。
    """
    import sys
    if sys.platform != "darwin":
        return
    try:
        if os.path.isfile(path) or os.path.isdir(path):
            remove_macos_immutable_flags(path)
    except Exception:
        pass
    try:
        app_path = find_app_bundle(path)
        if app_path and os.path.normcase(app_path) != os.path.normcase(path):
            remove_macos_immutable_flags(app_path)
            remove_macos_quarantine(app_path)
    except Exception:
        pass


def remove_macos_quarantine(path):
    """移除 .app 包的 com.apple.quarantine 属性。

    使用系统自带的 /usr/bin/xattr 工具 —— 无需额外的
    Python 包，在缺少 os.*xattr API 的 frozen 构建中同样可用。
    """
    import sys
    if sys.platform != "darwin":
        return
    try:
        subprocess.run(
            ["/usr/bin/xattr", "-dr", "com.apple.quarantine", path],
            check=False, capture_output=True, timeout=30,
        )
    except FileNotFoundError:
        pass
    except Exception:
        pass


def resign_macos_bundle(main_js_path):
    """在修改 main.js 后，使用 ad-hoc 签名重新签署 .app 包。

    在 macOS 上，对已签名 .app 包内任何文件的修改都会
    破坏代码签名。启用了 Hardened Runtime 的 Electron 应用
    之后会在启动时崩溃。codesign --force --sign - 会打上
    ad-hoc 签名（不含 Developer ID），这对本地运行已经足够。
    此外还会移除 com.apple.quarantine 属性，
    以免 Gatekeeper 弹出警告。
    """
    import sys
    if sys.platform != "darwin":
        return

    from patcher.utils.console import info, ok, warn

    app_path = find_app_bundle(main_js_path)
    if not app_path:
        # main.js 不在 .app 内（例如便携版副本）—— 跳过
        return

    info(f"正在重新签名 {os.path.basename(app_path)}（ad-hoc）……")
    try:
        subprocess.run(
            ["/usr/bin/codesign", "--force", "--deep", "--sign", "-", app_path],
            check=True, capture_output=True, text=True, timeout=60,
        )
        ok("已应用 ad-hoc 签名")
    except FileNotFoundError:
        warn("未找到 codesign —— 请安装 Xcode 命令行工具")
        return
    except subprocess.CalledProcessError as e:
        stderr = (e.stderr or "").strip()
        warn(f"codesign 执行失败：{stderr}")
        return

    remove_macos_quarantine(app_path)


def resign_macos_binary(path):
    """在修改后，使用 ad-hoc 签名重新签署 Antigravity 2.0 二进制文件。

    在 Apple Silicon 上，若代码签名与文件内容不一致，macOS 会立即
    向进程发送 SIGKILL。codesign --force --sign - 会把 Developer ID
    签名替换为 ad-hoc 签名（签名标识为「-」），这对本地运行已经足够。
    """
    import sys
    if sys.platform != "darwin":
        return

    from patcher.utils.console import info, ok, warn

    real = os.path.realpath(path)
    info(f"正在重新签名 {os.path.basename(real)}（ad-hoc）……")
    try:
        subprocess.run(
            ["/usr/bin/codesign", "--force", "--sign", "-", real],
            check=True, capture_output=True, text=True, timeout=60,
        )
        ok("已应用 ad-hoc 签名")
    except FileNotFoundError:
        warn("未找到 codesign —— 请安装 Xcode 命令行工具")
    except subprocess.CalledProcessError as e:
        warn(f"codesign 执行失败：{(e.stderr or '').strip()}")
