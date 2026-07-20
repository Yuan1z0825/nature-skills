# Export and archive

Formal export must create two files:

```text
exports/proposal_final.md     # archive / versioning / future reuse
exports/proposal_final.docx   # submission / supervisor circulation
```

Optional export:

```text
exports/proposal_final.pdf
```

**.docx 必须用 python-docx 脚本生成，禁止用 pandoc**。pandoc 输出的 .docx 格式粗糙（标题蓝色、无中文字体、无段落格式），不可直接交付。使用 `scripts/build_proposal_docx.py`，该脚本实现以下格式：Times New Roman 12pt + 宋体，Heading 黑体或宋体加粗黑色，1.5 倍行距，四边 1 英寸页边距，表格 10pt 带网格。Load `pdf` only when PDF is requested.

## Pre-delivery checks

- No unresolved TODOs
- No unsupported claims presented as facts
- Citation placeholders cleared or explicitly marked
- Figure/table numbering consistent
- Version name and date clear
- Target threshold reached or remaining risks reported

## docx 格式要求

pandoc 默认输出格式粗糙，正式提交版需用 python-docx 生成：
- 标题：居中、Times New Roman + 宋体、18pt 加粗、黑色
- Heading 1/2/3：Times New Roman + 宋体、16/14/12pt、加粗、黑色
- 正文：Times New Roman + 宋体、12pt、1.5 倍行距、无首行缩进（西文论文风格）
- 页边距：四边 1 英寸
- 表格：10pt、Table Grid 样式
- 代码块：Consolas 9pt

参考脚本：`scripts/build_proposal_docx.py`（解析 markdown → 格式化 docx）

## Archive rule

Before writing to an external archive, vault, or synced folder, ask for explicit approval:

```text
是否归档到 <archive-root>/researchwrite/<project-slug>/？
```

Keep external archival outside the default pipeline unless the user explicitly requests it.
