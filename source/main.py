import sys
import os

from patcher.utils.admin import is_admin, run_as_admin
from patcher.utils.console import setup_console
from patcher.cli import run_cli, confirmed


if __name__ == "__main__":
    setup_console()
    if os.name == "nt" and os.environ.get("SKIP_ELEVATION") != "1" and not is_admin():
        if run_as_admin():
            sys.exit(0)
        else:
            print("  [!] 无法提升权限，脚本可能无法修改文件。")
    elif os.name == "posix" and not is_admin():
        print("  [!] 修补根目录下的文件需要 root 权限。")
        if confirmed("是否使用 sudo 重新启动？"):
            try:
                if getattr(sys, "frozen", False):
                    args = ["sudo", sys.executable] + sys.argv[1:]
                else:
                    args = ["sudo", sys.executable] + sys.argv
                os.execvp("sudo", args)
            except Exception as e:
                print(f"  [!] 使用 sudo 重新启动失败：{e}")
                sys.exit(1)
        else:
            from patcher.constants import COLOR_YELLOW
            from patcher.utils.console import color
            print(color("  [!] 将在无 root 权限下继续，可能出现写入错误。", COLOR_YELLOW))
            print()

    try:
        run_cli()
    except KeyboardInterrupt:
        print("\n  [i] 正在退出……")
        sys.exit(0)
    except (PermissionError, OSError) as e:
        # 防止出现截图里那种未处理的 traceback
        # （备份 language_server.agybak -> Errno 1 Operation not permitted）：
        # 不再显示 "Failed to execute script 'main'"，而是给出易懂的提示。
        print(f"\n  [!] 文件系统错误：{e}")
        import sys as _sys

        if _sys.platform == "darwin":
            print("  [i] macOS 阻止了对 Antigravity.app 内部的写入。")
            print("  [i] 请关闭 Antigravity 并使用 sudo 重新运行：")
            print("        sudo python main.py   （或 sudo ./Open_AG_Patcher）")
            print("  [i] 如果仍提示 'Operation not permitted'，请检查文件标志：")
            print("        ls -lO /Applications/Antigravity.app/Contents/resources/bin/language_server")
        else:
            print("  [i] 没有写入权限 —— 请先关闭 Antigravity，并以管理员/root 身份重新运行。")
        sys.exit(1)
    except Exception as e:
        print(f"\n  [!] 未预期的错误：{e}")
        print("  [i] 请反馈问题：https://github.com/AvenCores/open-antigravity-unlock/issues")
        sys.exit(1)
