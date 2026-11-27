<div align="center">
    <a href="https://www.youtube.com/@avencores/" target="_blank">
      <img src="https://github.com/user-attachments/assets/338bcd74-e3c3-4700-87ab-7985058bd17e" alt="YouTube" height="40">
    </a>
    <a href="https://t.me/avencoresyt" target="_blank">
      <img src="https://github.com/user-attachments/assets/939f8beb-a49a-48cf-89b9-d610ee5c4b26" alt="Telegram" height="40">
    </a>
    <a href="https://vk.ru/avencoresreuploads" target="_blank">
      <img src="https://github.com/user-attachments/assets/dc109dda-9045-4a06-95a5-3399f0e21dc4" alt="VK" height="40">
    </a>
    <a href="https://dzen.ru/avencores" target="_blank">
      <img src="https://github.com/user-attachments/assets/bd55f5cf-963c-4eb8-9029-7b80c8c11411" alt="Dzen" height="40">
    </a>
</div>

# 🔑 Open AG Patcher
<p align="center">
  <img src="https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54" alt="Python">
  <a href="./LICENSE"><img src="https://img.shields.io/badge/License-GPL--3.0-blue?style=for-the-badge" alt="GPL-3.0 License"></a>
  <img src="https://img.shields.io/badge/%E8%AF%AD%E8%A8%80-%E4%B8%AD%E6%96%87-brightgreen?style=for-the-badge" alt="中文">
  <a href="https://github.com/iosmers/open-antigravity-patcher-zh/stargazers"><img src="https://img.shields.io/github/stars/iosmers/open-antigravity-patcher-zh?style=for-the-badge" alt="GitHub stars"></a>
  <img src="https://img.shields.io/github/forks/iosmers/open-antigravity-patcher-zh?style=for-the-badge" alt="GitHub forks">
  <a href="https://github.com/iosmers/open-antigravity-patcher-zh/watchers">
  <img src="https://img.shields.io/github/watchers/iosmers/open-antigravity-patcher-zh?style=for-the-badge" alt="GitHub Watchers"></a>
  <a href="https://github.com/iosmers/open-antigravity-patcher-zh/pulls"><img src="https://img.shields.io/github/issues-pr/iosmers/open-antigravity-patcher-zh?style=for-the-badge" alt="GitHub pull requests"></a>
  <a href="https://github.com/iosmers/open-antigravity-patcher-zh/issues"><img src="https://img.shields.io/github/issues/iosmers/open-antigravity-patcher-zh?style=for-the-badge" alt="GitHub issues"></a>
</p>

> 🌏 **本仓库是中文汉化版** —— [`iosmers/open-antigravity-patcher-zh`](https://github.com/iosmers/open-antigravity-patcher-zh)
>
> - **原作者**：AvenCores（原仓库 `AvenCores/open-antigravity-patcher` 与作者账号均已无法访问）
> - **现存可参考副本**：[trustybird/AvenCores-open-antigravity-patcher](https://github.com/trustybird/AvenCores-open-antigravity-patcher)（非官方镜像）
> - **汉化范围**：命令行界面、菜单、提示与错误信息、README 文档；补丁逻辑与上游完全一致。
> - **反馈建议**：功能性 Bug 请参考上述镜像仓库的说明；汉化用词与发布相关问题请在本仓库提 Issue。

面向 Antigravity 2.0、Antigravity IDE、Antigravity CLI 以及 VS Code 的 Google Antigravity 扩展的开源补丁工具：无需 VPN、也无需更换 Google 账号区域即可解除区域限制。它是 [Antigravity IDE 无需 VPN 和更换 Google 账号区域](https://github.com/confeden/Antigravity) 这一工具的开源替代实现。

![maxresdefault](https://i.ibb.co/s9Vh80CM/python-w-TPlox-Po-G4.png)

# 🎦 安装与问题排查视频指南

![maxresdefault](https://github.com/user-attachments/assets/54c4f1bd-01f5-4ee8-92d1-f7bbb910d079)

<div align="center">

[**在 YouTube 观看**](https://youtu.be/GyQVTxgt12E)

[**在 Rutube 观看**](https://rutube.ru/video/aba4484f8e0b5e67e966ff8229385f83/)

[**在 Dzen 观看**](https://dzen.ru/video/watch/6a7c430575822e0e4ba2970e)

[**在 VK Video 观看**](https://vkvideo.ru/video-234234162_456239108)

[**在 Telegram 观看**](https://t.me/avencoreschat/571689)

</div>

## ⚠️ HTTP 500 Internal Server Error 错误
如果在 Antigravity IDE 中发起请求时出现 HTTP 500 Internal Server Error，那基本无能为力，只能更换账号（建议换成 Antigravity IDE 官方支持的区域，或已购买付费订阅的账号）。即便是付费版工具也无法解决这个问题。

**错误示例**
```
Trajectory ID: 2669b09c-1d11-4620-9bfa-6ad1f0e26a88
Error: HTTP 500 Internal Server Error
Sherlog: 
TraceID: 0xd9ada64bcca3260c
Headers: {"Alt-Svc":["h3=\":443\"; ma=2592000,h3-29=\":443\"; ma=2592000"],"Content-Length":["109"],"Content-Type":["text/event-stream"],"Date":["Sat, 14 Mar 2026 13:51:24 GMT"],"Server":["ESF"],"Server-Timing":["gfet4t7; dur=423"],"Vary":["Origin","X-Origin","Referer"],"X-Cloudaicompanion-Trace-Id":["d9ada64bcca3260c"],"X-Content-Type-Options":["nosniff"],"X-Frame-Options":["SAMEORIGIN"],"X-Xss-Protection":["0"]}

{
  "error": {
    "code": 500,
    "message": "Internal error encountered.",
    "status": "INTERNAL"
  }
}
```

## ⚠️ HTTP 403 Forbidden / SUBSCRIPTION_REQUIRED (#3501) / Agent execution terminated due to error 错误
如果 Antigravity IDE 或 CLI（`agy`）出现 `HTTP 403 Forbidden`、原因为 `SUBSCRIPTION_REQUIRED`，或提示 `You do not have a valid license of this product`、`Agent execution terminated due to error`，那么这既不是本地补丁的问题，也不是 `Eligibility Check` 界面的问题。

该错误与 Google API 以及用户账号状态有关：许可证、访问权限或 Google 服务端的权限校验。补丁工具只修改 Antigravity / Antigravity CLI 的本地文件，无法为账号授予许可证，也无法改变 Google API 的返回结果，因此对这类错误无能为力。

**解决方案：**
1. **更换 Google 账号区域**，或使用注册在 Antigravity 官方支持区域的账号。
2. **如果更换区域仍无效**，则需要购买官方订阅。

**可选套餐（Google AI）：**

*   **Google AI Plus**
    *   **价格：** 每月 445 ₽
    *   **存储空间：** 400 GB
    *   **功能：** 使用 AI 工具提升效率，Gemini 额度提升至 2 倍*。
    *   [订阅 Plus](https://one.google.com/about/google-ai-plans/) | [查看套餐权益](https://one.google.com/about/google-ai-plans/) *(有附加条件)*
*   **Google AI Pro**
    *   **价格：** 1 790 ₽/月
    *   **存储空间：** 5 TB
    *   **功能：** Gemini 额度提升至 4 倍*，做更多事。
    *   [订阅 Pro](https://one.google.com/about/google-ai-plans/) | [查看套餐权益](https://one.google.com/about/google-ai-plans/) *(有附加条件)*
*   **Google AI Ultra**
    *   **价格：** 6 990 ₽/月起
    *   **存储空间：** 20 TB 起
    *   **功能：** Gemini 额度提升至 20 倍*，加速工作流程。
    *   [订阅 Ultra](https://one.google.com/about/google-ai-plans/) | [查看套餐权益](https://one.google.com/about/google-ai-plans/) *(有附加条件)*

**错误示例：**
```json
{
  "error": {
    "code": 403,
    "details": [
      {
        "@type": "type.googleapis.com/google.rpc.ErrorInfo",
        "domain": "cloudaicompanion.googleapis.com",
        "metadata": {
          "error_number": "1001",
          "uiMessage": "true"
        },
        "reason": "SUBSCRIPTION_REQUIRED"
      }
    ],
    "message": "You do not have a valid license of this product. Please contact your administrator to request a license. If you are not an enterprise user and believe you are receiving this message as an error, please try using the latest version and logging in again. (#3501)",
    "status": "PERMISSION_DENIED"
  }
}
```

## ⚠️ HTTP 400 Bad Request 错误
如果你收到 `HTTP 400 Bad Request` 并附带 `User location is not supported for the API use` 消息，说明 Google 判定你所在的位置不受支持。

**重要提示：** 使用 VPN、代理或其他绕过限制的方式可能被 Google 检测到并导致该错误。Google 正在积极打击各类绕过手段，如果你的 IP 地址或会话中的其他参数引起怀疑，访问可能会被封锁。

**解决方案：**
1. 应用补丁（**PATCH → `1`：Antigravity IDE patch**）。补丁工具会在代码层面正确配置 `isGoogleInternal` 绕过。
2. 如果已经打过补丁，请尝试更换 Google 账号或使用其他 VPN。
3. 可以尝试 **[Xbox DNS](https://xbox-dns.ru/)**、**[dns.malw.link](https://info.dns.malw.link/)**、**[GeoHide](https://dns.geohide.ru:8443/)**（在电脑或路由器上使用的专用解锁 DNS 服务器）。

**错误示例：**
```json
{
  "error": {
    "code": 400,
    "message": "User location is not supported for the API use.",
    "status": "FAILED_PRECONDITION"
  }
}
```

## ⚠️ HTTP 429 Too Many Requests / RESOURCE_EXHAUSTED 错误

向 Antigravity 发送提示词时出现配额耗尽错误：

```
Error: HTTP 429 Too Many Requests
{
  "error": {
    "code": 429,
    "message": "Resource has been exhausted (e.g. check quota).",
    "status": "RESOURCE_EXHAUSTED"
  }
}
```

带 Sherlog 的完整形式：
```
Error: HTTP 429 Too Many Requests
Sherlog:
TraceID: 0xe83b93ad455d1950
Headers: {"Alt-Svc":["h3=\":443\"; ma=2592000,h3-29=\":443\"; ma=2592000"],"Content-Length":["139"],"Content-Type":["text/event-stream"],"Date":["Sun, 06 Sep 2026 10:44:19 GMT"],"Server":["ESF"],"Server-Timing":["gfet4t7; dur=502"],"Vary":["Origin","X-Origin","Referer"],"X-Cloudaicompanion-Trace-Id":["e83b93ad455d1950"],"X-Content-Type-Options":["nosniff"],"X-Frame-Options":["SAMEORIGIN"],"X-Xss-Protection":["0"]}
```

**解决方案：** 重置 Antigravity 数据目录（干净的配置 + 全新的 token），之后可选地从备份恢复会话记录。下面是 Windows、macOS 和 Linux 的完整指南。

> **Antigravity 与 Antigravity IDE 的区别：** Antigravity 2.0 的数据目录名为 `Antigravity`，Antigravity IDE 的数据目录名为 `Antigravity IDE`。请在下面的命令中替换为你自己的目录名。为简洁起见，后文统一使用 `Antigravity`。

### Windows（完整指南）

**1.** 完全退出 Antigravity（托盘图标 → `Quit` / `退出`，并在任务管理器中确认没有 `Antigravity` 进程）。

**2.** 打开 `%appdata%`（`Win+R` → 输入 `%appdata%` → 回车）。找到 `Antigravity` 文件夹，把它移动到安全位置，例如桌面：
```powershell
Move-Item "$env:APPDATA\Antigravity" "$env:USERPROFILE\Desktop\Antigravity-backup"
```

**3.** 启动 Antigravity，完成登录，发送一条测试提示词检查连接。429 错误应该消失了。

**4.** 如果一切正常，关闭 Antigravity。

**5.** *（可选，恢复会话记录）* 我们只需要聊天数据：
- `User\globalStorage`（你的聊天记录）
- `User\workspaceStorage`

第 3 步启动时，Antigravity 已经重新创建了一个干净的 `%appdata%\Antigravity` 目录。只删除其中这两个文件夹，然后从备份中复制过来：
```powershell
Remove-Item -Recurse -Force "$env:APPDATA\Antigravity\User\globalStorage"
Remove-Item -Recurse -Force "$env:APPDATA\Antigravity\User\workspaceStorage"

Copy-Item -Recurse "$env:USERPROFILE\Desktop\Antigravity-backup\User\globalStorage" "$env:APPDATA\Antigravity\User\"
Copy-Item -Recurse "$env:USERPROFILE\Desktop\Antigravity-backup\User\workspaceStorage" "$env:APPDATA\Antigravity\User\"
```

> ⚠️ **不要复制**备份中的 `settings.json` 文件，否则会把旧的问题配置带回来。

**6.** 启动 Antigravity，检查会话记录并发送提示词。如果一切正常，就可以删除备份了：
```powershell
Remove-Item -Recurse -Force "$env:USERPROFILE\Desktop\Antigravity-backup"
```

### macOS（完整指南）

**1.** 完全退出 Antigravity（`Cmd+Q`，确认 Dock 图标下方的小圆点消失）。

**2.** 把数据目录移动到安全位置：
```bash
mv ~/Library/Application\ Support/Antigravity ~/Desktop/Antigravity-backup
```

**3.** 启动 Antigravity，完成登录，发送一条测试提示词 —— 429 错误应该消失了。

**4.** 如果一切正常，退出 Antigravity（`Cmd+Q`）。

**5.** *（可选，恢复会话记录）* 第 3 步启动时，Antigravity 已经重新创建了一个干净的 `~/Library/Application Support/Antigravity` 目录。只删除其中的聊天存储目录，然后从备份中复制过来：
```bash
rm -rf ~/Library/Application\ Support/Antigravity/User/globalStorage
rm -rf ~/Library/Application\ Support/Antigravity/User/workspaceStorage

cp -a ~/Desktop/Antigravity-backup/User/globalStorage ~/Library/Application\ Support/Antigravity/User/
cp -a ~/Desktop/Antigravity-backup/User/workspaceStorage ~/Library/Application\ Support/Antigravity/User/
```

> ⚠️ **不要复制**备份中的 `settings.json` 文件，否则会把旧的问题配置带回来。

**6.** 启动 Antigravity，检查会话记录并发送提示词。如果一切正常，就可以删除备份了：
```bash
rm -rf ~/Desktop/Antigravity-backup
```

### Linux（完整指南）

Linux 上的数据目录：`${XDG_CONFIG_HOME:-~/.config}/Antigravity`（通常是 `~/.config/Antigravity`）。

**1.** 完全退出 Antigravity：
```bash
pkill -f -i antigravity; sleep 2; pgrep -a -i antigravity || echo "closed"
```

**2.** 把数据目录移动到安全位置：
```bash
# 标准路径
mv ~/.config/Antigravity ~/Antigravity-backup

# 如果设置了 XDG_CONFIG_HOME：
# mv "${XDG_CONFIG_HOME:-$HOME/.config}/Antigravity" ~/Antigravity-backup
ls -d ~/Antigravity-backup
```

**3.** 启动 Antigravity，完成登录，发送一条测试提示词 —— 429 错误应该消失了。

**4.** 如果一切正常，退出 Antigravity（见第 1 步）。

**5.** *（可选，恢复会话记录）* 第 3 步启动时，Antigravity 已经重新创建了一个干净的 `~/.config/Antigravity` 目录。只删除其中的聊天存储目录，然后从备份中复制过来：
```bash
rm -rf ~/.config/Antigravity/User/globalStorage
rm -rf ~/.config/Antigravity/User/workspaceStorage

cp -a ~/Antigravity-backup/User/globalStorage ~/.config/Antigravity/User/
cp -a ~/Antigravity-backup/User/workspaceStorage ~/.config/Antigravity/User/
```

> ⚠️ **不要复制**备份中的 `settings.json` 文件，否则会把旧的问题配置带回来。

**6.** 启动 Antigravity，检查会话记录并发送提示词。如果一切正常，就可以删除备份了：
```bash
rm -rf ~/Antigravity-backup
```

### 为什么这样有效

移动数据目录后，Antigravity 会从零创建新的配置 —— 全新的 token、干净的配额。与已耗尽配额的旧绑定关系就被重置了。

### 给已打过补丁的用户的说明

补丁修改的是已安装应用内部的 `main.js`（macOS 上位于 `.app` 包内），移动数据目录**不会影响**它，因此不需要重新打补丁。

唯一会被重置的是 `settings.json` 中的运行时 workaround。如果重置数据后出现问题，请再运行一次补丁工具（菜单第 1 项）。补丁工具会检测到 `main.js` 已被打过补丁，只应用 settings workaround。

## ⚠️ Antigravity CLI 许可证错误（#3501）
如果 Antigravity CLI（`agy`）出现 `You do not have a valid license of this product` 错误，这既不是本地补丁的问题，也不是 `Eligibility Check` 界面的问题。

该错误与 Google API 以及用户账号状态有关：许可证、访问权限或 Google 服务端的权限校验。补丁工具只修改 Antigravity / Antigravity CLI 的本地文件，无法为账号授予许可证，也无法改变 Google API 的返回结果，因此对这类错误无能为力。

**错误示例：**
```text
⚠ You do not have a valid license of this product. Please contact your administrator to request a license. If you are
not an enterprise user and believe you are receiving this message as an error, please try using the latest version and
logging in again. (#3501)
Error ID: b2c1d9edcaac4fd5ac5766de06c2253b
Trajectory ID: d3ee4302-4213-40f9-9ac5-42e83e38a5ce
```

## ⚠️ 补丁错误："✗ isGoogleInternal -> true (auth) — pattern not found"

如果在应用补丁（PATCH → `1`：Antigravity IDE patch）时收到以下提示：

```text
✗ isGoogleInternal -> true (auth) — pattern not found
```

这说明补丁工具在它尝试修改的 `main.js` 文件中没有找到预期的 `isGoogleInternal` 模式。

**几乎 100% 的情况下，这是因为补丁工具找到并试图修改了一个与 Antigravity IDE 无关的随机 `main.js` 文件。**

### 解决方案：

1. 在补丁工具的主菜单中查看它识别出的 `main.js` 文件路径（通常在开始打补丁前会输出）。
2. 确认该路径指向真正的 Antigravity IDE 文件，例如：
   - Windows: `%LOCALAPPDATA%\Programs\Antigravity IDE\resources\app\out\main.js`
   - Linux: `/usr/share/antigravity-ide/resources/app/out/main.js`
   - macOS: `/Applications/Antigravity IDE.app/Contents/Resources/app/out/main.js`
3. 如果路径指向了别的文件（例如其他 Electron 应用或脚本当前目录下的 `main.js`），请选择 **TOOLS → `11`（Select custom path）** 并手动指定 Antigravity IDE 文件夹的正确路径。
4. 确认补丁工具的工作目录中没有多余的 `main.js` 文件 —— 如果存在，补丁工具可能会优先选中它（搜索从当前目录开始）。

> **说明：** 如果你从一个存放着其他 `main.js`（例如别的项目的）的目录运行补丁工具，请把脚本移动到其他目录，或通过命令行参数显式指定 Antigravity IDE 的路径：
>
> ```bash
> python main.py "C:\Users\<username>\AppData\Local\Programs\Antigravity IDE"
> ```

## 📚 错误相关的补充资料
若想更深入理解各类 HTTP 错误及其诊断方法，推荐阅读以下指南：
- [5xx Server Errors: The Complete Guide](https://komodor.com/learn/5xx-server-errors-the-complete-guide/) —— 服务端错误的详细解析。

## 🌟 功能特性
- 自动在标准路径和 Windows 注册表中查找已安装的 Antigravity 2.0、Antigravity IDE、Antigravity CLI（`agy`）以及 VS Code 的 Google Antigravity 扩展。
- **更新检查** —— 启动时自动检查新版本，也可通过菜单手动检查（TOOLS → `9`）。
- **Antigravity CLI 补丁** —— 通过字节签名在机器码层面移除「Eligibility Check」界面并绕过 eligibility 校验，适用于 `agy`/`agy.exe` Go 二进制文件的 x86-64 与 ARM64 架构（带备份与回滚）。
- **Antigravity Manager（`language_server`）补丁** —— 通过字节签名在后端编译二进制中移除授权校验（`hasValidAuth=true`），适用于 x86-64 与 ARM64 架构（带备份与回滚）。
- **VS Code 的 Google Antigravity 扩展补丁** —— 在 `google.google-antigravity` 扩展的 `extension.js` 中注入防重复下载二进制的 guard，并关闭 release 渠道变更检测（`isChannelChanged -> false`），使已下载/已打补丁的二进制不被覆写。此外还会用 agy 补丁修补已下载的 `~/.gemini/bin/antigravity` 二进制。
- 支持 Linux：在 `/usr/share/antigravity-ide` 中搜索，通过 `dpkg`、`rpm` 和 `package.json` 识别版本。
- 支持 macOS：在 `/Applications` 和 `~/Applications` 中查找 `.app` 包，修改 `main.js` 后执行 ad-hoc 重新签名。
- 修改前创建备份。
- **POSIX 上的原子化二进制替换** —— Linux/macOS 上的 `agy` 与 `language_server` 通过同目录临时文件（`tempfile.mkstemp`，O_EXCL）加 `os.replace` 写入：正在运行的进程不会阻塞打补丁（不会因二进制被占用而出现 `ETXTBSY` / 「Permission denied」），文件权限得以保留（`+x` 不丢失），并保持原文件的 owner/group；出现任何错误时都会删除临时文件，同时拒绝对符号链接打补丁。通用逻辑见 `source/patcher/utils/atomic.py`。
- 通过简洁的菜单应用与回滚补丁。
- 同时支持 `resources/app/out/main.js` 与 `resources/app/main.js` 两种路径。
- 彩色输出，并尝试自动提权（Windows 上的 UAC，Linux 上提示使用 `sudo`）。
- 应用补丁前检查 Antigravity IDE 的最低版本（>= `2.1.1`）。
- 通过 Windows 注册表、Linux 包管理器或 macOS 上的 `package.json` 识别 Antigravity IDE 版本。
- 检测到已应用过的补丁时，会询问是否重新应用。

## 🚀 使用方法
1. 关闭 Antigravity IDE 或 Antigravity 2.0。
2. 以管理员身份运行补丁工具（必要时脚本会自行请求提权）。
3. 在菜单中选择需要的操作：

| 菜单项 | 说明 |
|---|---|
| **PATCH** | |
| `1` Antigravity IDE patch | 为 Antigravity IDE 的 `main.js` 应用补丁（绕过区域锁） |
| `2` Antigravity 2.0 patch | 为二进制文件 `language_server`（Antigravity Manager）应用补丁 |
| `3` Antigravity CLI (agy) patch | 为二进制 `agy`/`agy.exe` 应用补丁（解锁 agy 工具） |
| `4` Antigravity VS Code Patch | 修补 `google.google-antigravity` 扩展的 `extension.js` 与 `~/.gemini/bin/antigravity` 二进制（需要已安装并已打补丁的 Antigravity 2.0） |
| **RESTORE** | |
| `5` Antigravity IDE | 从备份恢复 Antigravity IDE 的原始 `main.js` |
| `6` Antigravity 2.0 | 从备份恢复原始 `language_server` |
| `7` Antigravity CLI | 从备份恢复原始 `agy`/`agy.exe` |
| `8` Antigravity VS Code extension | 从备份恢复原始 `extension.js`（以及 `~/.gemini/bin` 下的二进制） |
| **TOOLS** | |
| `9` Check for updates | 检查 GitHub 上是否有新版本 |
| `10` Open GitHub repository | 在浏览器中打开项目页面 |
| `11` Select custom path | 手动选择应用目录或文件路径（IDE / 2.0 / CLI / VS Code 扩展） |
| `12` About program | 显示程序与作者信息 |
| **`0` Exit** | 退出补丁工具 |

从源码运行：
```bash
python main.py
```

指定路径运行（适用于 Antigravity IDE、Antigravity 2.0 或 Antigravity CLI）：
```bash
# Windows
python main.py "C:\\Users\\<username>\\AppData\\Local\\Programs\\Antigravity IDE"
python main.py "C:\\Users\\<username>\\AppData\\Local\\Programs\\Antigravity\\resources\\bin\\language_server.exe"
python main.py "C:\\Users\\<username>\\AppData\\Local\\agy\\bin\\agy.exe"

# Linux
python main.py /usr/share/antigravity-ide
python main.py /opt/Antigravity/resources/bin/language_server
python main.py /usr/local/bin/agy

# macOS
python3 main.py /Applications/Antigravity\ IDE.app
python3 main.py /Applications/Antigravity.app
python3 main.py /usr/local/bin/agy
```

如果 `main.js` 或 `language_server` 就在脚本旁边，则无需指定路径 —— 它们会被自动找到。

> **macOS：** 如果 `Antigravity IDE.app` 位于 `/Applications`，写入需要 `sudo`（脚本会主动建议重启提权）。安装在 `~/Applications` 或用户目录时无需 `sudo`。打补丁成功后，`.app` 会自动用 ad-hoc 签名重新签名（`/usr/bin/codesign --force --deep --sign -`）—— 否则启用了 Hardened Runtime 的 Electron 在 macOS 上无法启动。扫描已签名的 Mach-O 文件时采用内存读取（不使用 `mmap`），以免内核在检查已打补丁的二进制时以 CODESIGNING SIGKILL 终止进程。移除 `com.apple.quarantine` 使用系统内置的 `/usr/bin/xattr` 工具 —— 无需额外的 Python 包。

### 🍎 在 macOS 上使用

由于官方发布中没有提供 macOS 的预编译二进制（仅提供 Windows 和 Linux），你可以直接从源码运行补丁工具，或者自行编译可执行文件。

#### 方式一：从源码运行（推荐）
1. 创建虚拟环境、激活并安装所需依赖：
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. 完全退出 Antigravity 2.0 或 Antigravity IDE。
3. 运行补丁工具并指定应用路径：
   ```bash
   # 对应 Antigravity IDE
   python3 main.py "/Applications/Antigravity IDE.app"
   
   # 对应 Antigravity 2.0
   python3 main.py "/Applications/Antigravity.app"
   ```
   *说明：如果应用位于 `/Applications` 目录，脚本会自动请求提权（`sudo`）以便写入。*

#### 方式二：自行编译二进制文件
如果你需要现成的可执行文件，可以按 [🛠️ 编译](#%EF%B8%8F-编译) 一节的说明自行构建。

编译成功后，通过终端运行编译产物：
```bash
cd dist
chmod +x Open_AG_Patcher_macOS
sudo ./Open_AG_Patcher_macOS
```
如果 macOS 阻止运行编译出的文件，请移除 quarantine 属性：
```bash
xattr -dr com.apple.quarantine Open_AG_Patcher_macOS
```

#### 菜单该怎么选
请使用：
- **PATCH → `1`**（Antigravity IDE patch）对应 `Antigravity IDE.app`
- **PATCH → `2`**（Antigravity 2.0 patch）对应 `Antigravity.app`（后端 language_server）
- **PATCH → `3`**（Antigravity CLI (agy) patch）对应 `agy` 二进制（若已安装）
- **PATCH → `4`**（Antigravity VS Code Patch）对应 VS Code 中的 `google.google-antigravity` 扩展
- **RESTORE → `5`**、`6`、`7` 或 `8` 用于从备份恢复

对于 `Antigravity.app`，补丁工具通常能自动找到：
```text
/Applications/Antigravity.app
```
如果自动搜索没有找到应用，请选择 **TOOLS → `11`**（Select custom path）并指定下列路径之一：
```text
/Applications/Antigravity.app
/Applications/Antigravity IDE.app
```

#### 检查签名
打补丁后 `.app` 会自动用 ad-hoc 签名重新签名。可用下面的命令验证：
```bash
codesign -dv /Applications/Antigravity.app 2>&1 | grep Signature
```
预期结果：
```text
Signature=adhoc
```

## ❓ 具体改动了什么

### Antigravity IDE 的补丁

补丁工具会修改 `main.js` 以绕过 `isGoogleInternal` 校验。改动可通过备份文件（`main.js.bak`）回滚。

### `resetIsTierGCPTos(),this.XXX.isGoogleInternal` → `resetIsTierGCPTos(),true`
将授权服务中 `resetIsTierGCPTos()` 调用之后对 `isGoogleInternal` 标志的判断替换为无条件 `true`，从而启用 Google 内部访问路径。应用补丁后会自动清理 VS Code 缓存目录（`CachedData` 与 `Code Cache/js`），强制 IDE 重新编译打过补丁的 JS 代码。


### Antigravity Manager（language_server）的补丁

Antigravity Manager（`language_server` 或 `language_server.exe`）是在 Antigravity 2.0 内部启动的后端服务。默认情况下它要求 Google 服务端的授权与许可证校验通过。

补丁工具通过 `MultiGate` 类，按字节签名直接修改编译后的 `language_server` 二进制，覆盖两种架构：
- **x86-64**（Intel Mac / Windows / Linux x64）：找到并把 `cmp byte ptr [rax + 8], 0` 替换为 `mov byte ptr [rax + 8], 1` 并补 `nop`（`\xc6\x40\x08\x01\x90\x90`）。
- **ARM64**（Linux arm64 / Apple Silicon macOS）：找到并把 `ldrb w3, [x0, #8] ; tbz w3, #0, skip` 指令序列（考虑一条或两条准备指令）替换为 `mov w3, #1 ; strb w3, [x0, #8]`（`\x23\x00\x80\x52\x03\x20\x00\x39`）。

结果是 `hasValidAuth` 的返回值被强制为 `true`，从而解除封锁。
该补丁可通过 **RESTORE → `6`** 从 `.agybak` 恢复原始二进制来回滚。
POSIX 上的写入与 `agy` 同样是原子化的（临时文件 + `os.replace`，保留 `+x` 与所有者），正在运行的 `language_server` 不会阻塞打补丁。

### Antigravity CLI（agy）的补丁

Antigravity CLI 是独立的 Go 二进制（Windows 上为 `agy.exe`，Linux/macOS 上为 `agy`），它会展示装饰性的「Eligibility Check」界面，并根据服务器响应生成「Account ineligible」错误。由于这是编译后的二进制（而非 JS），打补丁是通过唯一字节签名**在机器码层面**完成的，经由 `MultiGate` 覆盖两种架构：**x86-64**（Windows / Linux x64 / Intel Mac）与 **ARM64**（Windows ARM64 / Linux arm64 / Apple Silicon macOS）。

补丁工具只应用**一个 gate** —— 构造错误之前的外层检查会让错误分支变得不可达：

#### Gate 1 —— 「Eligibility Check」界面

##### x86-64
1. 补丁工具扫描二进制，寻找该 gate 检查的唯一签名：
   ```asm
   test rax, rax              ; 48 85 c0            <-- auth 结果 == nil？
   je  eligible               ; 0f 84 xx xx xx xx   <-- 若为 nil → GOOD
   cmp byte ptr [rax+8], 0   ; 80 78 08 00         <-- 检查 eligibility 标志
   jne eligible               ; 0f 85 xx xx xx xx   <-- 若标志 != 0 → GOOD
   call failure_builder       ; e8 xx xx xx xx      <-- BAD：构造错误
   ```
2. 补丁工具把 `cmp byte ptr [rax+8], 0` 替换为 `test rax,rax` + `NOP`（`48 85 c0 90`）。由于此处 `rax` 必然非零，`jne` 跳转总会把执行流导向「eligible」分支。

##### ARM64
1. 在当前的原生 arm64 构建中，构造错误之前的外层检查形如：
   ```asm
   cbnz x1, error            ; xx xx xx b5     <-- 若 x1 != 0 → BAD
   cbz  x0, eligible         ; xx xx xx b4     <-- 若 x0 == 0 → GOOD
   ldrb w1, [x0, #8]        ; 01 20 40 39     <-- 加载 eligibility 标志
   tbnz w1, #0, eligible    ; xx xx xx 37     <-- 若第 0 位 != 0 → GOOD
   bl   failure_builder      ; xx xx xx 97     <-- BAD：构造错误
   ```
2. 补丁工具把标志加载指令 `ldrb w1,[x0,#8]` 替换为 `mov w1,#1`（`21 00 80 52`），因此已有的 `tbnz` 总会选择「eligible」分支。`MultiGate` 会自动选择 x64 或 arm64 签名。统一的严格 ARM64 gate 覆盖了两种已知尾部形态：经典形态（`x0`/`x1`/`x2` → `[sp,#0x90]`/`[sp,#0x60]`/`[sp,#0x80]`）与 macOS 构建形态（`x0`/`x1`/`x2`/`x3` → `[sp,#0x98]`/`[sp,#0x60]`/`[sp,#0x88]`/`[sp,#0x58]`）。从 CLI 1.2.7 起，该检查被重新编译为不含外层 `cbnz` 的形式（`cbz x0` → `ldrb w4,[x0,#8]` → `tbnz w4,#0` → `ldp x4,x5,[x0,#0x48]`）—— 由独立的 gate `eligibility screen off (arm64, w4)` 覆盖，修复字节为 `mov w4,#1`（`24 00 80 52`）。此外界面函数中还有一处内联检查（`cbnz x1` → `cbz x0` → `ldrb w2,[x0,#8]` → `tbnz w2,#0` → `bl`）—— 由 gate `eligibility screen off (arm64, w2)` 覆盖，修复字节为 `mov w2,#1`（`22 00 80 52`）；缺少它的话，即使 w4 已被修补，`Eligibility check failed:` 界面依然会出现。`MultiGate` 会收集**所有**子 gate 的匹配结果（`resolve_all`）—— 在 1.2.7 中两处都会被修补。与最新构建的兼容性由测试 `test-agy/test_cli_releases.py` 自动验证，它会下载最新发布中的所有压缩包。

#### 通用步骤
3. 写入前会创建备份 `agy.exe.agybak`（POSIX 上为 `agy.agybak`）。如果已有备份已过期（应用自动更新过），它会被自动刷新 —— 不会保留过期副本。
4. 在 Linux/macOS 上写入是原子化的：新字节先写入同目录下的临时文件（`tempfile.mkstemp`，O_EXCL），`fsync` 之后通过 `os.replace` 覆盖目标文件，并保留原文件的权限、所有者和用户组。正在运行的 `agy` 不会干扰打补丁 —— 内核会继续执行旧 inode，后续启动则会使用新二进制。Windows 上则直接写入文件。
5. 在 macOS 上，修改完成后二进制会被重新 ad-hoc 签名（与 `.app` 的处理一致）。

**补丁安全性：**
- 如果在二进制中找不到字节签名（未知/不受支持的版本），补丁工具会**拒绝打补丁**且不做任何修改 —— 并输出「signature not found (unsupported version?)」。
- 写入前每个补丁都会被校验：偏移量非负、补丁不越界、且不改变文件大小。
- 禁止对符号链接打补丁：目标必须是普通文件，否则补丁工具会拒绝写入。
- 如果签名出现多次（Go 可能把同一函数编译出多个副本），补丁工具会对**所有**匹配位置应用修复 —— 它们在机器码层面是完全一致的。
- 回滚通过 **RESTORE → `7`**（Antigravity CLI）从 `.agybak` 恢复完成。

> **平台说明：** x86-64 的签名已在 Windows 与 Intel macOS 上验证，ARM64 的签名已在 Apple Silicon macOS 上验证。Discovery 以跨平台方式查找二进制（`PATH`、Windows 上的 scoop，POSIX 上的 `/usr/local/bin`、`/opt/antigravity/bin`、`~/.local/bin`）。在 Linux 上 `agy` 二进制的编译方式可能不同，签名可能匹配不上 —— 这种情况下补丁工具会如实报告，并且不修改文件。

### VS Code 的 Google Antigravity 扩展补丁

> **⚠️ 重要：** 要正确修补 VS Code 扩展（`PATCH → 4`），需要已安装并且已经打过补丁的 Antigravity 2.0（`PATCH → 2` —— `language_server` 补丁）。请先安装 Antigravity 2.0，对它应用补丁，然后再去修补 VS Code 中的 `google.google-antigravity` 扩展。

VS Code 的 `google.google-antigravity` 扩展每次启动时都会检查后端二进制的版本，并从 Google 的 release 服务器重新下载。补丁工具会对扩展的 `extension.js` 做两处修改：

#### Part 1 —— 防重复下载的 guard

在 `outputChannel.appendLine('[INSTALL] Checking Antigravity releases...')` 这一行之后注入一段代码，用于检查是否已经存在下载好的二进制（通过 `targetPathOverride` 或在 `~/.gemini/bin` 中），如果找到就**立即返回它的路径**，跳过版本检查与重新下载：

```js
{const __primary=options.targetPathOverride||getInstalledTargetPath();
const __candidates=[__primary,
(0,path_1.join)((0,path_1.dirname)(__primary),'antigravity'+((0,path_1.extname)(__primary)||''))];
for(const __p of __candidates){if(__p&&await pathExists(__p)){
outputChannel.appendLine('[INSTALL] Existing binary found at '+__p+'. Skipping version check and re-download.');return __p;}}}
```

插入点通过灵活的正则查找，它会匹配 `outputChannel.appendLine('...');` 的**完整调用** —— 兼容不同引号与空格，但严格止于该调用的右括号，以确保注入内容落在它之后而不是内部。

#### Part 2 —— 关闭 release 渠道变更检测

```js
// 原来：
const isChannelChanged = manifestFetched && lastInstalledUrl !== releaseBaseUrl;
// 改为：
const isChannelChanged = false;
```

没有这一步，扩展会认为 release 渠道已变更，从而强制重新下载二进制，覆盖掉已打补丁的版本。

#### 补充 —— 修补已下载的二进制

修补 `extension.js` 之后，补丁工具会立即询问是否对扩展下载的二进制 `~/.gemini/bin/antigravity`（或 `~/.gemini/bin/agy`）应用 agy 补丁（见上文）—— 它包含同样的 eligibility 检查。

**细节：**
- 备份：原文件旁的 `extension.js.vscodebak`；过期备份会自动更新。
- 通过检测注入代码与 `const isChannelChanged = false;` 的存在来判断是否已打过补丁。
- 回滚：**RESTORE → `8`** 会从 `.vscodebak` 恢复 `extension.js`，同时询问是否从 `.agybak` 恢复 `~/.gemini/bin` 下的二进制。
- 打补丁后需要重新加载 VS Code 窗口（**Developer: Reload Window**）。
- 扩展搜索路径：`~/.vscode/extensions`、`~/.vscode-insiders/extensions`、`~/.vscode-oss/extensions`、`~/.vscode-server/extensions`、`~/.vscode-server-insiders/extensions`（或环境变量 `VSCODE_EXTENSIONS` 指定的目录）。存在多个版本时，按 mtime 选择最新的。

## 🔍 文件查找逻辑

补丁工具按以下顺序查找 `main.js`：

1. 命令行参数（目录路径，或直接指向 `main.js`）。
2. 当前目录（`./main.js`）。
3. 按标准路径自动搜索：
   - **Windows:**
     - `%LOCALAPPDATA%\Programs\Antigravity IDE`
   - **Linux:**
     - `/usr/share/antigravity-ide`
     - `/opt/Antigravity IDE`
     - `/opt/Antigravity IDE/resources/app/out`
   - **macOS:**
     - `/Applications/Antigravity IDE.app/Contents/Resources/app`
     - `~/Applications/Antigravity IDE.app/Contents/Resources/app`
4. Windows 注册表（`HKCU` 与 `HKLM` 下的键 `{AA73B3E3-C6C8-45C8-B1DC-4AE56C751432}_is1`：`SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\`）。

在找到的目录内会检查以下路径：
- `resources/app/out/main.js`
- `resources/app/main.js`
- `out/main.js` (macOS)
- `main.js`（如果直接指定了路径）

在 macOS 上脚本也可以直接接受 `.app` 包的路径 —— `Contents/Resources/app/out/main.js` 会被自动解析。

### 查找 Antigravity CLI（`agy`）

`agy` 二进制（Windows 上为 `agy.exe`）以与安装位置无关的方式查找 —— 通过 `PATH` 与标准目录，不写死路径/版本：

1. 命令行参数，或 **TOOLS → `11` → `3`**（指向 `agy`/`agy.exe` 文件或其所在文件夹）。
2. `PATH` (`shutil.which("agy")`).
3. 标准目录：
   - **Windows：** `%LOCALAPPDATA%`、`%PROGRAMFILES%`、`%PROGRAMFILES(X86)%`、`%ProgramData%`、`%APPDATA%`（以及其中的 `Programs` 子目录）、scoop（`%USERPROFILE%\scoop\apps`、`%SCOOP%\apps`）。匹配模式：`agy/bin/agy.exe`、`agy/*/bin/agy.exe`（scoop 的版本目录）、`agy*/agy.exe`。
   - **Linux/macOS:** `/usr/local/bin`, `/usr/bin`, `/opt/antigravity/bin`, `/opt/antigravity`, `~/.local/bin`, `~/bin`.

如果找到多份副本（例如 scoop 中存在多个版本），会按 mtime 选择最新的一份。

### 查找 Google Antigravity 扩展（VS Code）

`google.google-antigravity` 扩展的 `extension.js` 会在以下目录中查找（最优先的是通过环境变量 `VSCODE_EXTENSIONS` 指定的覆盖路径）：

1. 命令行参数，或 **TOOLS → `11` → `4`**（指向 `extension.js`、`google.google-antigravity-*` 扩展目录，或 `extensions` 根目录）。
2. `~/.vscode/extensions`
3. `~/.vscode-insiders/extensions`
4. `~/.vscode-oss/extensions`
5. `~/.vscode-server/extensions`（远程服务器）
6. `~/.vscode-server-insiders/extensions`

在扩展目录内按 `google.google-antigravity-*` 模式查找文件夹；存在多个版本时按 mtime 选择最新的。预期文件是扩展目录根下的 `extension.js`。

### 查找 `~/.gemini/bin` 下的二进制

扩展下载的二进制（仅 **PATCH → `4`** 使用）在 `~/.gemini/bin` 中查找：Windows 上为 `antigravity.exe`/`agy.exe`，POSIX 上为 `antigravity`/`agy`。如果那里没有二进制，而扩展又从未运行过 —— 补丁工具会提示你先在 VS Code 里运行一次扩展，让它下载二进制。

## 🔎 Antigravity IDE 版本识别

| 平台 | 版本识别方式 |
|---|---|
| **Windows** | 注册表：键 `{AA73B3E3-...}_is1` 中的 `DisplayVersion` |
| **Linux (deb)** | `dpkg-query -W antigravity-ide` |
| **Linux (rpm)** | `rpm -q --queryformat %{VERSION} antigravity-ide` |
| **Linux（portable/snap/flatpak）** | `main.js` 旁的 `package.json` |
| **macOS** | `Antigravity IDE.app/Contents/Resources/app/` 中的 `package.json` |

如果版本无法识别，补丁工具会询问是否跳过检查继续。如果版本低于 `2.1.1` —— 会给出警告并同样让你选择。

## 🔒 已打补丁检测

打补丁前，脚本会通过两个特征检查文件是否已被修补过：
- 不存在 `if(this.X.isGoogleInternal)`（该模式已被替换为 `if(true)`）
- 不存在未修改的 `isGoogleInternal`（基于逗号的 auth 检查）。

## 🛡️ 权限提升

- **Windows**：通过 `ShellExecuteW` 带 `runas` 参数自动发起 UAC 请求。能正确处理含空格的路径。
- **Linux**：如果脚本不是以 root 运行，会建议通过 `sudo` 重启（`os.execvp`）。若拒绝则继续运行，并警告可能出现写入错误。此时运行时 workaround 会写入原始用户的 `settings.json`（`SUDO_USER`/`SUDO_UID`），而不是 `/root/.config/...`。
- **macOS**：复用同一套 posix 逻辑 —— 非 root 运行时会提示 `sudo`。对于 `~/Applications/Antigravity IDE.app`，`sudo` 提示可以回答「n」（该目录本就可写）；对于 `/Applications/Antigravity IDE.app` 则应同意。通过 `sudo` 运行时，用户的 `settings.json` 同样取自原始用户的 home 目录，而不是 `root`。

## 🍎 macOS 相关特性

### 打补丁后重新签名 `.app`

对已签名的 `.app` 包内任何文件的修改都会破坏 code signature。启用了 Hardened Runtime 的 Electron 应用（Antigravity IDE 就是其中之一）此后在 macOS 上**无法启动** —— 甚至在 Gatekeeper 向用户弹出对话框之前就失败了。

为了让 `.app` 继续可用，脚本会在 `do_patch` 与 `do_restore` 之后自动执行：

```bash
codesign --force --deep --sign - /path/to/Antigravity\ IDE.app
xattr -dr com.apple.quarantine /path/to/Antigravity\ IDE.app
```

`--sign -` 表示 ad-hoc 签名（无需 Developer ID）。对于本地运行应用来说已经足够，不需要公证（Notarization）。

需要已安装 `codesign` —— 它随 **Xcode Command Line Tools** 一起提供：
```bash
xcode-select --install
```

### 打补丁时出现 "Operation not permitted" 错误

如果你遇到错误 `[!] Backup error: [Errno 1] Operation not permitted: '/Applications/Antigravity IDE.app/Contents/Resources/app/out/main.js.bak'`：

1. 为终端授予完全磁盘访问权限：**系统设置 → 隐私与安全性 → 完全磁盘访问权限**（System Settings → Privacy & Security → Full Disk Access）。
2. 用下面的命令移除应用的隔离属性：
   ```bash
   sudo xattr -rd com.apple.quarantine /path/to/Antigravity\ IDE.app
   ```

### 如果打补丁后应用无法启动

1. 确认 `codesign` 可用：`which codesign`。
2. 确认 `.app` 已被重新签名：`codesign -dv /Applications/Antigravity\ IDE.app 2>&1 | grep Authority` —— 应当显示 `Signature=adhoc`。
3. 如果 macOS 仍然拦截：进入 `系统设置 → 隐私与安全性` —— 底部会出现「仍要打开」按钮。

## ⚙️ 环境要求

- **Python** 3.x
- **依赖**：`packaging`（用于版本比较）
- **操作系统**：
  - **Windows** —— 完整支持通过注册表自动搜索与 UAC 提权。
  - **Linux** —— 在 `/usr/share/antigravity-ide` 中自动搜索，通过 `dpkg`/`rpm`/`package.json` 识别版本，支持 sudo 提权。
  - **macOS** —— 在 `/Applications/Antigravity IDE.app` 与 `~/Applications/Antigravity IDE.app` 中自动搜索，通过 `package.json` 识别版本，使用 `codesign` 进行 ad-hoc 重新签名（需要 Xcode Command Line Tools）。
- **Antigravity 2.0 最低版本**：`2.5.0`
- **Antigravity IDE 最低版本**：`2.1.1`
- **支持的版本**：Antigravity 2.0 为 `2.3.0` 及以上，IDE 为 `2.1.1` 及以上

## 🛠️ 编译

编译可执行文件时建议使用虚拟环境：

1. **创建并激活虚拟环境：**
   * **Windows:**
     ```bash
     cd source
     python -m venv .venv
     .venv\Scripts\activate
     ```
   * **Linux / macOS:**
     ```bash
     cd source
     python3 -m venv .venv
     source .venv/bin/activate
     ```

2. **安装依赖：**
   ```bash
   pip install -r requirements.txt
   ```

3. **通过 PyInstaller 编译：**
   * **Windows:**
     ```bash
     pyinstaller --onefile --uac-admin --icon=icon.ico --name="Open_AG_Patcher_Windows" --noupx --clean --version-file=version.txt main.py
     ```
   * **Linux:**
     ```bash
     pyinstaller --onefile --icon=icon.ico --name="Open_AG_Patcher_Linux" --hidden-import=packaging --hidden-import=packaging.version --hidden-import=packaging.specifiers --hidden-import=packaging.requirements main.py
     ```
   * **macOS (Universal2):**
     ```bash
     pyinstaller --onefile --name="Open_AG_Patcher_macOS" --target-arch universal2 --hidden-import=packaging --hidden-import=packaging.version --hidden-import=packaging.specifiers --hidden-import=packaging.requirements main.py
     ```

## 项目结构

- `source/main.py` —— 补丁工具的主入口（负责权限检查并启动 CLI）。
- `source/patcher/` —— 补丁工具的核心源码，采用模块化架构：
  - `constants.py` —— 全局常量、正则表达式、版本号。
  - `cli.py` —— 控制台用户界面、菜单与输入处理。
  - `utils/` —— 系统辅助工具（控制台颜色、管理员权限、POSIX 权限、文件哈希、二进制原子替换 `atomic.py`）。
  - `ide/` —— 直接针对 Antigravity IDE（`main.js` 文件）的查找与打补丁逻辑。
  - `agy/` —— Antigravity CLI 二进制（`agy`/`agy.exe`）的查找与字节签名打补丁逻辑。
  - `manager/` —— Antigravity Manager 二进制（`language_server`/`language_server.exe`）的查找与字节签名打补丁逻辑。
  - `vscode/` —— VS Code 的 `google.google-antigravity` 扩展（`extension.js`）及其下载的 `~/.gemini/bin` 二进制的查找与打补丁逻辑。
- `source/requirements.txt` —— 编译与运行所需的依赖。
- `source/build.txt` —— 针对不同操作系统的编译命令示例。
- `source/icon.ico` —— 用于 `exe`/`app` 的图标。

# 📜 许可证与署名

本项目基于 GPL-3.0 许可证发布。许可证全文见 [`LICENSE`](LICENSE) 文件。

- **原作者**：AvenCores（GitHub 账号 @AvenCores 与原仓库 `AvenCores/open-antigravity-patcher` 均已无法访问）
- **现存参考副本**：[trustybird/AvenCores-open-antigravity-patcher](https://github.com/trustybird/AvenCores-open-antigravity-patcher)（非官方镜像，保留了原始代码与 LICENSE）
- **中文汉化**：iosmers —— [iosmers/open-antigravity-patcher-zh](https://github.com/iosmers/open-antigravity-patcher-zh)

本汉化版是对上游项目的非官方中文翻译，**未修改任何补丁逻辑**，仅翻译界面文案与文档，并因上游仓库失效而同步调整了更新检查与链接指向。依据 GPL-3.0，本仓库同样以 GPL-3.0 发布，并保留原作者的版权与署名（见 [`LICENSE`](LICENSE)）。

本项目的部分改动与实现方案参考了仓库 [eligibility-antigravity-patcher](https://github.com/QNIX-Dev/eligibility-antigravity-patcher)（MIT 许可证）的成果。所有集成与修改均保留了原作者版权并注明了出处。

---
# 💰 支持作者
+ **SBER**: `2202 2050 1464 4675`
