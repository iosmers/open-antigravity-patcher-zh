import os
import stat
import tempfile


def fsync_dir(dirpath):
    """同步目录，确保重命名操作可靠落盘。"""
    if os.name == "nt":
        return

    flags = os.O_RDONLY
    if hasattr(os, "O_DIRECTORY"):
        flags |= os.O_DIRECTORY

    fd = os.open(dirpath, flags)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def atomic_replace_posix(path, data, meta_source=None):
    """
    在 POSIX 系统上通过安全的临时文件原子替换目标文件。

    Args:
        path: 目标文件路径
        data: 要写入的字节数据
        meta_source: 元数据（属主、权限）的来源文件。
                     默认使用 path。
    """
    path = os.path.abspath(path)

    # 禁止对符号链接进行操作
    if os.path.islink(path):
        raise ValueError("Refusing to patch symlink")

    if not os.path.isfile(path):
        raise ValueError("Target is not a regular file")

    if meta_source is None:
        meta_source = path

    st = os.stat(meta_source)
    directory = os.path.dirname(path)

    # 使用 O_EXCL 安全地创建临时文件
    fd, tmp_path = tempfile.mkstemp(
        prefix=f".{os.path.basename(path)}.",
        suffix=".tmp",
        dir=directory,
    )

    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())

            # 在 chmod 之前设置属主（chown 可能会清除 setuid/setgid）
            try:
                os.fchown(f.fileno(), st.st_uid, st.st_gid)
            except OSError:
                # 可能权限不足，这通常不是致命问题
                pass

            # 应用原始文件的权限位
            os.fchmod(f.fileno(), stat.S_IMODE(st.st_mode))

        # 原子替换
        os.replace(tmp_path, path)

        # 同步目录
        fsync_dir(directory)

        tmp_path = None  # 标记为已成功替换
    finally:
        # 出错时删除临时文件
        if tmp_path is not None:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass


def validate_patch_params(bdata, patches):
    """
    在应用补丁前校验补丁参数。

    Args:
        bdata: 包含文件数据的 bytearray
        patches: 补丁列表，格式为 (offset, gate_object)

    Raises:
        ValueError: 当补丁参数不合法时抛出
    """
    for off, g in patches:
        # 检查偏移量是否为负
        if off < 0:
            raise ValueError(f"Negative offset: {off}")

        fix = g.fix

        # 如果存在用于校验的原始字节
        if hasattr(g, "orig"):
            orig = g.orig

            # 补丁不得改变文件大小
            if len(fix) != len(orig):
                raise ValueError(
                    f"Patch changes file size: orig={len(orig)}, fix={len(fix)}"
                )

            # 检查是否越过文件边界
            if off + len(orig) > len(bdata):
                raise ValueError(
                    f"Patch offset out of bounds: offset={off}, "
                    f"patch_size={len(orig)}, file_size={len(bdata)}"
                )

            # 校验原始字节是否匹配
            if bdata[off:off + len(orig)] != orig:
                raise ValueError(
                    f"Original bytes mismatch at offset {off}"
                )
        else:
            # 没有原始字节时，至少检查边界
            if off + len(fix) > len(bdata):
                raise ValueError(
                    f"Patch offset out of bounds: offset={off}, "
                    f"patch_size={len(fix)}, file_size={len(bdata)}"
                )


def apply_patches_to_data(bdata, patches):
    """
    对 bytearray 应用补丁，并进行校验。

    Args:
        bdata: 包含文件数据的 bytearray
        patches: 补丁列表，格式为 (offset, gate_object)

    Returns:
        bytearray: 修改后的数据
    """
    # 应用前校验所有补丁
    validate_patch_params(bdata, patches)

    # 应用补丁
    for off, g in patches:
        if hasattr(g, "orig"):
            bdata[off:off + len(g.orig)] = g.fix
        else:
            bdata[off:off + len(g.fix)] = g.fix

    return bdata
