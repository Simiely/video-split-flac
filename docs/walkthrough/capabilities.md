# 能力清单（bili_split.py · 0.3.3）

> 依据：代码 grep 验证（5 子命令 / split 15 参数 / 其他 10 参数）+ radon 实测（cc A 4.89 / MI A 20.05）。
> 铁律：素材（scenarios.md）中出现的功能必须都能在下列清单中找到。

## CLI 入口层

| C-ID | 能力 | 入口 | 说明 |
|---|---|---|---|
| C-01 | split 主流程（下载→解码→切割→歌词→主题模板） | `split --url --cuts` | 产出 seg_XX.flac/txt/lrc + cuts.json + themes.json |
| C-02 | apply 重命名+嵌标签 | `apply` | 读 themes.json → `NN_主题.flac` + mutagen 写标签 |
| C-03 | selftest 离线自测 | `selftest` | 合成正弦波 → 切割+转写全链路验证 |
| C-04 | fetch-model 模型下载 | `fetch-model --name --dir` | 镜像优先/代理兜底；已有文件跳过 |
| C-05 | import-cookies 转换 | `import-cookies --input --output` | EditThisCookie JSON 或 name=value 字符串 → cookies.txt |

## 逻辑层

| C-ID | 能力 | 位置 | 说明 |
|---|---|---|---|
| C-06 | 站点识别 B站/YouTube | detect_site | URL 含 youtube/youtu.be → youtube；bilibili/bv 开头 → bilibili |
| C-07 | YouTube 代理默认 + 覆盖 | resolve_proxy | 未指定 --proxy 且 youtube → PROXY_DEFAULT(127.0.0.1:7890) |
| C-08 | YouTube client 多级降级 | download_audio | 当前→web→android→tv 轮询，全失败抛最后错误 |
| C-09 | cookie 三来源优先级 | build_dl_cmd | --cookies-text > --cookies 文件 > --browser 登录态 |
| C-10 | 歌词来源：字幕优先→Whisper 回退 | collect_subs_timed + transcribe_segments | --subs-lang 获取失败自动回退 |
| C-11 | 繁转简 | to_simplified | OpenCC t2s，LRC 前缀保留；未装 opencc 原样返回 |
| C-12 | LRC 标准头 + 时间戳 | build_lrc / rebuild_lrc_header | [ti:][ar:][al:] 全写（网易云兼容）|
| C-13 | 标签嵌入 | write_flac_tags | LYRICS(LRC滚动) + UNSYNCEDLYRICS(纯文本) + TITLE/ARTIST/COMMENT |
| C-14 | 时间戳/分段校验 | parse_ts / parse_cuts | 格式错误抛错；结束≤开始抛错；重叠仅警告(0.5s 容差) |
| C-15 | 工具路径解析 | find_exe / _tool_path | 参数 > 环境变量(FFMPEG_PATH 等) > PATH；找不到报错提示 |
| C-16 | 文件名净化 | sanitize | Windows 非法字符 → 下划线，去首尾点 |

## 已知边界（走查前提）

- 单进程 CLI：**无并发**（L5 素材不适用，理由：同一命令单次执行）
- 一次性本地执行：**无离线重放**（L6 素材不适用，理由：无队列/重放机制）
- 无多角色权限模型：权限差异列以「凭证/配置边界」覆盖（S-14）
