# `nature-statistics` 技能

[English](README_EN.md)

`nature-statistics` 用于审查、改写或起草 Nature / 高影响力期刊投稿中的统计报告文本，重点是透明、可复核、与实验设计一致，而不只是 p 值是否显著。

## 适合用它做什么

- 检查 Statistical analysis / Methods 中统计方法是否完整。
- 改写 Results、figure legends 和 source data 中的统计说明。
- 区分 biological replicates、technical replicates、重复测量、视野/细胞/子样本和独立实验单位。
- 识别伪重复、嵌套数据、多重比较、交互解释、相关性过度解释和显著性滥用。
- 交叉检查摘要、正文、表格和结论中同一统计量的数值精度、单位及统计术语是否一致。
- 根据审稿人统计意见生成保守回应或修改建议。
- 对旗舰 `Nature Article` 检查单尾/双尾、exact n、重复次数、显著与非显著 P 值、ANOVA F/df 和 t 检验 t/df。

## 典型请求

- “帮我检查这段 Statistical analysis 是否符合 Nature 风格。”
- “图注里的 error bars、n 和 p 值怎么写更清楚？”
- “审稿人说统计不充分，帮我列修改方案和回复草稿。”

## 你需要提供

- 样本量、重复层级、实验单位、分组、检验方法和多重比较方式。
- 图表、图注、Results 文本、统计输出或审稿意见。
- 哪些事实已确认，哪些需要保守标注。

## 产出

- 统计报告审查：主要问题、风险等级和需要作者确认的信息。
- 可粘贴的 Statistical analysis、Results 或 figure legend 改写。
- 跨章节统计一致性风险清单。
- 审稿统计问题的逐点回应草稿。
- `AUTHOR_INPUT_NEEDED` 清单，用于标记缺失样本量、检验或设计事实。

## 边界

- 不会替作者编造样本量、重复数、p 值、效应量、模型假设或检验名称。
- 不直接替代统计师或完整再分析；如需重新建模，应要求原始数据和分析代码。
- 不能仅凭图像判断实验单位和独立重复，需要作者确认设计。

## 相关技能

- `nature-figure`：把统计信息落实到图件和 source data。
- `nature-response`：回应统计类审稿意见。
- `nature-polishing`：润色统计描述的英文表达。
