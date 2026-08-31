# AGENTS.md · 项目规则

> 📌 **文档基线**：2026-08-31（commit `a1772df`）完成四件套重写
> **更新文档/代码后，请更新此行**（日期 + 新 commit hash），并在 CHANGELOG 追加版本

## 技术栈（精确版本）

- Python 3.13.12（推荐 WorkBuddy managed venv；`FFMPEG_PATH`/`YTDLP_PATH`/`NODE_PATH` 环境变量可指向本机工具）
- yt-dlp 2026.07.04（需 node JS runtime + ffmpeg 位置）
- ffmpeg 9.0.1（portable 构建，`--ffmpeg` 参数或 PATH 均可）
- faster-whisper 1.2.1（ctranslate2 4.8.1，CPU int8）
- mutagen 1.48.1（FLAC 标签写入）
- node 22.22.2（yt-dlp 的 JS 挑战解算 runtime）

## 关键坑（必须遵守）

- **Whisper 模型下载**：huggingface_hub 自动下载必失败（hf-mirror HEAD 302 触发保护）。用 `fetch-model` 子命令下载到 `models/` 本地目录，`--model` 传**本地目录路径**。
- **YouTube client 策略**：匿名用 `android`（稳定，360p/44k）；有 cookie 时自动 `tv`（1080p/128k，偶发限流 → 自动降级 `web` 重试）。`--yt-client` 可覆盖。android client **不支持 cookie**（yt-dlp 自动跳过）。
- **VAD 默认关闭**：`vad_filter=True` 会把音乐/歌曲当噪声滤成 0 字。讲课类可 `--vad`。
- **FLAC 歌词字段必须大写**：`LYRICS`（LRC 同步歌词）+ `UNSYNCEDLYRICS`（纯文本），用 **mutagen** 写；ffmpeg `-metadata lyrics=` 写小写，多数播放器不认。
- **Windows 沙箱删文件**：`os.remove` 在沙箱下会被安全钩子拦截（回收站不可用抛 OSError）——脚本内已 try/except 降级，勿改回裸 `os.remove`。
- **本机网络**：境外流量需代理 `127.0.0.1:7890`；yt-dlp 的 GitHub API 操作用 node fetch 直连，不用 curl/git。

## 约定

- 注释用中文；输出文件 UTF-8 编码
- 敏感文件（`cookies.txt` / `youtube_cookies.json`）**绝不入库**，已 .gitignore
- 中间产物（`temp/`、`seg_XX.txt/lrc`）保留在输出目录，交付物为 `NN_主题.flac`

## 常用命令

```bash
# 转写（核心）
python bili_split.py split --url <链接> --cuts "0:00-12:34, ..." --model models/faster-whisper-small --out ./output

# 应用主题 + 嵌歌词
python bili_split.py apply --out ./output

# 模型 / cookie / 自测
python bili_split.py fetch-model --name small
python bili_split.py import-cookies --input cookies.json
python bili_split.py selftest --model models/faster-whisper-small
```

## 详细规则（按需 @引用）

- 单项目文档规范：见 knowledge-base `模板库/单项目规范/README.md`
