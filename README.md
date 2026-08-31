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

## 安装

依赖：Python 3.13+、[ffmpeg](https://www.gyan.dev/ffmpeg/builds/)（加入 PATH 或指定路径）、yt-dlp。

```bash
# 1. Python 依赖
pip install faster-whisper mutagen

# 2. yt-dlp（已随包管理可用则跳过）
pip install -U yt-dlp

# 3. 下载 Whisper 中文识别模型（国内镜像加速）
python bili_split.py fetch-model --name small
```

## 快速开始

```bash
# ① 下载 → 按时间戳切段 → Whisper 转写歌词（含 LRC 时间戳）
python bili_split.py split \
  --url "https://www.bilibili.com/video/BV1xxxxxxxx" \
  --cuts "0:00-12:34, 12:34-25:00" \
  --model "models/faster-whisper-small" \
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

`input_template.html` 是可视化输入助手：填链接 + 动态增删分段 → 实时生成命令 → 一键复制。直接浏览器打开即可。

### YouTube 说明

- 自动走本机代理（`http://127.0.0.1:7890`，可用 `--proxy` 覆盖）
- 匿名下载稳定但音质一般（360p/44k）；配登录 Cookie 解锁 1080p + 128k 音频：

```bash
python bili_split.py import-cookies --input cookies.json   # EditThisCookie 导出 → cookies.txt
python bili_split.py split --url ... --cookies cookies.txt ...
```

## 常用命令

| 命令 | 作用 |
|---|---|
| `split --url --cuts --model --out` | 下载→切段→转写（核心） |
| `apply --out` | 填好主题后：重命名+嵌歌词 |
| `fetch-model --name small/medium` | 下载 Whisper 模型（镜像加速） |
| `import-cookies --input x.json` | Cookie JSON → cookies.txt |
| `selftest --model` | 离线自测工具链 |
| `split ... --vad` | 讲课类可开 VAD 静音过滤 |
| `split ... --yt-client tv` | 强制高音质 client |

## 许可

个人项目，随用随取。
