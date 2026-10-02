# `nature-reviewer` 技能

[English](README_EN.md)

`nature-reviewer` 用于从审稿人视角模拟 Nature 风格的预投稿评审，帮助作者在投稿前发现 novelty、significance、technical soundness 和读者价值上的风险。

## 适合用它做什么

- 对手稿、摘要、图表或结果故事线做投稿前压力测试。
- 按 Nature 官方审稿维度评估 originality、scientific importance、interdisciplinary readership、technical soundness 和 readability。
- 在相互不可见的独立上下文中生成三份 reviewer reports，全部定稿后再单独生成 cross-review synthesis。
- 标记无支撑声称、技术缺陷、证据链断点和非专业读者理解障碍。
- 将意见明确分成 `Major Concerns` 和 `Minor Comments`；对会阻断核心论证的 Major 问题标记 `Blocking Yes`。
- 尖锐意见保持直接、专业且有证据，小问题保持具体、可执行，不为凑数量虚构问题。
- 整体文风尽量不用破折号或冒号连接句子，优先使用分句、逗号、分号、括号或另起一行的短标签；稳定编号、必要连字符和不能改动的原文格式不受影响。
- 用内部 12 轴技术清单检查覆盖范围，并为每条实质性意见绑定 claim pointer 和可核验的证据位置。
- 交叉核对手稿内部的术语、单位、数值精度、Methods 计数和表格支撑，区分语言问题与会削弱可信度的实质矛盾。
- 在三位 reviewer 报告全部冻结后，执行独立的 forensic consistency audit，检查算术恒等式、metric 上下限、聚合层级、正文与表格矛盾、重复行、离散度异常、数据来源和复现门槛；审计结果不反馈给 reviewer，也不改冻结报告。
- 不为了降低重复度而提前协调或改写审稿意见；只有至少两位 reviewer 独立提出同一问题时才在后置综合中列为共识。
- 判断哪些读者会关心这项工作，以及为什么。

## 典型请求

- “像 Nature reviewer 一样审这篇 introduction 和 Figure 1。”
- “投稿前帮我找最可能被审稿人攻击的技术问题。”
- “给我三份 reviewer reports 和一个综合判断，不要写 rebuttal。”

## 你需要提供

- 手稿全文、摘要、关键章节、图表、图注或作者说明。
- 目标期刊、学科领域和你最担心的审稿风险。
- 已有补充实验或不能新增实验的限制。

## 产出

- 三份 peer-review style reports。
- Cross-review synthesis：共识问题、分歧重点和编辑层风险。
- 带稳定编号、claim pointer、evidence pointer 和解决判据的可追溯审稿意见。
- 分级的 Major/Minor 意见、Blocking 风险和去重后的 minor revision checklist。
- 必须补强的实验、分析、叙事或图表证据清单。
- 对无证据判断的明确标记。

## 边界

- 不会虚构具体审稿人身份、专业人设或编辑决定。
- 不同 reviewer 之间不能读取、引用、赞同或回应彼此的意见；综合判断只在全部独立报告锁定后生成。
- 只基于用户提供材料和技能内官方审稿规则做保守模拟。
- 如果目标是写返修回复，优先使用 `nature-response`。

## 相关技能

- `nature-response`：把真实审稿意见转成回复包。
- `nature-writing`：根据评审风险重建手稿叙事。
- `nature-statistics`：深入审查统计设计和报告。
