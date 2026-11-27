import os
import re
import sys
import errno
import mmap
import shutil
import contextlib
import filecmp

from patcher.constants import COLOR_CYAN
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
    resign_macos_bundle,
    resign_macos_binary,
    ensure_macos_writable,
)
from patcher.utils.update import handle_patch_failure
from patcher.utils.admin import terminate_processes
from patcher.utils.atomic import atomic_replace_posix, apply_patches_to_data

BAK_EXT = ".agybak"


# ----------------------------------------------------------------------- Gate --
# 基于字节特征码对 Go 编译的 agy/agy.exe 机器码打补丁。
# 特征码使用 re.S，使 '.' 也能匹配位移字节 0x0a。
class Gate:
    def __init__(self, sig, patched, fix, offset=0, desc=""):
        self.sig = re.compile(sig, re.S)
        self.patched = re.compile(patched, re.S)
        self.fix = fix
        self.offset = offset
        self.desc = desc

    def find(self, data):
        """返回 ('patched'|'unpatched', [需要写入的文件偏移列表])。
        若特征码不存在（未知版本），抛出 LookupError。
        允许出现多个 unpatched 匹配 —— 全部修补（Go 可能
        把同一个函数编译成多个副本）。"""
        patched_offsets = [m.start() + self.offset for m in self.patched.finditer(data)]
        if patched_offsets:
            return ("patched", patched_offsets)
        unpatched_offsets = [m.start() + self.offset for m in self.sig.finditer(data)]
        if not unpatched_offsets:
            raise LookupError("gate signature not found (unsupported version?)")
        return ("unpatched", unpatched_offsets)


    def resolve(self, data):
        """(kind, [write-offsets], concrete-gate). The concrete gate carries the fix bytes
        and label to apply — so a MultiGate can hand back the arch-matching sub-gate."""
        kind, offsets = self.find(data)
        return kind, offsets, self

    def resolve_all(self, data):
        """返回 [(kind, [写入偏移], 具体 gate)] —— 对 Gate 而言只有一个元素。"""
        return [self.resolve(data)]


class MultiGate:
    """One logical gate whose machine code differs per CPU arch and per build
    (the CLI eligibility check compiles to distinct instructions on amd64 vs
    arm64, and Apple reshaped it again in 1.2.7), so it declares one Gate
    signature per variant. Architectures never overlap, but one binary CAN
    match several same-arch gates at once (arm64 1.2.7 has both the inline w2
    check in the screen function and the w4 check inside the check helper) —
    every unpatched match must be patched, otherwise the screen survives."""

    def __init__(self, *gates, desc=""):
        self.gates = gates
        self.desc = desc

    def resolve_all(self, data):
        """返回所有匹配的子 gate，形式为 [(kind, [写入偏移], 具体 gate)]。
        若没有任何特征码匹配（未知版本），抛出 LookupError。"""
        matches = []
        err = None
        for g in self.gates:
            try:
                matches.append(g.resolve(data))
            except LookupError as e:
                err = e
        if not matches:
            raise err or LookupError("no gate signature matched")
        return matches


# ---------------------------------------------------------------------------
# Gate 1：CLI 资格校验拦截（初始检查的唯一关卡）。
# x64:
#   test rax,rax ; je eligible ; cmp byte[rax+8],0 ; jne eligible ; call failure_builder
# Repeating the non-null test keeps ZF=0, so jne always selects eligible.
# 特征码仅限定于检查逻辑的 16 字节核心：尾部（call + 寄存器溢出）
# 在不同构建间存在差异，因此不纳入匹配模式。
CLI_GATE_X64 = Gate(
    rb"\x48\x85\xc0\x0f\x84....\x80\x78\x08\x00\x0f\x85....",
    rb"\x48\x85\xc0\x0f\x84....\x48\x85\xc0\x90\x0f\x85....",
    b"\x48\x85\xc0\x90",
    offset=9,
    desc="eligibility screen off (x64)",
)
# arm64:
#   cbnz x1,error ; cbz x0,eligible ; ldrb w1,[x0,#8] ; tbnz w1,#0,eligible
#   bl failure_builder + spills.
# Loading 1 instead makes tbnz always select eligible.
# 单个严格的 gate 可覆盖两种已知的尾部形式：
#   - 经典形式：x0/x1/x2 -> [sp,#0x90]/[sp,#0x60]/[sp,#0x80]
#   - macOS 构建：x0/x1/x2/x3 -> [sp,#0x98]/[sp,#0x60]/[sp,#0x88]/[sp,#0x58]
CLI_GATE_ARM64 = Gate(
    rb"...\xb5...\xb4\x01\x20\x40\x39[\x01\x21\x41\x61\x81\xa1\xc1\xe1].[\x00-\x07]\x37"
    rb"...[\x94-\x97](?:\xe0\x4b\x00\xf9\xe1\x33\x00\xf9\xe2\x43\x00\xf9"
    rb"|\xe0\x4f\x00\xf9\xe1\x33\x00\xf9\xe2\x47\x00\xf9\xe3\x2f\x00\xf9)",
    rb"...\xb5...\xb4\x21\x00\x80\x52[\x01\x21\x41\x61\x81\xa1\xc1\xe1].[\x00-\x07]\x37"
    rb"...[\x94-\x97](?:\xe0\x4b\x00\xf9\xe1\x33\x00\xf9\xe2\x43\x00\xf9"
    rb"|\xe0\x4f\x00\xf9\xe1\x33\x00\xf9\xe2\x47\x00\xf9\xe3\x2f\x00\xf9)",
    b"\x21\x00\x80\x52",
    offset=8,
    desc="eligibility screen off (arm64)",
)
# arm64（CLI 1.2.7+）：检查逻辑被重新编译 —— 外层 cbnz 消失，
# 标志位读入 w4，且 tbnz 之后是 ldp 而不是 bl+溢出：
#   cbz x0,eligible ; ldrb w4,[x0,#8] ; tbnz w4,#0,eligible
#   ldp x4,x5,[x0,#0x48] ...
# mov w4,#1 使现有的 tbnz 始终选择 eligible 分支。
# 之所以单独设一个 gate：修补字节依赖寄存器（是 w4 而非 w1），无法
# 与旧模式合并。特征码很严格：在 1.2.7 的 linux/mac/windows arm64
# 构建中恰好只有一处匹配（已由 test_cli_releases 测试验证）。
CLI_GATE_ARM64_W4 = Gate(
    rb"[\x00\x20\x40\x60\x80\xa0\xc0\xe0]..\xb4\x04\x20\x40\x39"
    rb"[\x04\x24\x44\x64\x84\xa4\xc4\xe4].[\x00-\x07]\x37\x04\x94\x44\xa9",
    rb"[\x00\x20\x40\x60\x80\xa0\xc0\xe0]..\xb4\x24\x00\x80\x52"
    rb"[\x04\x24\x44\x64\x84\xa4\xc4\xe4].[\x00-\x07]\x37\x04\x94\x44\xa9",
    b"\x24\x00\x80\x52",
    offset=4,
    desc="eligibility screen off (arm64, w4)",
)
# arm64（CLI 1.2.7+，拦截函数中的内联检查）—— 拦截界面的主 gate，
# 缺少它时即使修补了 w4，"Eligibility check failed:" 界面仍会出现：
#   cbnz x1,? ; cbz x0,eligible ; ldrb w2,[x0,#8] ; tbnz w2,#0,eligible
#   bl check_helper ...
# mov w2,#1 使 tbnz 直接跳转到 eligible，不再调用辅助函数。
# 特征码很严格：在 1.2.7 的 linux/mac/windows arm64 中恰好只有一处匹配。
CLI_GATE_ARM64_W2 = Gate(
    rb"[\x01\x21\x41\x61\x81\xa1\xc1\xe1]..\xb5[\x00\x20\x40\x60\x80\xa0\xc0\xe0]..\xb4"
    rb"\x02\x20\x40\x39[\x02\x22\x42\x62\x82\xa2\xc2\xe2].[\x00-\x07]\x37...[\x94-\x97]",
    rb"[\x01\x21\x41\x61\x81\xa1\xc1\xe1]..\xb5[\x00\x20\x40\x60\x80\xa0\xc0\xe0]..\xb4"
    rb"\x22\x00\x80\x52[\x02\x22\x42\x62\x82\xa2\xc2\xe2].[\x00-\x07]\x37...[\x94-\x97]",
    b"\x22\x00\x80\x52",
    offset=8,
    desc="eligibility screen off (arm64, w2)",
)

CLI_GATE = MultiGate(
    CLI_GATE_X64,
    CLI_GATE_ARM64,
    CLI_GATE_ARM64_W2,
    CLI_GATE_ARM64_W4,
    desc="eligibility screen off",
)

ALL_GATES = [
    (CLI_GATE, "eligibility screen off"),
]


@contextlib.contextmanager
def _scan_data(f):
    # Reading a modified signed Mach-O through mmap can cause an uncatchable
    # CODESIGNING SIGKILL on macOS, including during post-write verification.
    if sys.platform == "darwin":
        f.seek(0)
        yield f.read()
        return
    if os.fstat(f.fileno()).st_size == 0:
        yield b""
        return
    mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
    try:
        yield mm
    finally:
        mm.close()


@contextlib.contextmanager
def _mapped(path):
    """用于扫描特征码的只读字节视图。

    在 macOS 上不对已签名文件做内存映射（有 SIGKILL 风险），
    而是通过 _scan_data 读取；其他系统使用零拷贝 mmap。"""
    with open(path, "rb") as f:
        with _scan_data(f) as data:
            yield data


def is_locked(path):
    """
    若文件被占用（应用正在运行）则返回 True。

    在 POSIX 上即使进程正在运行，也可以通过 os.replace 替换文件，
    因此只有 Windows 才视为会被锁定。

    注意：在 POSIX 上这并不能保证文件未被使用。
    如果确实需要判断占用情况，需要更复杂的逻辑
    （例如检查进程或文件锁）。
    """
    if os.name != "nt":
        return False

    try:
        with open(path, "r+b"):
            return False
    except OSError:
        return True


def get_status(path):
    """返回 ('patched'|'unpatched'|'unknown', None) —— 不向外抛出异常。
    只有当所有 gate 均已应用时才返回 'patched'。"""
    if not path or not os.path.isfile(path):
        return ("unknown", None)
    try:
        with _mapped(path) as d:
            states = []
            for gate, _ in ALL_GATES:
                try:
                    for state, _offsets, _g in gate.resolve_all(d):
                        states.append(state)
                except LookupError:
                    return ("unknown", None)
            if all(s == "patched" for s in states):
                return ("patched", None)
            if all(s == "unpatched" for s in states):
                return ("unpatched", None)
            return ("unpatched", None)  # 部分应用 —— 视为 unpatched
    except OSError:
        return ("unknown", None)


def is_already_patched(path):
    """与 IDE/asar 兼容的接口：仅当补丁已应用时返回 True。"""
    return get_status(path)[0] == "patched"


def _make_backup(path):
    """把干净的文件快照保存为 <path>.agybak。
    仅在文件处于 unpatched 状态时调用 —— 此时的字节就是原始内容。
    与当前文件不一致的备份说明已过期（应用自动更新过）——
    此时刷新备份，而不是继续保留旧的。"""
    bak = path + BAK_EXT
    if os.path.exists(bak):
        if filecmp.cmp(path, bak, shallow=False):
            return  # 备份已与当前构建一致
        info(f"备份已过期（应用已更新）—— 正在刷新 {os.path.basename(path)}{BAK_EXT}")
    else:
        info(f"正在创建备份 -> {os.path.basename(path)}{BAK_EXT}")
    if sys.platform == "darwin":
        ensure_macos_writable(path)
    try:
        shutil.copy2(path, bak)
    except (PermissionError, OSError) as e:
        need_retry = (
            sys.platform == "darwin"
            and isinstance(e, OSError)
            and e.errno in (errno.EPERM, errno.EACCES)
        )
        if need_retry:
            warn("备份被 macOS 文件标志阻止，正在移除标志后重试……")
            ensure_macos_writable(path)
            shutil.copy2(path, bak)
        else:
            raise
    fix_posix_permissions(bak)
    ok(f"备份：{os.path.basename(bak)}（{format_bytes(file_size(bak))}）")


def _copy_to_user_bin(path):
    from patcher.utils.file import get_posix_invoking_user_home
    user_home = get_posix_invoking_user_home()
    dest_dir = os.path.join(user_home, ".local", "bin") if user_home else os.path.expanduser("~/.local/bin")
    dest_path = os.path.join(dest_dir, "agy")
    if os.path.abspath(path) == os.path.abspath(dest_path):
        return
    info(f"正在将文件保存到用户目录 -> {dest_path}")
    try:
        os.makedirs(dest_dir, exist_ok=True)
        if os.path.exists(dest_path):
            try:
                os.remove(dest_path)
            except Exception:
                pass
        shutil.copy2(path, dest_path)
        os.chmod(dest_path, 0o755)
        ok(f"文件已成功复制到：{dest_path}")
    except Exception as e:
        warn(f"无法将文件复制到 {dest_path}：{e}")


def do_patch_agy(path):
    from patcher.cli import confirmed
    from patcher.utils.captcha import confirm_with_captcha

    if not path or not os.path.isfile(path):
        from patcher.cli import offer_download_and_block
        offer_download_and_block("Antigravity CLI")
        return

    hash_before = file_hash(path)
    info(f"目标：{color(path, COLOR_CYAN)}")
    hint(f"大小：{color(format_bytes(file_size(path)), COLOR_CYAN)}")
    print()

    write_success = False
    patches = []  # [(offset, gate), ...] —— 需要写入的 gate
    for attempt in range(2):
        if is_locked(path):
            if attempt == 0:
                warn("程序文件被占用（Antigravity CLI 正在运行）。")
                if confirmed("是否自动关闭正在运行的 agy 进程并重试？"):
                    terminate_processes(["agy"])
                    import time
                    time.sleep(1.5)
                    continue
            err("文件被占用 —— 请先关闭 Antigravity CLI。")
            return

        # 在 mmap 中扫描，并在写入之前关闭（零拷贝扫描）
        patches = []
        try:
            with _mapped(path) as d:
                all_patched = True
                for gate_obj, gate_label in ALL_GATES:
                    try:
                        matches = gate_obj.resolve_all(d)
                    except LookupError as e:
                        err(f"{gate_label}：{e}")
                        handle_patch_failure()
                        return
                    for kind, offsets, g in matches:
                        if kind == "unpatched":
                            all_patched = False
                            for off in offsets:
                                patches.append((off, g))
                if all_patched:
                    hint("agy 已打过补丁（所有 gate 均已应用）。")
                    if not confirm_with_captcha("仍要应用补丁吗？"):
                        return
                    # 重新打补丁：重写所有 gate
                    patches = []
                    for gate_obj, _ in ALL_GATES:
                        for _kind, offsets, g in gate_obj.resolve_all(d):
                            for off in offsets:
                                patches.append((off, g))
        except OSError as e:
            err(f"读取错误：{e}")
            return

        if not patches:
            return

        try:
            _make_backup(path)
        except (PermissionError, OSError) as e:
            err(f"备份错误：{e}")
            if sys.platform == "darwin":
                hint("macOS 阻止了写入（Errno 1 Operation not permitted）。")
                hint("请关闭 Antigravity，然后使用 sudo 重新运行本工具：")
                hint("  sudo python main.py   （或 sudo ./Open_AG_Patcher）")
            else:
                hint("没有写入权限 —— 请先关闭 agy，并以管理员/root 身份重新运行。")
            handle_patch_failure()
            return

        try:
            if os.name == "nt":
                # Windows：直接写入，并检查锁定状态
                with open(path, "r+b") as f:
                    bdata = bytearray(f.read())
                    bdata = apply_patches_to_data(bdata, patches)
                    f.seek(0)
                    f.write(bdata)
                    f.flush()
                    os.fsync(f.fileno())
            else:
                # POSIX：通过临时文件进行原子替换
                with open(path, "rb") as f:
                    bdata = bytearray(f.read())

                bdata = apply_patches_to_data(bdata, patches)

                # 使用安全的临时文件进行原子替换
                if sys.platform == "darwin":
                    ensure_macos_writable(path)
                atomic_replace_posix(path, bytes(bdata))

            write_success = True
            break
        except PermissionError as e:
            if attempt == 0:
                if sys.platform == "darwin":
                    warn(f"写入被 macOS 阻止（文件标志/属主）：{e}")
                    ensure_macos_writable(path)
                    import time
                    time.sleep(0.5)
                    continue
                warn(f"权限被拒绝（文件被占用）：{e}")
                if confirmed("是否自动关闭正在运行的 agy 进程并重试？"):
                    terminate_processes(["agy"])
                    import time
                    time.sleep(1.5)
                    continue
            err(f"写入错误（权限被拒绝）：{e}")
            if sys.platform == "darwin":
                hint("请关闭 Antigravity 并使用 sudo 重新运行：sudo python main.py")
            handle_patch_failure()
            return
        except OSError as e:
            if e.errno in (errno.EPERM, errno.EACCES) and attempt == 0 and sys.platform == "darwin":
                warn(f"写入被 macOS 阻止（文件标志/属主）：{e}")
                ensure_macos_writable(path)
                import time
                time.sleep(0.5)
                continue
            err(f"写入错误：{e}")
            handle_patch_failure()
            return
        except Exception as e:
            err(f"写入错误：{e}")
            handle_patch_failure()
            return

    if not write_success:
        handle_patch_failure()
        return

    hash_after = file_hash(path)
    resign_macos_bundle(path)
    resign_macos_binary(path)
    if os.name == "posix":
        _copy_to_user_bin(path)
    print()
    step("修补 agy 程序", True, f"{len(patches)} 个 gate")
    print()
    panel_rows = [
        ("目标", os.path.basename(path)),
    ]
    for off, g in patches:
        panel_rows.append(("Gate", f"{g.desc} @ 0x{off:x}"))
    if hash_before and hash_after:
        panel_rows.append(("修补前", f"{hash_before[:8]}...{hash_before[56:]}"))
        panel_rows.append(("修补后", f"{hash_after[:8]}...{hash_after[56:]}"))
    print_panel("打补丁完成", panel_rows)
    hint("请重启 Antigravity CLI 以使更改生效。")


def do_restore_agy(path):
    from patcher.cli import confirmed

    if not os.path.isfile(path):
        err(f"目标不是文件：{path}")
        return

    bak = path + BAK_EXT
    if not os.path.exists(bak):
        warn(f"{os.path.basename(path)} 没有备份（无内容可还原）。")
        return

    status, _ = get_status(path)
    if status != "patched":
        warn("agy 未打补丁 —— 跳过还原（备份可能来自其他版本）。")
        if not confirmed("仍要从备份还原吗？"):
            hint("已取消还原。")
            return

    if is_locked(path):
        err("程序文件被占用 —— 请先关闭 Antigravity CLI。")
        return

    if not confirmed("是否从备份还原 agy？"):
        hint("已取消还原。")
        return

    hash_before = file_hash(path)
    try:
        if os.name == "nt":
            shutil.copy2(bak, path)
        else:
            # 将备份读入内存
            with open(bak, "rb") as f:
                bak_data = f.read()

            # 使用备份的元数据进行原子替换
            atomic_replace_posix(path, bak_data, meta_source=bak)

        fix_posix_permissions(path)
    except Exception as e:
        err(f"还原错误：{e}")
        return

    hash_after = file_hash(path)
    resign_macos_bundle(path)
    resign_macos_binary(path)
    if os.name == "posix":
        _copy_to_user_bin(path)
    print()
    panel_rows = [("目标", os.path.basename(path))]
    if hash_before and hash_after and hash_before != hash_after:
        panel_rows.append(("修补前", f"{hash_before[:8]}...{hash_before[56:]}"))
        panel_rows.append(("修补后", f"{hash_after[:8]}...{hash_after[56:]}"))
    print_panel("还原完成", panel_rows)
