import os
import glob
import shutil


def clean_path(raw_path):
    """去除首尾的引号/空格 —— 与 ide/discovery.clean_path 行为一致。"""
    return raw_path.strip().strip('"').strip("'")


def _dedup_newest(paths):
    """对真实路径去重，并按修改时间排序（最新的在前）。
    等价于 patch.py 中的 _dedup_newest。"""
    seen = set()
    out = []
    existing = {p for p in paths if p and os.path.exists(p)}
    for p in sorted(existing, key=lambda x: os.path.getmtime(x), reverse=True):
        key = os.path.normcase(os.path.realpath(p))
        if key not in seen:
            seen.add(key)
            out.append(p)
    return out


def _win_candidate_dirs():
    """Windows 上搜索 agy.exe 的根目录：环境变量 + scoop + Programs。"""
    out = []
    for var in ("LOCALAPPDATA", "PROGRAMFILES", "PROGRAMFILES(X86)",
                "ProgramData", "APPDATA"):
        p = os.environ.get(var)
        if not p:
            continue
        out.append(p)
        programs = os.path.join(p, "Programs")
        if os.path.isdir(programs):
            out.append(programs)
    up = os.environ.get("USERPROFILE", "")
    if up:
        out.append(os.path.join(up, "scoop", "apps"))
    scoop = os.environ.get("SCOOP", "")
    if scoop:
        out.append(os.path.join(scoop, "apps"))
    return [p for p in out if p and os.path.isdir(p)]


def _posix_candidate_dirs():
    """POSIX 上搜索 agy 程序的目录。"""
    from patcher.utils.file import get_posix_invoking_user_home
    user_home = get_posix_invoking_user_home()
    out = ["/usr/local/bin", "/usr/bin", "/opt/antigravity/bin", "/opt/antigravity"]
    if user_home:
        out.append(os.path.join(user_home, ".local/bin"))
        out.append(os.path.join(user_home, "bin"))
    else:
        out.append(os.path.expanduser("~/.local/bin"))
        out.append(os.path.expanduser("~/bin"))
    return [p for p in out if p and os.path.isdir(p)]


def _win_find():
    cands = []
    w = shutil.which("agy")
    if w:
        # which() 会返回来自 PATHEXT 的大写 .EXE；此处归一化以便去重/输出
        base, ext = os.path.splitext(w)
        cands.append(base + ext.lower())
    for root in _win_candidate_dirs():
        cands += glob.glob(os.path.join(root, "agy", "bin", "agy.exe"))
        cands += glob.glob(os.path.join(root, "agy", "*", "bin", "agy.exe"))  # scoop version dirs
        cands += glob.glob(os.path.join(root, "agy*", "agy.exe"))
    return _dedup_newest(cands)


def _posix_find():
    cands = []
    local_agy = os.path.join(os.getcwd(), "agy")
    if os.path.isfile(local_agy):
        cands.append(local_agy)
    w = shutil.which("agy")
    if w:
        cands.append(w)
    for root in _posix_candidate_dirs():
        cands += glob.glob(os.path.join(root, "agy"))
    return _dedup_newest(cands)


def find_agy_binary():
    """返回 agy 程序的路径（Windows 上为 agy.exe，POSIX 上为 agy），找不到则返回 ''。
    查找不依赖固定位置：PATH + 标准目录 + scoop。"""
    try:
        hits = _win_find() if os.name == "nt" else _posix_find()
    except Exception:
        return ""
    return hits[0] if hits else ""


def resolve_agy_path(raw_path):
    """解析用户提供的 agy 程序路径。
    返回有效路径或 ''。若直接指向 agy/agy.exe 文件则直接采用；
    若是目录，则使用类似 find_agy_binary 的通配规则在其中查找。"""
    if not raw_path:
        return ""
    cleaned = clean_path(raw_path)
    if not cleaned:
        return ""
    resolved = os.path.abspath(os.path.expandvars(os.path.expanduser(cleaned)))

    if os.path.isfile(resolved):
        name = os.path.basename(resolved).lower()
        if name in ("agy", "agy.exe"):
            return resolved
        # 任意文件 —— 按原样接受（用户更清楚自己的目标）
        return resolved

    if os.path.isdir(resolved):
        # 在指定目录内查找（包括 bin/ 以及类似 scoop 的 version/ 结构）
        patterns = (["agy.exe", os.path.join("bin", "agy.exe")] if os.name == "nt"
                    else ["agy", os.path.join("bin", "agy")])
        hits = []
        for pat in patterns:
            hits += glob.glob(os.path.join(resolved, pat))
            hits += glob.glob(os.path.join(resolved, "*", pat))
        deduped = _dedup_newest(hits)
        if deduped:
            return deduped[0]

    return ""
