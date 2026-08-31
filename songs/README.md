# 歌曲库 · 按视频分文件夹

每个来源视频一个子文件夹，命名 = 视频 ID（可从链接 `youtube.com/watch?v=<ID>` 获取）。

| 子文件夹 | 视频 ID | 内容 | 生成日期 |
|---|---|---|---|
| [`ss2rbgXZbDk/`](ss2rbgXZbDk/) | ss2rbgXZbDk | 宝宝中文儿歌合集 23 首（flac + lrc + 封面 + 复现命令） | 2026-08-31 |
| [`Ogb8PcUBwpE/`](Ogb8PcUBwpE/) | Ogb8PcUBwpE | 唱儿歌学中文 27 首（flac + lrc + 封面 + 复现命令） | 2026-08-31 |

## 约定

- 每个子文件夹包含：`NN_歌名.flac`（含 LRC 滚动歌词/封面标签）、同名 `.lrc`、`cover.jpg`、`README.md`（复现命令 + 清单）
- 新增视频 → 新建 `<视频ID>/` 子目录，并在本表加一行
- 上传方式：小文件 git push；大文件（>20MB 单文件或总量大）用 GitHub Contents API 直连上传（见 AGENTS.md）
