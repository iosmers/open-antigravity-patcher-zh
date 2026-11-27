import os
import glob


def _user_home():
    """用户主目录。在 POSIX 上通过 sudo 运行时，
    返回调用者用户的主目录（~user）而不是 /root，
    以便正确定位 ~/.vscode-server 和 ~/.gemini。"""
    if os.name == "posix":
        from patcher.utils.file import get_posix_invoking_user_home
        home = get_posix_invoking_user_home()
        if home:
            return home
    return os.path.expanduser("~")


def clean_path(raw_path):
    """去除首尾的引号/空格 —— 与 ide/agy discovery 行为一致。"""
    return raw_path.strip().strip('"').strip("'")


def _extension_roots():
    """VS Code 扩展的根目录（正式版、Insiders、OSS、remote-server）。
    若设置了环境变量 VSCODE_EXTENSIONS，则该覆盖项排在最前。"""
    home = _user_home()
    roots = []
    env = os.environ.get("VSCODE_EXTENSIONS")
    if env and os.path.isdir(env):
        roots.append(env)
    roots += [
        os.path.join(home, ".vscode", "extensions"),
        os.path.join(home, ".vscode-insiders", "extensions"),
        os.path.join(home, ".vscode-oss", "extensions"),
        os.path.join(home, ".vscode-server", "extensions"),
        os.path.join(home, ".vscode-server-insiders", "extensions"),
    ]
    seen = set()
    out = []
    for r in roots:
        key = os.path.normcase(os.path.abspath(r))
        if key not in seen and os.path.isdir(r):
            seen.add(key)
            out.append(r)
    return out


def find_extension_dir():
    """返回最新的 google.google-antigravity-* 扩展目录。
    目录名带版本号（例如 google.google-antigravity-1.0.0），
    因此按通配符查找并按修改时间排序（最新的在前）。"""
    candidates = []
    for root in _extension_roots():
        candidates += glob.glob(
            os.path.join(root, "google.google-antigravity-*")
        )
    dirs = [d for d in candidates if os.path.isdir(d)]
    if not dirs:
        return ""
    dirs.sort(key=lambda d: os.path.getmtime(d), reverse=True)
    return dirs[0]


def find_extension_js():
    """返回 google.google-antigravity 扩展的 extension.js 路径，找不到则返回 ''。"""
    ext_dir = find_extension_dir()
    if not ext_dir:
        return ""
    js = os.path.join(ext_dir, "extension.js")
    return js if os.path.isfile(js) else ""


def resolve_extension_path(raw_path):
    """解析用户提供的 extension.js 路径。
    支持：extension.js 文件本身、扩展目录
    （google.google-antigravity-*），或 extensions 根目录。"""
    if not raw_path:
        return ""
    cleaned = clean_path(raw_path)
    if not cleaned:
        return ""
    resolved = os.path.abspath(os.path.expandvars(os.path.expanduser(cleaned)))

    if os.path.isfile(resolved):
        if os.path.basename(resolved).lower() == "extension.js":
            return resolved
        # 任意文件 —— 按原样接受（用户更清楚自己的目标）
        return resolved

    if os.path.isdir(resolved):
        # 扩展自身的目录
        direct = os.path.join(resolved, "extension.js")
        if os.path.isfile(direct):
            return direct
        # extensions 根目录 —— 在其中查找 google.google-antigravity-*
        hits = glob.glob(
            os.path.join(resolved, "google.google-antigravity-*", "extension.js")
        )
        hits = [h for h in hits if os.path.isfile(h)]
        if hits:
            hits.sort(key=lambda p: os.path.getmtime(p), reverse=True)
            return hits[0]

    return ""


def find_gemini_antigravity_binary():
    """扩展下载到 ~/.gemini/bin 的程序文件。
    Windows: antigravity.exe / agy.exe, macOS/Linux: antigravity / agy.
    返回路径或 ''。仅由「Antigravity VS Code 补丁」菜单项使用。"""
    home = _user_home()
    ext = ".exe" if os.name == "nt" else ""
    for name in ("antigravity", "agy"):
        p = os.path.join(home, ".gemini", "bin", name + ext)
        if os.path.isfile(p):
            return p
    return ""


def describe_gemini_binary_path():
    """返回便于阅读的预期程序路径（用于提示信息）。"""
    name = "antigravity.exe" if os.name == "nt" else "antigravity"
    return os.path.join("~", ".gemini", "bin", name)
