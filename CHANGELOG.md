# CHANGELOG.md

## [0.2.0] - 2026-08-31

工作流文档化 + 歌曲库按视频分目录。

### 新增
- AGENTS.md 写全 AI 端到端工作流（4 步：给网址 → 收链接时间戳 → split/apply → 上传 songs/<视频ID>/）
- README 新增「完整使用流程」章节（输入模板页 / YouTube / B站 三个网址）+ 歌曲库目录结构
- songs/ 按视频 ID 分子文件夹（songs/<视频ID>/），含总索引 README
- split 新增 --subs-lang（YouTube 官方字幕优先，zh-Hant → 简体，失败回退 Whisper）
- 歌词繁转简（OpenCC t2s，split 自动）

### 修复
- 网易云歌词：LYRICS 重建标准 LRC 头 [ti:][ar:][al:]（对照 MusicTag 格式）
- 歌名校准为经典儿歌标准名（老麦克唐纳有个农场/小金鱼/头肩膀膝盖脚趾等）

## [0.1.3] - 2026-08-31

- LYRICS 写入改为标准 LRC 完整头 [ti:][ar:][al:]（网易云音乐兼容，参考 MusicTag v1.0.9 写入格式）
- build_lrc 支持 artist/album 头；新增 rebuild_lrc_header
- songs/ 新增儿歌合集 23 首（flac + 同名 .lrc + 频道头像封面 + 复现命令 README）

## [0.1.2] - 2026-08-31

输入模板页优化：分段时间拆成 时/分/秒 三个输入框（秒支持小数），免手动敲冒号；同步部署 GitHub Pages。
## [0.1.1] - 2026-08-31

文档完善：环境准备与故障排查。

### 新增
- README 新增「环境准备」章节：4 个外部工具（Python/ffmpeg/yt-dlp/node）的获取方式、路径查找顺序（参数 → 环境变量 → PATH）、Windows 注意事项
- README 新增「拉下来运行不成功？排查清单」：覆盖缺工具、模型下载失败、YouTube 403/限流、转写为空、播放器不显示歌词等 9 类问题
- CHANGELOG 按版本分节维护

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
