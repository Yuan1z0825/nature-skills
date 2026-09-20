# `nature-exam-thumbnail` 技能

[English](README_EN.md)

批量生成并上线学习平台考试缩略图：从数据库读取缺缩略图的记录，抓取不重复图源，渲染统一风格 WebP，上传到 R2/S3，再回写数据库并校验。

## 适合用它做什么

- 新导入一批考试（如 telc B1/B2 数十套）后逐条缺少封面图。
- 修复重复图片、404 图片后需要重跑生成。
- 让学习平台列表页有统一风格的封面。

## 典型请求

- “有 49 套 telc 考试没有缩略图，帮我生成并更新数据库。”
- “现在缩略图有几张重复，重新生成一批不重复的。”
- “换一套图源，把所有考试的封面重新生成。”

## 你需要提供

- 数据库访问（能查到 `exams` 表与缺 `photo_url` 的行）。
- R2/S3 对象存储配置（`R2_ACCOUNT_ID`、`R2_ACCESS_KEY_ID`、`R2_SECRET_ACCESS_KEY`、`R2_BUCKET_NAME`、`R2_PUBLIC_URL`）。
- 可选：Pexels API key；缺省退回 curated URL。
- 可选：允许使用的 emoji 列表（默认用内置列表）。

## 产出

- 每场考试一张 `thumbnails/exams/{exam_id}.webp`（1280×720 WebP）。
- 公共 URL 列表与 `{id, url, source_photo, emoji}` audit JSON。
- 数据库 `exams.photo_url` 已更新，缺缩略图数量归零，无重复。

## 边界

- 不做创意设计，文案由用户提供。
- 不覆盖已有 `photo_url`，除非修复重复/404。
- 上传成功前不会声称完成。

## 相关技能

- `nature-figure`：论文级科学插图，不是产品封面。