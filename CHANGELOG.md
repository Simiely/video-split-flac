# CHANGELOG.md

## [0.1.0] - 2026-08-31

首个可交付版本。B站/YouTube 视频分段 → FLAC + Whisper 歌词 + LRC 滚动歌词嵌入 + 主题命名。

### 新增
- `split`：下载（B站/YouTube 自动识别）→ 时间戳精确切段 → faster-whisper 转写（含每句时间戳）
  - YouTube 自动代理（127.0.0.1:7890）、player client 策略（android/tv/web + 自动降级）
  - 输出 seg_XX.flac / seg_XX.txt / seg_XX.lrc / cuts.json / themes.json
- `apply`：主题重命名（NN_主题.flac）+ mutagen 嵌入标签
  - `LYRICS` = LRC 同步歌词（滚动）、`UNSYNCEDLYRICS` = 纯文本、`TITLE`/`ARTIST`/`COMMENT`
- `fetch-model`：国内镜像下载 Whisper 模型（本地目录加载）
- `import-cookies`：EditThisCookie JSON → yt-dlp cookies.txt（.youtube.com / .bilibili.com 域）
- `selftest`：离线自测工具链
- `input_template.html`：可视化输入助手（链接 + 动态分段 + 命令生成）
- 文档四件套：README / AGENTS / DEVELOPMENT / CHANGELOG

### 修复
- VAD 过滤音乐 → 默认关闭，`--vad` 可选
- ffmpeg 歌词小写标签 → mutagen 大写 `LYRICS` + `UNSYNCEDLYRICS` 双写
- 沙箱 os.remove 中断 → try/except 降级
- cmd_split 切割调用多包 run() → 修正
