# 素材剧本 + 覆盖矩阵（bili_split.py · 0.3.3）

## 操作链素材（S-ID，按复杂度 L1-L9 分级）

| S-ID | 等级 | 操作链（输入→动作→预期） | 覆盖 C-ID | 走查 |
|---|---|---|---|---|
| S-01 | L1 单链直通 | B站链接 + 2 段 `0:00-10:00,10:00-20:00` → split → 产出 seg_01/02.flac + txt/lrc + cuts.json + themes.json | C-01,C-06,C-14 | 深度 |
| S-02 | L1 单链直通 | YouTube 链接（无 --proxy）→ split → 自动走 127.0.0.1:7890 代理下载成功 | C-01,C-06,C-07 | 深度 |
| S-03 | L1 单链直通 | `fetch-model --name small --dir models`（模型已存在）→ 全部跳过 → 就绪提示 | C-04 | 快速 |
| S-04 | L1 单链直通 | `import-cookies`（EditThisCookie JSON）→ cookies.txt 生成 → yt-dlp 可读 | C-05 | 快速 |
| S-05 | L4 状态机长链 | split 产出 → 填 themes.json 主题 → apply → 重命名 `NN_主题.flac` + LYRICS/UNSYNCEDLYRICS 标签 → ffprobe 验证 | C-01,C-02,C-12,C-13,C-16 | 深度 |
| S-06 | L2 多步往返 | 依次用 --cookies-text → --cookies 文件 → --browser，验证优先级与命令参数正确性 | C-09 | 深度 |
| S-07 | L2 多步往返 | 带 --subs-lang zh-Hant（字幕可获取）→ 歌词走字幕；模拟字幕获取失败 → 回退 Whisper | C-10,C-11 | 深度 |
| S-08 | L3 误操作恢复 | `--cuts "12:00-10:00"`（结束早于开始）→ 抛 ValueError 退出 | C-14 | 快速 |
| S-09 | L3 误操作恢复 | apply 时某段 theme 为空 → 跳过该段继续；seg 文件缺失 → 跳过并提示 | C-02 | 深度 |
| S-10 | L8 边界极限 | `--cuts "0:00-10:00,9:50-20:00"`（重叠）→ 警告但继续执行；空 cuts → 报错 | C-14 | 快速 |
| S-11 | L8 边界极限 | 未设 FFMPEG_PATH 且 ffmpeg 不在 PATH → 报错并提示设环境变量 | C-15 | 快速 |
| S-12 | L9 故障注入 | YouTube 下载时 tv client 被限流（"page needs to be reloaded"）→ 自动降级 web/android → 下载成功 | C-08 | 深度 |
| S-13 | L9 故障注入 | fetch_title 失败（tv 限流/网络断）→ 返回空 → split 继续，apply 后 ARTIST 标签缺失（已知行为） | C-01 | 深度 |
| S-14 | L2 凭证边界 | B站导出的 cookie 文件用于 YouTube 下载（站点不匹配）→ 命令仍执行但 yt-dlp 可能 403 → 依赖 C-08 降级 | C-06,C-09 | 快速 |

## 覆盖矩阵

| 模块 | 正常 | 空态 | 边界 | 凭证差异 | 并发 | 离线 | 状态推进 | 误操作 | 故障注入 |
|---|---|---|---|---|---|---|---|---|---|
| split | S-01,S-02 | S-10 | S-10 | S-14 | — | — | S-05 | S-08 | S-12,S-13 |
| apply | S-05 | — | — | — | — | — | S-05 | S-09 | — |
| fetch-model | S-03 | — | — | — | — | — | — | — | — |
| import-cookies | S-04 | — | — | S-14 | — | — | — | — | — |
| 歌词/字幕 | S-07 | — | — | — | — | — | S-05 | — | S-13 |

对账结论：
- 每行 ≥1 格 ✓；每列 ≥1 格 ✓（L4 状态推进 S-05、L8 边界 S-10/S-11、L9 故障注入 S-12/S-13 齐备）
- L5 并发 / L6 离线：**整列留空，理由已记**（单进程 CLI 无并发；一次性执行无重放）→ 符合方案「空格写理由」要求
