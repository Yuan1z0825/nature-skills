# `nature-paper-card` 技能

[English](README_EN.md)

`nature-paper-card` 用于精读一篇科研论文，并生成有来源约束、可复核的 01–16 节 Paper Card；它强调研究问题、方法逻辑、实验—结论证据链、结论边界、批判性分析和可检验研究想法，而不是把摘要翻译成中文。

## 适合用它做什么

- 对单篇论文进行结构化精读，而不是只生成摘要。
- 追踪核心结论对应的图、表、公式、实验和消融证据。
- 区分作者陈述、外部事实、Agent 分析和研究假设。
- 检查论文的结论边界、作者自述局限和未解决问题。
- 从证据链出发提出可证伪、可执行的候选研究想法。

## 典型请求

- “使用 `nature-paper-card` 精读这篇 PDF，生成完整 Paper Card。”
- “分析这篇论文的方法模块、关键公式和实验—结论证据链。”
- “这篇论文真正证明了什么、没有证明什么？”
- “基于论文中的限制，提出几个可以验证的后续研究方向。”

## 你需要提供

- 一篇论文的 PDF、DOI、arXiv 页面、出版社文章、粘贴文本，或已有的 `nature-reader` source map。
- 如有需要，说明输出语言、输出目录和希望重点审查的问题。
- 若只有摘要或局部材料，Skill 仍可运行，但会明确标记无法判断的部分。

## 工作方式

1. 使用内置 `prepare_paper.py` 准备来源材料，不临时重写 PDF 提取脚本。
2. 根据证据可靠性选择 `page-grounded`、`structure-grounded` 或 `source-limited` 模式。
3. 按论文的论证结构选择方法、发现、资源、临床、材料或综述分析镜头。
4. 先建立证据清单和 claim–evidence matrix，再生成固定的 01–16 节 Paper Card。
5. 使用内置 `audit_paper_card.py` 检查结构、来源定位和证据约束。

## 产出

- `paper-card.md`：固定 01–16 节的深度 Paper Card。
- `source_bundle.json`：PDF 或 source map 的标准化来源包。
- `audit-report.json`：结构、定位和证据约束审计结果。
- 可选的 `rendered-pages/`：需要视觉核对时渲染的 PDF 页面。

## 运行和依赖

- 需要 Python 3。
- PDF 处理优先使用 Skill 自带脚本和当前环境中可用的 PDF 库。
- PDF 页码可靠时同时使用 PDF 页码和结构定位；页码提取失败时自动降级为结构定位，不伪造页码。
- source map 中缺失或非法的页码会保留为未定位块并给出警告，不会自动归入 PDF 第 1 页。
- 外部检索只用于文献背景核验、知识连接、书目信息确认或用户明确要求的新颖性检查。

## 使用教程

完整的可复制教程见[中文教程](../../docs/nature-paper-card-tutorial.md)，包括输入、触发方式、三种来源定位模式、输出文件和结果验收方法。

最小调用示例：

```text
使用 nature-paper-card 精读这篇论文，生成中文 Paper Card。
重点检查方法模块、关键实验、结论边界和可验证的后续研究想法。
```

## 边界

- 一次处理一篇论文，不负责批量文献监控。
- 不生成全文双语翻译；需要全文阅读材料时使用 `nature-reader`。
- 不生成正式同行评审报告；需要审稿人视角时使用 `nature-reviewer`。
- 不把 Paper Card 改写成公众号文章，也不生成第 17、18 节。
- 来源不足时明确写 `Not assessable`，不会补写不可见的实验或页码。

## 相关技能

- `nature-reader`：生成全文双语 Markdown、图文对应和稳定 source map。
- `nature-academic-search`：核验领域历史、外部知识连接或相关工作。
- `nature-reviewer`：生成正式的审稿人式评审报告。
- `nature-literature-pipeline`：批量发现、筛选和推送论文。
- `nature-paper2ppt`：把论文内容转换成汇报幻灯片。
