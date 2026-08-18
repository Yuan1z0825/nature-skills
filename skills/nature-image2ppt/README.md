# `nature-image2ppt` 技能

[English](README_EN.md)

`nature-image2ppt` 将已有幻灯片图片、截图、扫描 PDF 或图片型 PPTX 重建为对象级可编辑 PowerPoint；它负责还原现有视觉页面，不负责根据笔记从零创作新演示文稿。

## 适合用它做什么

- 把单页或多页幻灯片图片转换为可编辑 `.pptx`。
- 恢复扫描 PDF、截图或图片型 PPTX 中的文本、形状和页面结构。
- 原生重建文本框、卡片、圆形节点、连接线、箭头、公式和可测量曲线。
- 将无法可靠原生重建的复杂局部保留为可替换图片资产。
- 保留源 PPTX 的 speaker notes，并对页面和最终文件执行渲染 QA。

## 典型请求

- “把这些幻灯片截图还原成可以逐个编辑元素的 PowerPoint。”
- “把这个扫描 PDF 转成可编辑 PPTX，保留原来的版式。”
- “修复这份图片型 PPT，让流程图、知识图谱和箭头可以编辑。”

## 你需要提供

- 幻灯片图片、扫描 PDF 或图片型 PPT/PPTX 文件。
- 希望保留的页面范围、语言、尺寸或字体要求；没有特殊要求时可省略。
- 是否允许复杂插图作为独立图片资产保留，以及材料是否必须离线处理。

## 工作方式

1. 运行环境预检，规范化输入并生成 OCR 文字提示。
2. 按语义区域拆解页面，在原生对象和局部图片资产之间进行混合重建。
3. 对每页执行结构、箭头、区域分解和渲染检查；视觉结论以绑定当前源图/渲染哈希的逐项证据记录，不能用“看起来不错”代替。
4. 从结构化 v2 页面 manifest 组装最终 PPTX，并重新验证渲染结果和 speaker notes。

## 产出

- 对象级可编辑 PowerPoint 文件。
- 每页的 manifest、文字提示、渲染预览和 QA 报告。
- 最终文件验证结果，以及仍作为可替换图片资产保留的复杂视觉清单。
- 页面输出严格限制在各自页面目录，最终文件限制在本次 run 目录，并采用原子写出避免失败后留下半成品。

## 运行和依赖

- 使用 Python 3.10 或更高版本，并安装 `requirements.txt`。
- 复制或同步技能文件不会自动安装 Python 包；必须在实际运行 CLI 的同一 Python 环境中安装依赖，并以 `doctor --json` 成功为准。
- 使用 Microsoft PowerPoint（Windows）或 LibreOffice 完成渲染检查；以 `python cli/image2ppt/cli.py doctor --json` 的结果为准。
- 在线文字识别使用百度 AI Studio `PADDLE_OCR_TOKEN`。将 `config.example.yaml` 复制为同目录的 `config.yaml` 后填写 Token；真实配置已被 Git 忽略，不能提交。
- 完整实现同步自 [Paul-Jeo/Image2PPT](https://github.com/Paul-Jeo/Image2PPT)，并在本技能目录中保留 MIT License。

## 边界

- 只还原已有页面；根据论文、提纲或笔记创作新 deck 时使用 `nature-paper2ppt`。
- 照片、复杂插画、密集知识图谱和难以稳定测量的视觉可能部分保留为图片资产。
- 低分辨率输入、缺失字体和复杂曲线会限制还原精度，需要根据渲染对照复核。
- 在线 OCR 会把当前任务页面发送到百度服务；敏感材料应选择离线模式。

## 相关技能

- `nature-paper2ppt`：从论文内容创作新的汇报型演示文稿。
- `nature-figure`：生成或重绘投稿级科研图和论文示意图。
- `nature-reader`：先建立扫描论文的全文阅读材料和图文对应关系。
