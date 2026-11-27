# AI 智能体指南：`test-agy` 与补丁 gate

## 1. 这是什么

`test-agy/` 用于验证补丁工具的字节签名（`source/patcher/agy/patcher.py`，
`CLI_GATE`）存在于 `google-antigravity/antigravity-cli` 最新发布的
**所有官方构建**中（linux/mac/windows × x64/arm64）。
Google 会周期性地重新编译 eligibility 检查 —— 该测试能及时捕捉到这一变化。

文件：
- `test_cli_releases.py` —— 测试本体（仅使用标准库）。
- `__init__.py` —— 空文件，供 `unittest discover` 使用。

## 2. 如何运行

```bash
python test-agy/test_cli_releases.py
python -m unittest discover -s test-agy -v
```

环境变量：
- `AGY_RELEASE_TAG` —— 检查指定 tag 而不是 `latest`（例如 `1.2.7`）。
- `AGY_TEST_CACHE` —— 压缩包缓存目录（不设置的话每次运行都会下载约 340 MB）。
- `GITHUB_TOKEN` —— 遇到 GitHub API 速率限制时使用。

下载的二进制/缓存**不要提交**。测试不会改动下载文件的原件 ——
补丁是在临时副本上验证的。

## 3.