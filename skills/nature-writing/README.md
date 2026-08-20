# `nature-writing` 技能

[English](README_EN.md)

`nature-writing` 用于根据作者提供的 claims、图表、结果、笔记或中文草稿，起草或重建 Nature 风格手稿章节，并准备首次投稿材料包。

## 适合用它做什么

- 构建标题、摘要、引言、结果叙事、讨论、结论或 significance paragraph。
- 根据图表和数据组织 claim-evidence 叙事。
- 将中文研究笔记转成英文手稿段落。
- 为 Introduction 建立背景、缺口、问题和贡献链。
- 对 Results 或 Discussion 做章节级重排，而不是只做句子润色。
- 将结果分为核心发现、必要支撑、结论性限定、稳健性、异质性、provenance、替代推断和边缘情况，决定主文、图注、Methods/source data 与 SI 的位置，并压缩成最短充分证据链。
- 准备首次投稿 cover letter、title page、highlights、作者贡献、数据/代码可用性和其他声明。
- 整理推荐审稿人、投稿材料矩阵和提交前完整性检查。
- 对旗舰 `Nature Article` 执行分阶段官网清单：初投稿文件、标题/字数/display 限制、Extended Data、SI、Reporting Summary、伦理和专项材料。
- 对 `Nature Machine Intelligence` 执行独立的分阶段投稿合同：Article/Analysis 字数与 6 个 display 上限、必需 cover letter、最多 10 个 Extended Data、会议论文实质扩展、数据与中心代码审查要求。
- 对旗舰 Nature、Nature Communications、NMI 及其他 Nature Portfolio 期刊的 Results，按“每节推进一个 claim”组织证据链，允许直接服务于当前实验的局部解释，并将 Discussion 收束为跨结果综合而非重复论证。
- 对所有 Nature / Nature Portfolio 目标的 Introduction，快速从具体问题收敛到精确 unknown，用文献建立 known–unknown 张力，以问题和可回答它的设计体现 novelty，并逐项对齐 Introduction 问题链与 Results 答案链。
- 对所有 Nature / Nature Portfolio 目标的 Abstract，按“精确 gap → 可回答的设计 → 主发现 → 1–2 个决定性支撑/边界 → 意义”压缩为最短证据链，数字仅在定义或实质支撑核心 claim 时保留。这三组默认最初来自 NMI 已发表论文语料归纳，其中 Results–Discussion 又经旗舰 Nature 论文对照加强；它们适用于 Nature 风格写作，但都不是官方投稿规则。

## 典型请求

- “根据这些图和结果写一个 Nature 风格 abstract。”
- “帮我重建 introduction 的逻辑，不要只润色句子。”
- “把这些中文结果整理成英文 Results 叙事。”
- “根据这篇稿件准备首次投稿 cover letter 和完整 submission package。”

## 你需要提供

- 核心 claim、图表、关键结果、实验事实和目标读者。
- 目标章节、长度、语言和需要保留的术语。
- 已确认引用、限制条件和不能新增的结论。

## 产出

- 章节大纲、claim-evidence map 或可粘贴正文。
- Results allocation table、删除/替换记录和主文压缩前后字数差（需要时提供）。
- 对 novelty、significance、证据链和读者路径的修改建议。
- 需要作者确认的事实、引用或图表说明。
- 首次投稿材料包、可编辑 LaTeX 模板、缺失信息清单和 `ready / ready_with_author_checks / blocked` 状态。

## 边界

- 不会替作者虚构实验结果、统计意义、机制解释或参考文献。
- 如果已有英文草稿只需要句子级润色，优先使用 `nature-polishing`。
- 如果需要先找文献支撑 claim，优先使用 `nature-citation` 或 `nature-academic-search`。
- 首次投稿材料由本技能处理；返修 cover letter、rebuttal 和逐点回复由 `nature-response` 处理。

## 相关技能

- `nature-polishing`：英文润色、翻译和风格收束。
- `nature-citation`：为 claim 匹配支撑文献。
- `nature-figure`：把图件结论和面板设计对齐到正文叙事。
- `nature-response`：返修 cover letter、response to reviewers 和返修通信材料。
- `nature-reviewer`：投稿前模拟审稿。
