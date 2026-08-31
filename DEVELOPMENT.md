# DEVELOPMENT.md · 开发文档

## 一、项目概览

**目标**：一条命令把 B站/YouTube 视频按用户时间戳切成多个音频段（FLAC），自动转写歌词，把 LRC 同步歌词嵌入文件，按歌词主题命名。

**核心价值**：把"下载 → 切段 → 转歌词 → 嵌标签 → 命名"五步机械流程沉淀成可复用脚本，用户只需给链接 + 时间戳。

## 二、架构说明

两阶段设计（机械化 / 智能化分离）：

```
split（阶段一：全自动机械化）
  链接 + 时间戳 + 模型
    ├─ yt-dlp 下载最佳音轨（站点识别：bilibili/youtube）
    │    └─ YouTube：自动代理 + player client 策略 + cookie
    ├─ ffmpeg 解码为 wav（原采样率 + 16k mono 双份）
    ├─ 按时间戳精确切割（-ss/-to 放 -i 前，采样级精确）
    │    ├─ seg_XX.flac（最终交付，原采样率）
    │    └─ seg_XX_w16.wav（whisper 专用 16k）
    └─ faster-whisper 逐段转写（保留每句时间戳）
         ├─ seg_XX.txt（纯文本歌词）
         └─ seg_XX.lrc（LRC 同步歌词 [mm:ss.xx]）
    产出: cuts.json + themes.json（主题待填模板）

apply（阶段二：人类/AI 填主题后执行）
  themes.json（每段 theme 4-8 字）
    ├─ ffmpeg -c copy 拷贝改名 → NN_主题.flac（不动音频流）
    └─ mutagen 写标签（embedded）：
         LYRICS = LRC 同步歌词（滚动）
         UNSYNCEDLYRICS = 纯文本（静态兼容）
         TITLE/ARTIST/COMMENT
```

**子命令**：`split` / `apply` / `fetch-model` / `import-cookies` / `selftest`

**关键函数**：`detect_site`（站点识别）、`ytdlp_base`（统一 yt-dlp 参数注入）、`build_dl_cmd`（含降级重试）、`build_lrc`（时间戳→LRC）、`write_flac_tags`（mutagen 标签写入）。

## 三、关键问题与方案

### 问题：huggingface_hub 自动下载 Whisper 模型失败

**TL;DR**：hf-mirror HEAD 请求 302 到 huggingface.co 触发 `FileMetadataError` 保护，代理同样失败；改为手动下载本地目录加载。

- 问题：`WhisperModel("small")` 首次下载必挂
- 根因：huggingface_hub 1.29 对跨域重定向的 HEAD 校验（`Distant resource does not seem to be on huggingface.co`）
- 解决：`fetch-model` 用 urllib 手动下载 4 个文件（config/model.bin/tokenizer/vocabulary）到 `models/faster-whisper-<name>`，`WhisperModel(本地目录)` 直接加载；大文件走 hf-mirror 直连，小文件走 hf.co 代理兜底
- 预防：模型路径永远传本地目录，不要依赖 hub 在线下载

### 问题：YouTube 下载 403 / 限流（代理 IP）

**TL;DR**：web client 匿名 403，android 稳定但低清，tv+cookie 高音质但间歇限流 → 分 client 策略 + 自动降级。

- 问题：`HTTP Error 403: Forbidden`（web client）与 `The page needs to be reloaded`（tv client 限流）
- 根因：数据中心/代理 IP 触发 YouTube bot 检测；不同 player_client 权限与稳定性不同
- 解决：默认 `android`（免 cookie 稳定）；有 cookie 自动 `tv`（解锁 1080p/128k），下载失败 try/except 自动降级 `web` 重试；`--yt-client` 手动覆盖
- 补充：android client 不支持 cookie（yt-dlp 直接跳过）；`--js-runtimes node:...` 必须注入（新版 yt-dlp 解混淆依赖）
- 预防：client 组合变更先跑 `--skip-download --list-formats` 验证

### 问题：VAD 把音乐过滤成 0 字

**TL;DR**：`vad_filter=True` 将歌曲当噪声滤除，转写为空；默认关闭。

- 问题：歌曲转写 0 字，关闭 VAD 后正常出 786 字
- 根因：Silero VAD 对带伴奏人声的误判
- 解决：默认 `vad_filter=False`，`--vad` 参数可选开启（讲课类）
- 预防：转写为空先怀疑 VAD

### 问题：ffmpeg 写歌词标签播放器不认

**TL;DR**：`-metadata lyrics=` 写入小写 `lyrics`，FLAC 事实标准是大写 `LYRICS`；改用 mutagen 双写。

- 问题：foobar2000 等不显示歌词
- 根因：FLAC Vorbis Comment 无官方歌词字段，事实标准 `LYRICS`（foobar2000/MusicBee/Picard 阵营）与 `UNSYNCEDLYRICS`（Mp3tag/Bandcamp 阵营）；ffmpeg 写小写两边都不认
- 解决：mutagen 写 `LYRICS`（LRC 同步歌词）+ `UNSYNCEDLYRICS`（纯文本）双写，字段大写
- 预防：参考 MusicBrainz Picard vorbis.py "read both but always write LYRICS"

### 问题：Windows 沙箱拦截 os.remove

**TL;DR**：sandbox 的 safe-delete 钩子拦截删除走回收站，回收站不可用抛 OSError 中断流程。

- 问题：apply 处理第一段后中断
- 根因：`os.remove` / `shutil.rmtree` 被 sitecustomize shim 包装（回收站不可用）
- 解决：`os.remove` 包 try/except 降级（保留中间文件，日志提示手动删）
- 预防：不在脚本里做"删除"作为主流程依赖

## 四、变更动作清单

- 改功能 → 更新本文件对应章节
- 踩坑解决 → 三、节追加一篇
- 发版 → README + CHANGELOG
- 约定/坑变化 → AGENTS.md 更新
