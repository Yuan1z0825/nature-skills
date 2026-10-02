# `nature-paper-card` 使用教程

[English](nature-paper-card-tutorial_EN.md)

## 它解决什么问题

普通论文摘要只能告诉你作者声称做了什么。`nature-paper-card` 会进一步检查方法如何工作、关键结论由哪些实验支撑、结论边界在哪里，以及哪些后续想法值得验证，最终生成固定 01–16 节的可复核 Paper Card。

## 准备输入

推荐提供完整 PDF，也可以提供 DOI、arXiv 页面、出版社文章、粘贴文本或 `nature-reader` 生成的 source map。仅提供摘要时，结果会自动进入 `source-limited` 模式。

示例输入：

```text
使用 nature-paper-card 精读这篇 PDF，生成中文 Paper Card。
重点检查：
1. 每个方法模块解决什么问题；
2. 哪些实验真正支撑主要结论；
3. 作者没有证明什么；
4. 哪些后续研究想法具有可检验性。
```

## 运行流程

Agent 应先调用 Skill 自带的 `scripts/prepare_paper.py`，而不是临时编写 PDF 提取脚本。准备完成后，它会选择一种来源定位模式：

| 模式 | 使用条件 | 引用方式 |
|---|---|---|
| `page-grounded` | PDF 页码提取可靠 | PDF 页码加章节、图、表或公式定位 |
| `structure-grounded` | 页码不可靠，但全文结构仍可靠 | 只使用章节、图、表、公式或文本块定位 |
| `source-limited` | 只有摘要、元数据或局部文本 | 明确限定材料范围，不生成页码引用 |

随后，Agent 建立证据清单和 claim–evidence matrix，生成 Paper Card，并调用 `scripts/audit_paper_card.py` 做最终审计。

## 检查输出

典型输出目录包括：

```text
workdir/
├── source_bundle.json
├── paper-card.md
├── audit-report.json
└── rendered-pages/    # 仅在需要视觉核对时出现
```

验收 `paper-card.md` 时检查：

- 01–16 节是否完整且顺序正确；
- 主要方法、结果、边界和限制是否带有来源定位；
- 数值是否与论文一致；
- 作者陈述和 Agent 分析是否明确分开；
- 页码不可用时是否正确降级，而不是伪造页码；
- 第 16 节的研究想法是否包含假设、机制、实验和失败判据；
- 是否没有第 17、18 节或公众号文章内容。

`audit-report.json` 中的错误应在交付前解决；警告需要结合论文内容人工判断。

## 不完整来源示例

如果只有摘要，可以这样调用：

```text
使用 nature-paper-card 根据这段摘要生成 source-limited Paper Card。
不要推断正文实验，不要生成页码引用；无法判断的部分明确标记。
```

此时结果仍保持 01–16 节结构，但不可由现有材料支撑的内容会标为 `Not assessable from supplied material`。

## 与相邻技能的分工

- 需要全文双语阅读材料：使用 `nature-reader`。
- 需要外部文献检索和领域历史核验：使用 `nature-academic-search`。
- 需要正式审稿报告：使用 `nature-reviewer`。
- 需要批量发现和筛选论文：使用 `nature-literature-pipeline`。
- 需要论文汇报幻灯片：使用 `nature-paper2ppt`。
