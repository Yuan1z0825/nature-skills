# `nature-figure` 技能

[English](README_EN.md)

`nature-figure` 用于设计、生成和审查投稿级科研图件，面向 Nature 系列、高影响力期刊、论文图版、机制示意图和 graphical abstract 草稿。

## 适合用它做什么

- 根据数据、图注或论文结论生成 Python / R 绘图脚本和可编辑图件。
- 将已有图件重画为更清楚的多面板论文 figure。
- 按“一张 Figure 回答一个 Results 级科学问题”的默认逻辑规划多面板证据链，让各 panel 分别承担主证据、control、正交验证、扰动、机制或边界等不同推理角色，而不是只把同一结果换指标重画。
- 规划 Figure 1、机制图、workflow、graphical abstract 或补充图。
- 检查面板标签、配色与视觉层级、逐面板误差线、最终 PDF 实际字号、统计标注、source data 和导出格式；多面板图在渲染时自动检查同行/同列轴框、宽高、panel 标签锚点和重复间距是否在 1.5 pt 容差内，每次生成或修改布局后再检测文字—文字、文字—线条/曲线、页面裁切及可疑色块/图片边缘重合。
- 区分旗舰 `Nature` 初投稿、主图终稿和 Extended Data 的文件契约，并执行 `<250` 词图注上限。
- 对 `Nature Machine Intelligence` 单独执行 6 个主 display、最多 10 个 Extended Data、初投稿/终稿边界、300 dpi/180 mm 和 source data 要求；当前官网未给独立图注数字，保留 2018 官方 `<300` 英文词为历史建议线，整张图注建议 150–250 词且不是每个 panel 分别计算。
- 在用户明确要求时，通过 OpenRouter Images API 调用 `openai/gpt-image-2` 生成 AI 概念示意图草稿。
- 对 AI 辅助 graphical abstract 先定义单一中心信息、图件类型、目标读者和证据边界，再比较构图与可访问配色；投稿前单独核验目标期刊最新 AI 政策、科学准确性、版权、披露和 provenance。`Nature Careers` 专栏仅作为实践建议，不等于投稿许可。

## 工作方式

绘图前先建立图件契约，而不是直接套模板：

- 核心结论：这张图要证明什么。
- 证据层级：哪些面板是主证据，哪些是补充解释。
- 多面板架构：先写 figure-level claim，再决定每个 panel 的独特证据角色以及主图、另一张图或 Extended Data/SI 的去向。
- 图件原型：散点、箱线、热图、机制图、流程图、多面板组合等。
- 后端选择：Python 或 R；第一次选择后会作为默认偏好复用。
- 数据完整性：默认保留全部观测和指定变量，任何排除都记录规则与前后计数。
- 模板兼容性：先核对科学含义、数据结构和变换条件，再决定精确复用、结构适配或只继承样式。
- 投稿约束：尺寸、字体、色彩、分辨率、矢量格式和 source-data 可追溯性。
- 子图对齐门：由 Python axes 或 R patchwork/gtable 在最终尺寸下测量真实 panel 矩形；横排 3/4 张等跨度 panel 自动保证等宽，普通网格及“左二右一 / 左一右二”等跨行布局自动推断，可靠错位阻断导出，free-positioned hero panel、inset 和 colorbar 只能带理由豁免。
- 渲染碰撞门：最终 PDF 每次重绘后都生成 collision JSON；可靠碰撞必须修复，可疑 overlay 必须逐项复核。

## 典型请求

- “把这组数据做成 Nature 风格多面板图，优先 Python。”
- “参考 figures4papers 里 Nature Machine Intelligence 的布局，帮我补一个方法对比图。”
- “重画这个机制示意图，导出 SVG/PDF，并给我 source data 表。”
- “用 OpenRouter 生成 graphical abstract 草稿，但不要当作定量数据图。”

## 示例预览

| 方向 | 预览 | 可借鉴模式 |
|------|------|------------|
| 多面板论文图 | <a href="assets/gallery/fig1-material-mechanism-rich.png"><img src="assets/gallery/fig1-material-mechanism-rich.png" width="220" alt="Material design and physical validation"></a> | 机制示意、图像面板、定量结果和相关性放在同一证据链中 |
| 图表类型 atlas | <a href="assets/chart-atlas/atlas-03-heatmaps.png"><img src="assets/chart-atlas/atlas-03-heatmaps.png" width="220" alt="Heatmap atlas"></a> | 热图、注释矩阵、聚类块和发散色标的组合模式 |
| 第三方 figures4papers 参考 | <a href="assets/figures4papers/figure_VIGIL/figures/comparison_radar.png"><img src="assets/figures4papers/figure_VIGIL/figures/comparison_radar.png" width="220" alt="VIGIL comparison radar"></a> | 仅用于研究 layout、legend 和多指标比较语法；使用前阅读独立版权说明 |

## 你需要提供

- 原始数据、已有图、图注、论文 claim 或想表达的机制。
- 目标期刊、单栏/双栏尺寸、输出格式和是否需要 source data。
- Python / R 偏好；如果没有偏好，技能会先询问或沿用本机记录。

## 产出

- 可运行的 Python 或 R 绘图脚本。
- SVG/PDF/TIFF/PNG 等图件文件，优先保留可编辑矢量版本。
- 面板说明、source data 映射、排除计数、逐面板视觉审查表、alignment JSON/诊断 SVG、碰撞 JSON/诊断 PDF 和投稿前 QA 记录。
- AI 示意图任务中，输出概念草稿和需要人工重画/核实的元素列表。

## 内置参考

- `references/api.md`：Python 配色、样式和绘图 helper 约定。
- `references/asset-adaptation.md`：模板语义匹配、字段映射和数据完整性规则。
- `references/multipanel-evidence-architecture.md`：从 Results 级问题到 panel 证据角色、图内闭环、跨 Figure claim escalation 和主图/Extended Data/SI 去向的规划与审计。
- `references/template-catalog.md`：volcano、ROC、marker dot plot、marginal 和 paired 的已验证 Python CSV 模板。
- `references/chart-types.md`：常见图型选择和视觉规则。
- `references/demos.md`：第三方 `figures4papers` 示例索引、使用边界和原创适配模式。
- `references/qa-contract.md`：导出前检查项、source-data 约束和静态预检入口。
- `references/ai-graphical-abstract-workflow.md`：AI 图形摘要的信息简报、构图与配色、期刊政策门、人工科学核验、披露和 provenance 工作流。
- `references/openrouter-image-generation.md`：OpenRouter / GPT Image 2 的 provider-specific 生成与 QA 路径。
- `scripts/validate_figure.py`：Python/R 绘图源码的可复现静态 QA。
- `scripts/audit_pdf_text.py`：扫描导出 PDF 的 `Tf` 操作符，发现 mathtext 上下标等低于 5 pt 的实际字形。
- `scripts/audit_panel_alignment.py` 与 `scripts/panel_alignment.R`：在最终物理尺寸下测量 Matplotlib axes 或 R patchwork/gtable，对同行 3/4 panel 等宽、同行/同列边界、跨行面板共享外边界、panel 标签和重复间距执行阻断式自动审计。
- `scripts/audit_figure_collisions.py`：对 Python/R 最终 PDF 执行自动几何碰撞审计，输出阻断性 FAIL、需复核 WARN、JSON 报告和可选带框诊断 PDF。
- `scripts/figure_safety.py`：严格单调插值和基于数据/误差范围的标签高度 helper。
- `assets/figures4papers/`：保留的第三方参考脚本与预览图；不自动适用本仓库 MIT License，使用前阅读 `THIRD_PARTY_NOTICES.md`。

## 边界

- 不会把 AI 生成图片当作真实实验结果或定量数据面板。
- 不会把内部可用的 AI 草稿自动称为可投稿终稿；两者分别判定。
- 不会凭空补统计检验、样本量、误差线含义或实验条件。
- 不会为了渲染方便静默抽样、忽略变量或删除不完整观测。
- 不会把自动校验通过当作视觉验收；对齐门只保证已声明的几何关系在容差内，最终交付仍需逐面板检查不确定性、标签碰撞、间距和显著性层级。
- 私有模板可以在本机使用，但不应在面向用户输出中暴露私有路径、文件名或来源。
- 第三方参考材料的版权和再使用条件以其来源及 `THIRD_PARTY_NOTICES.md` 为准；本仓库不额外授予这些文件的使用权。

自动碰撞审计需要 PyMuPDF：

```bash
python -m pip install -r skills/nature-figure/requirements.txt
```

## 相关技能

- `nature-statistics`：检查统计标注、n 定义和 p 值表述。
- `nature-writing`：把图件结论放回手稿叙事。
- `nature-paper2ppt`：把论文图件整理成汇报幻灯片。

## 与其他技能的关系

- 如果任务核心是统计解释、样本量定义或显著性表述，优先让 `nature-statistics` 先把文字审清，再回到 `nature-figure` 画图。
- 如果图件已经定稿，但需要把结论组织成摘要、引言或结果段落，交给 `nature-writing` 继续承接。
- 如果图件要直接转成组会材料或答辩汇报，再交给 `nature-paper2ppt` 组织成页面。
- `nature-figure` 负责图件本身；它不替代统计审查，也不替代手稿叙事。
