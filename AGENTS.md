# AGENTS.md · 项目规则（AI 工作流指令）

> 📌 **文档基线**：2026-08-31（commit `b88e4d7`）完成四件套重写；0.2.0 工作流文档化
> **更新文档/代码后，请更新此行**（日期 + 新 commit hash），并在 CHANGELOG 追加版本

## ⭐ AI 端到端工作流（下次读仓库照此执行）

**目标**：用户想要"从视频出音乐（分段 FLAC + 滚动歌词 + 封面 + 上传）"，按下面 4 步走。

### Step 1 · 给用户三个网址（先发这些，等用户找视频）

```
1. 输入模板（填链接+时间戳，生成命令）：
   https://simiely.github.io/video-split-flac/
2. YouTube 官网（找视频）：
   https://www.youtube.com/
3. 哔哩哔哩官网（找视频）：
   https://www.bilibili.com/
```

### Step 2 · 等用户提供「链接 + 分段时间戳」→ 跑 split

```bash
FFMPEG_PATH=<本机ffmpeg.exe路径> YTDLP_PATH=<本机yt-dlp.exe路径> NODE_PATH=<本机node.exe路径> \
python bili_split.py split \
  --url "<视频链接>" \
  --cuts "0:00-12:34, 12:34-25:00" \
  --model models/faster-whisper-small \
  --subs-lang zh-Hant \
  --out ./output
```

- **`--subs-lang zh-Hant` 必须加**：YouTube 官方字幕（自动生成）比 Whisper 准确，失败自动回退 Whisper
- YouTube 默认走本机代理 127.0.0.1:7890；如需高音质加 `--cookies cookies.txt`（本机存在，勿入库）
- B 站无需代理无需 cookie

### Step 3 · 读歌词 → 填主题 → apply

1. 读 `output/seg_XX.txt`（每段歌词，简体）
2. 为每段提炼 4-8 字主题（经典名优先，如"两只老虎"），写入 `output/themes.json`
3. 跑 apply：
```bash
FFMPEG_PATH=<本机ffmpeg.exe路径> python bili_split.py apply --out ./output
```
产出 `NN_主题.flac`：内嵌 `LYRICS`（标准 LRC 头 `[ti:][ar:][al:]` + 时间戳滚动歌词，网易云兼容）+ `UNSYNCEDLYRICS` + `TITLE/ARTIST/COMMENT` + 封面。

### Step 4 · 上传到 `songs/<视频ID>/` 子文件夹

```
songs/<视频ID>/          ← 视频 ID 取链接 ?v= 后的部分（如 ss2rbgXZbDk）
├── NN_歌名.flac × N    ← 成品
├── NN_歌名.lrc × N     ← 同名歌词（网易云兼容）
├── cover.jpg           ← 频道头像封面（从频道页 og:image 抓取，900x900）
└── README.md           ← 复现命令 + 清单
```

上传规则：
- **小文件**（总量 <20MB）：git add + commit + push（走代理 `-c http.https://github.com.proxy=http://127.0.0.1:7890`）
- **大文件**（歌曲 flac 多）：**用 GitHub Contents API 直连上传**（node fetch 直连 api.github.com；已存在文件先 GET sha 再 PUT；base64 内容）。git push 大包会 sideband 断连。
- 上传后更新 `songs/README.md` 总索引（加一行视频记录）+ 本文件基线 + CHANGELOG

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
- **FLAC 歌词字段大写**：`LYRICS` + `UNSYNCEDLYRICS` 用 **mutagen** 写；ffmpeg `-metadata lyrics=` 写小写不认。
- **Windows 沙箱**：`os.remove`/`shutil.copy2` 对 git 跟踪文件可能被钩子静默拦截——批量文件操作用提权执行或 try/except 降级。
- **本机网络**：境外流量代理 `127.0.0.1:7890`；GitHub API 用 node fetch 直连（不用 curl/git）；curl/git 子进程访问境外常被 Clash 分流拦成 000/断连。

## 约定

- 注释用中文；输出文件 UTF-8 编码
- 敏感文件（`cookies.txt` / `youtube_cookies.json`）**绝不入库**，已 .gitignore
- 交付物 = `NN_主题.flac`；中间产物（`temp/`、`seg_XX.txt/lrc`）留在输出目录
- 上传的歌曲子文件夹命名 = 视频 ID

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
