import random

from patcher.utils.console import warn, hint, color, COLOR_CYAN


def generate_math_captcha():
    """生成一个数学验证码（两个两位数相加）。

    Returns:
        tuple[str, str]: (可读的题目, 期望的答案字符串)。
    """
    a = random.randint(10, 99)
    b = random.randint(10, 99)
    question = f"{a} + {b} = ?"
    answer = str(a + b)
    return question, answer


def confirm_with_captcha(message):
    """显示警告，并要求用户解答数学验证码。

    Args:
        message: 向用户展示的上下文/提示（例如即将确认的操作）。

    Returns:
        bool: 用户答对验证码返回 True；用户取消（输入为空或
        按下 Ctrl+C）返回 False。
    """
    # 使用局部导入避免循环依赖：captcha.py 被各 patcher 模块使用，
    # 而 cli.py 又导入了这些模块。
    from patcher.cli import _read_console_line

    warn("警告：该文件似乎已经打过补丁。")
    warn("重复打补丁很可能没有必要，并且可能引发问题。")
    warn("如果你确定要继续，请解答下方的验证码。")
    hint("答案留空并按回车即可返回主菜单。")

    while True:
        question, expected = generate_math_captcha()
        print(f"  [?] {message}")
        prompt = f"        {question} （{color('答案', COLOR_CYAN)}）: "

        try:
            raw = _read_console_line(prompt).strip()
        except (EOFError, KeyboardInterrupt):
            return False

        if not raw:
            return False

        if raw == expected:
            return True

        warn("答案错误，请用新的验证码重试。")
