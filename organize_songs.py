# -*- coding: utf-8 -*-
"""organize_songs.py — 把 output 成品整理进 songs/<视频ID>/ 子文件夹并生成 README。

复用流程 (AGENTS.md Step 4):
  python organize_songs.py [--lyrics-source whisper|subs]

歌词来源 (写进 README 底部):
  - whisper: Whisper 转写 (非官方歌词, 可能有错字, 待后续更新)
  - subs:    YouTube 官方字幕 (zh-Hant 转简体)
"""
import argparse
import json
import os
import shutil
from mutagen.flac import FLAC


def fmt_ts(sec):
    """秒 -> m:ss 或 h:mm:ss (用于时长显示)。"""
    sec = int(round(sec))
    h, rem = divmod(sec, 3600)
    m, s = divmod(rem, 60)
    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def cuts_str(segments):
    def ts(v):
        h = int(v // 3600)
        m = int((v % 3600) // 60)
        s = v % 60
        # 整数秒不带小数, 非整数秒保留 1 位小数
        s_str = f"{int(s):02d}" if abs(s - round(s)) < 0.001 else f"{s:04.1f}"
        return f"{h}:{m:02d}:{s_str}" if h else f"{m:02d}:{s_str}"
    return ", ".join(f"{ts(s['start'])}-{ts(s['end'])}" for s in segments)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lyrics-source", default="whisper", choices=["whisper", "subs"],
                    help="歌词来源: whisper(转写) 或 subs(官方字幕)")
    ap.add_argument("--out", default="output")
    ap.add_argument("--songs", default="songs")
    args = ap.parse_args()

    outdir = args.out
    cuts = json.load(open(os.path.join(outdir, "cuts.json"), encoding="utf-8"))
    themes = json.load(open(os.path.join(outdir, "themes.json"), encoding="utf-8"))
    url = cuts["url"]
    title = cuts["title_hint"]

    # 视频 ID: 取 ?v= 后的部分
    vid = url.split("v=")[-1].split("&")[0] if "v=" in url else url.rstrip("/").split("/")[-1]
    dst = os.path.join(args.songs, vid)
    os.makedirs(dst, exist_ok=True)

    items = [(s["idx"], s["theme"]) for s in themes["segments"] if s.get("theme")]
    seg_map = {s["idx"]: s for s in cuts["segments"]}

    # 1. 复制 flac + 生成同名 lrc
    for idx, theme in items:
        num = f"{idx:02d}"
        src_flac = os.path.join(outdir, f"{num}_{theme}.flac")
        if not os.path.exists(src_flac):
            continue
        shutil.copy2(src_flac, os.path.join(dst, f"{num}_{theme}.flac"))
        lrc = FLAC(src_flac).get("LYRICS", [""])[0]
        with open(os.path.join(dst, f"{num}_{theme}.lrc"), "w", encoding="utf-8") as f:
            f.write(lrc + "\n")

    # 2. 复制封面
    cover = os.path.join(outdir, "cover.jpg")
    if os.path.exists(cover):
        shutil.copy2(cover, os.path.join(dst, "cover.jpg"))

    # 3. 生成 README (参考 ss2rbgXZbDk 格式)
    short_title = title.split(" - ")[-1].split("|")[0].strip() if " - " in title else title
    lines = [f"# {short_title} · {len(items)} 首", ""]
    lines.append("> 生成日期：2026-08-31 · 来源：YouTube · 工具：video-split-flac")
    lines.append("")
    lines.append(f"来源视频：[{title}]({url})")
    lines.append("")
    lines.append("## 生成命令（可复现核查）")
    lines.append("")
    lines.append("```bash")
    lines.append("python bili_split.py split \\")
    lines.append(f'  --url "{url}" \\')
    lines.append(f'  --cuts "{cuts_str(cuts["segments"])}" \\')
    lines.append('  --model models/faster-whisper-small \\')
    lines.append('  --yt-client mweb \\')
    lines.append('  --cookies cookies.txt \\')
    lines.append('  --out ./output')
    lines.append("python bili_split.py apply --out ./output")
    lines.append("```")
    lines.append("")
    lines.append(f"## 歌曲清单（{len(items)} 首）")
    lines.append("")
    lines.append("| # | 歌名 | 时长 |")
    lines.append("|---|------|------|")
    for idx, theme in items:
        seg = seg_map.get(idx, {})
        dur = fmt_ts(seg.get("end", 0) - seg.get("start", 0))
        lines.append(f"| {idx:02d} | {theme} | {dur} |")
    lines.append("")
    lines.append("---")
    if args.lyrics_source == "subs":
        lines.append("歌词来源：YouTube 官方字幕（zh-Hant 转简体）。")
    else:
        lines.append("歌词来源：**Whisper 转写（非官方歌词）**，本视频无 YouTube 字幕轨道，歌词可能有错字。")
    lines.append("每首内嵌 LYRICS（标准 LRC 头）+ UNSYNCEDLYRICS + 频道头像封面（[cover.jpg](cover.jpg)，已嵌入每首 flac）+ 同名 .lrc（网易云兼容）。")
    lines.append("")
    if args.lyrics_source == "whisper":
        lines.append("> ⚠️ 歌词非官方，如有官方歌词或更准确转写，后续再更新本目录。")
        lines.append("")

    with open(os.path.join(dst, "README.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"整理完成: {len(items)} 首 -> {dst} (歌词来源: {args.lyrics_source})")


if __name__ == "__main__":
    main()
