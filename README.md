# video-split-flac · 视频分段 → FLAC + 滚动歌词

> B站 / YouTube 视频按**时间戳分段**，每段转 **FLAC**，用 **Whisper 自动转写歌词**并**嵌入同步滚动歌词（LRC）**，再按歌词内容**提炼主题命名**。

## 功能

- ✅ 支持 B 站（URL / BV 号）与 YouTube（watch / shorts / youtu.be）
- ✅ 按时间戳精确分段（`0:00-12:34, 12:34-25:00` 自由格式）
- ✅ 每段输出 FLAC + 纯文本歌词 + LRC 同步歌词
- ✅ 歌词**嵌入 FLAC 标签**（embedded）：
  - `LYRICS` → LRC 同步歌词（foobar2000 / MusicBee / Poweramp 逐行滚动）
  - `UNSYNCEDLYRICS` → 纯文本（Mp3tag / Bandcamp 兼容）
  - 附 `TITLE`（主题）/ `ARTIST`（视频标题）/ `COMMENT`（源链接+时间戳）
- ✅ 按歌词内容提炼主题，自动命名 `01_主题.flac`
- ✅ YouTube 自动走代理 / 自动识别登录 Cookie / 限流自动降级

## 环境准备（重要：拉下来先看这里）

本项目**不打包工具**，运行时依赖 4 个外部工具，缺一不可。每个都可以用两种方式提供：

| 工具 | 版本要求 | 获取方式 | 如何让脚本找到它 |
|---|---|---|---|
| Python | 3.13+ | python.org 或 WorkBuddy | 直接 `python` 命令 |
| ffmpeg | 任意较新版本 | [gyan.dev 官方构建](https://www.gyan.dev/ffmpeg/builds/)（下载后解压即可，无需安装） | 加入 PATH，或设环境变量 `FFMPEG_PATH` |
| yt-dlp | 2026.07+ | `pip install -U yt-dlp` 或 [GitHub release](https://github.com/yt-dlp/yt-dlp/releases) | 加入 PATH，或设 `YTDLP_PATH` |
| node | 18+ | nodejs.org | 加入 PATH，或设 `NODE_PATH` |

> **路径查找顺序**：命令行参数（`--ffmpeg` 等）→ 环境变量（`FFMPEG_PATH` / `YTDLP_PATH` / `NODE_PATH`）→ 系统 PATH。
> 报错 `找不到 ffmpeg` / `找不到 yt-dlp` / `找不到 node` 时，按上表配置即可。

**为什么需要 node**：新版 yt-dlp 对 YouTube 做 JS 挑战解算依赖 JS runtime。没有 node 会出现 `No supported JavaScript runtime` 警告，导致 YouTube 部分格式缺失或签名失败——**不是必须但有它才完整**。

### 安装步骤（一条条来）

```bash
# 1. Python 依赖（核心）
pip install faster-whisper mutagen

# 2. yt-dlp（保持最新）
pip install -U yt-dlp

# 3. 下载 Whisper 模型（国内镜像加速，约 480MB）
python bili_split.py fetch-model --name small
#    模型下载到 models/faster-whisper-small/，--model 传这个目录即可

# 4. 自测工具链（可选但强烈建议：拉下来先跑这个）
python bili_split.py selftest --model models/faster-whisper-small
#    通过标准：输出"自测通过: 工具链可用"
```

### Windows 注意

- ffmpeg 用 **portable 版**（zip 解压），不要装商店版；解压后 `bin` 目录加入 PATH，或设 `FFMPEG_PATH=D:\path\to\ffmpeg\bin\ffmpeg.exe`
- 沙箱/受限环境下脚本删除中间文件可能被拦截——属已知行为，脚本会降级继续，不影响成品

## 🔄 完整使用流程（4 步）

> 交给 AI 时：让 AI 读取本仓库（AGENTS.md 有完整 AI 指令），它就知道怎么做。

1. **打开输入模板**（填链接 + 分段时间戳，自动生成命令）：
   🌐 **https://simiely.github.io/video-split-flac/**
2. **找视频**（两个来源）：
   - YouTube：https://www.youtube.com/
   - 哔哩哔哩：https://www.bilibili.com/
3. **把「链接 + 时间戳」发给 AI** → AI 跑 `split --subs-lang zh-Hant` → 读歌词填主题 → `apply` 出 `NN_主题.flac`（FLAC + 滚动歌词 + 封面）
4. **AI 上传到 `songs/<视频ID>/` 子文件夹**（每个视频一个目录，见下方结构）

### 歌曲库结构（songs/）

```
songs/
├── README.md            # 总索引（每个视频一行）
└── <视频ID>/            # 视频 ID = 链接 ?v= 后的部分
    ├── NN_歌名.flac × N # 成品（内嵌 LRC 滚动歌词 + 封面）
    ├── NN_歌名.lrc × N  # 同名歌词（网易云音乐兼容）
    ├── cover.jpg        # 频道头像封面
    └── README.md        # 该视频的复现命令 + 清单
```

## 快速开始

```bash
# ① 下载 → 按时间戳切段 → 歌词（优先 YouTube 官方字幕，失败回退 Whisper）
python bili_split.py split \
  --url "https://www.bilibili.com/video/BV1xxxxxxxx" \
  --cuts "0:00-12:34, 12:34-25:00" \
  --model "models/faster-whisper-small" \
  --subs-lang zh-Hant \
  --out ./output

# ② 读取各 seg_XX.txt 歌词 → 在 output/themes.json 填入每段 theme（4-8字主题）
#    （也可由 AI 读歌词后代填）

# ③ 重命名 + 嵌入歌词标签
python bili_split.py apply --out ./output
```

产出：

```
output/
├── 01_三角函数入门.flac     # 成品：FLAC + LRC 滚动歌词 + 主题命名
├── 02_微积分基础.flac
├── seg_01.txt / seg_01.lrc  # 歌词中间产物
└── themes.json              # 主题填写模板
```

### 输入模板页

`input_template.html` 是可视化输入助手：填链接 + 动态增删分段（时/分/秒拆分输入）→ 实时生成命令 → 一键复制。

- **在线使用**：🌐 https://simiely.github.io/video-split-flac/（GitHub Pages，任何浏览器可开）
- 本地使用：直接浏览器打开 `input_template.html`

### YouTube 说明

- 自动走本机代理（默认 `http://127.0.0.1:7890`，可用 `--proxy` 覆盖；国内直连 YouTube 会失败）
- 匿名下载稳定但音质一般（360p/44k）；配登录 Cookie 解锁 1080p + 128k 音频：

```bash
python bili_split.py import-cookies --input cookies.json   # EditThisCookie 导出 → cookies.txt
python bili_split.py split --url ... --cookies cookies.txt ...
```

## 拉下来运行不成功？排查清单

| 现象 | 原因 | 解决 |
|---|---|---|
| `找不到 ffmpeg` | ffmpeg 未装或不在 PATH | 下载 portable 版，设 `FFMPEG_PATH` 或加 PATH |
| `找不到 yt-dlp` | 未安装 | `pip install -U yt-dlp` 或设 `YTDLP_PATH` |
| `找不到 node` | 未安装 | 装 node 并设 `NODE_PATH`（没有也能跑 B 站，YouTube 会缺格式） |
| 模型报错/下载失败 | 模型目录不存在或自动下载被网络墙 | 先跑 `fetch-model --name small` 下载到本地，`--model` 用**本地目录路径** |
| YouTube `HTTP Error 403` | 代理 IP 被 YouTube bot 检测 | 脚本默认 android client，一般可绕过；仍失败可 `--yt-client web` 或配 cookie |
| YouTube `The page needs to be reloaded` | tv client 被限流（偶发） | 脚本已自动降级 web 重试；重试一次即可 |
| 歌词转写为空 | 歌曲被 VAD 误判为噪声 | 默认已关 VAD；确认没手动加 `--vad` |
| 播放器不显示歌词 | 标签字段名问题 | 成品用 mutagen 写大写 `LYRICS`（LRC）+ `UNSYNCEDLYRICS`，foobar2000/Mp3tag 可读 |
| Windows 提示删除文件失败 | 沙箱回收站限制 | 已知行为，不影响成品，手动删即可 |

## 常用命令

| 命令 | 作用 |
|---|---|
| `split --url --cuts --model --out` | 下载→切段→转写（核心） |
| `apply --out` | 填好主题后：重命名+嵌歌词 |
| `fetch-model --name small/medium` | 下载 Whisper 模型（镜像加速） |
| `import-cookies --input x.json` | Cookie JSON → cookies.txt |
| `selftest --model` | 离线自测工具链（拉下来先跑） |
| `split ... --vad` | 讲课类可开 VAD 静音过滤 |
| `split ... --yt-client tv` | 强制高音质 client |

## 许可

个人项目，随用随取。
