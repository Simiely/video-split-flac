# AGENTS.md · 项目规则（AI 工作流指令）

> 📌 **文档基线**：2026-11-18（commit `2c283b2`）接入 repo-kit 机器层（link-only / 规范 2.1.4）
> **更新文档/代码后，请更新此行**（日期 + 新 commit hash），并在 CHANGELOG 追加版本

## 🖥️ 新电脑 / 跨机器使用（clone 后必读）

仓库**不含**：模型（models/ 已 gitignore）、Cookie（cookies.txt 已 gitignore）、本机工具路径、代理。换电脑后必须自己补齐：

1. **装依赖**：Python 3.13+、ffmpeg（portable 解压即可）、yt-dlp（`pip install -U yt-dlp`）、node 18+
2. **配环境变量**：`FFMPEG_PATH` / `YTDLP_PATH` / `NODE_PATH` 指向新机器工具路径（或加入 PATH）
3. **装 Python 包**：`pip install faster-whisper mutagen opencc-python-reimplemented`
4. **下载模型**：`python bili_split.py fetch-model --name small`（国内镜像加速）
5. **自测**：`python bili_split.py selftest --model models/faster-whisper-small`

**跨机器差异（重要）**：

| 本机有 | 新机器没有 | 影响与处理 |
|---|---|---|
| 代理 `127.0.0.1:7890` | 无代理 | **YouTube 下载失败**。需自备代理，用 `--proxy <你的代理>` 覆盖 |
| `cookies.txt`（登录态） | 无 Cookie | YouTube 降级匿名下载（360p/44k 音质），功能可用；要高音质需重新提供 cookie 并 `import-cookies` |
| 已下载模型 | 无模型 | 必须执行 `fetch-model`，否则 split 报模型错误 |
| B 站 | — | **B 站全程不需要代理/Cookie**，新机器直接可用 |


> **完整的 9 步执行顺序（含每步命令与验收）见 @rules/端到端工作流.md** —— 需要跑全流程时读那一份。
## 技术栈（精确版本）

- Python 3.13.12（推荐 WorkBuddy managed venv；`FFMPEG_PATH`/`YTDLP_PATH`/`NODE_PATH` 环境变量可指向本机工具）
- yt-dlp 2026.07.04（需 node JS runtime + ffmpeg 位置）
- ffmpeg 9.0.1（portable 构建，`--ffmpeg` 参数或 PATH 均可）
- faster-whisper 1.2.1（ctranslate2 4.8.1，CPU int8）
- mutagen 1.48.1（FLAC 标签写入）
- opencc-python-reimplemented（繁转简，split 自动转换）
- node 22.22.2（yt-dlp 的 JS 挑战解算 runtime）

## 关键坑（必须遵守）

- **Whisper 模型下载**：huggingface_hub 自动下载必失败（hf-mirror HEAD 302 触发保护）。用 `fetch-model` 子命令下载到 `models/` 本地目录，`--model` 传**本地目录路径**。
- **YouTube client 策略**：匿名用 `android`（稳定，360p/44k）；有 cookie 时自动 `tv`（1080p/128k，偶发限流 → 自动降级 `web` 再 `android`）。android client **不支持 cookie**。
- **官方字幕优先**：`--subs-lang zh-Hant`（android client 免 PO token 可下）。zh-CN 轨道是拼音，zh-Hant 是汉字（转简体用）。
- **网易云歌词兼容**：`LYRICS` 内容必须是**标准 LRC 完整头**（`[ti:歌名]`+`[ar:]`+`[al:]`+时间戳行），缺头网易云不认（参考 MusicTag 写入格式）。
- **VAD 默认关闭**：`vad_filter=True` 会把音乐/歌曲当噪声滤成 0 字。讲课类可 `--vad`。
- **结尾空白（--tail-pad）**：默认每段成品 FLAC 结尾追加 3 秒静音（`apad=pad_dur`），只作用于成品；whisper 转写走 `cut_wav16` 不加，歌词时间戳不变。想精确截止设 `--tail-pad 0`。
- **FLAC 歌词字段大写**：`LYRICS` + `UNSYNCEDLYRICS` 用 **mutagen** 写；ffmpeg `-metadata lyrics=` 写小写不认。
- **Windows 沙箱**：`os.remove`/`shutil.copy2` 对 git 跟踪文件可能被钩子静默拦截——批量文件操作用提权执行或 try/except 降级。
- **本机网络**：境外流量代理 `127.0.0.1:7890`；GitHub API 用 node fetch 直连（不用 curl/git）；curl/git 子进程访问境外常被 Clash 分流拦成 000/断连。

## 约定

- 注释用中文；输出文件 UTF-8 编码
- 敏感文件（`cookies.txt` / `youtube_cookies.json`）**绝不入库**，已 .gitignore
- 交付物 = `NN_主题.flac`；中间产物（`temp/`、`seg_XX.txt/lrc`）留在输出目录
- 上传的歌曲子文件夹命名 = 视频 ID

## 机器层（repo-kit · link-only）

- `schema/taxonomy.json` + `schema/kit.lock.json`（kit `2.9.0` / 规范 `2.1.4` / `link-only`）+ `tools/repo-kit/check_repo.py`
- 校验：`python tools/repo-kit/check_repo.py --root .`；锁哈希：`pwsh tools/update-repo-kit.ps1 -Check`
- 只查**链接与锚点**：全仓 md 豁免 frontmatter（本仓没有 frontmatter 契约）
- `schema/kit.lock.json` **不要手改**，升级只能跑 `tools/update-repo-kit.ps1`

## 常用命令

```bash
# 转写（核心，字幕优先）
python bili_split.py split --url <链接> --cuts "0:00-12:34, ..." --model models/faster-whisper-small --subs-lang zh-Hant --out ./output

# 应用主题 + 嵌歌词
python bili_split.py apply --out ./output

# 模型 / cookie / 自测
python bili_split.py fetch-model --name small
python bili_split.py import-cookies --input cookies.json
python bili_split.py selftest --model models/faster-whisper-small
```

## 详细规则（按需 @引用）

- 单项目文档规范：见 knowledge-base `模板库/单项目规范/README.md`
- 歌曲库结构：见 `songs/README.md`（总索引）
- **端到端工作流（9 步）**：@rules/端到端工作流.md
