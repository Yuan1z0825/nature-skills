---
name: nature-exam-thumbnail
description: >-
  Batch-generate consistent WebP thumbnails for all exams or questions in a
  learning platform, using stock photos (Pexels), an emoji + short text overlay,
  level/type corner tags, upload to R2/S3, and update the platform DB rows.
---

# nature-exam-thumbnail — 批量生成并上线考试缩略图

需要批量处理“每个考试/题目缺一张缩略图”的任务时读取本技能。它覆盖从
数据库读取缺缩略图的记录、抓取不重复的图源、渲染 WebP、上传对象存储、
回写数据库并校验的三个环节（生成 → 上传 → 回写 → 校验）。

## 触发词

`exam thumbnails`、`generate thumbnails`、`考试缩略图`、`试卷封面图`、
`thumbnail missing`、`批量缩略图`

## 适用场景

- 新导入一批考试（如 telc B1/B2 数十套）时逐条缺少 `photo_url`
- 更换图源、修复重复/404 缩略图后需要重跑
- 学习平台前端列表页需要统一风格的封面色

## 工作流

### Step 1: 读数据库，圈定缺缩略图的记录

```sql
select e.id, e.title, e.category, e.level, e.type
from exams e
where (lower(e.title) like '%telc%' or lower(e.category) like '%telc%')
  and (e.photo_url is null or trim(e.photo_url) = '')
order by e.view_order
```

- 默认只补缺缩略图的行；不要覆盖已有缩略图，除非用户明确要求或修重复/404。
- 用项目的 venv Python（如 `.venv/bin/python`），不要用系统 Python，避免
  `datetime.UTC` 在 3.9 下缺失。

### Step 2: 拉取不重复的图源

- 有 `PEXELS_API_KEY` 时走 Pexels API，跨多个关键词（如 `german old town architecture`、
  `bavaria old town`）分页拉，按 photo id 去重。
- 拉图数量必须 ≥ 题目数；不足则换更多关键词或提高页数。
- 无 key 时退回 curated Pexels CDN URL 列表，但同样需要唯一且可访问。

### Step 3: 渲染并上传

- 复用/维护一个缩略图 CLI（可用 Pillow）：输出 `1280x720` WebP，
  文字左对齐、白底 inline 标签、emoji 独立无背景、右上角 level/type 圆角 pill 标签。
- emoji 只能来自用户提供的列表/文件，不要凭空发明 emoji 池。
- 对象路径 `thumbnails/exams/{exam_id}.webp`，上传到 R2/S3（ContentType
  `image/webp`，缓存一年）。
- 每张图用独立的 Pexels 源图，避免重复。

### Step 4: 回写数据库

- 上传成功后才 `update exams set photo_url = :url where id = :eid`。
- 一次性 commit；把 `{id, url, source_photo, emoji}` 存成 audit JSON 便于重试。
- 回写后按平台约定清除详情缓存键（如 `exam_bank:exam:<id>`）。

### Step 5: 校验

- 缺缩略图数量归零、无重复 `photo_url`。
- 抽样 HEAD 公共 URL，要求 `200` 且 `content-type` 为 `image/*`。

## 运行和依赖

- Python ≥ 3.10（需 `datetime.UTC`），依赖：`pillow`、`requests`、`boto3`、
  `python-dotenv`、`sqlalchemy`(async)。
- R2 环境变量：`R2_ACCOUNT_ID`、`R2_ACCESS_KEY_ID`、`R2_SECRET_ACCESS_KEY`、
  `R2_BUCKET_NAME`、`R2_PUBLIC_URL`（公共 base URL）。
- Pexels key 可选；缺省退回 curated URL。

## 内置参考

- `references/bulk-exam-thumbnail-cli-workflow.md`：完整批量运行流程、已知坑。

## 边界

- 不做“图片创意设计”，只产出统一风格的封面；文案由用户提供。
- 不覆盖已有 `photo_url`，除非显式要求（修重复/404 除外）。
- 永远不伪造上传成功：URL 未回写前不更新 DB。
- 不做 OCR/检测图里是否含文字。

## 相关技能

- `nature-figure`：论文级科学插图，不是产品封面。