# `nature-polishing` 技能

[English](README_EN.md)

`nature-polishing` 用于把学术手稿文本润色、重构或翻译成更接近 Nature 风格的简洁英文，同时保持作者原意、证据边界和引用意图。

## 适合用它做什么

- 将中文学术段落翻译为投稿可用英文。
- 精简冗长句子，增强论证顺序和段落推进。
- 按 Nature / Nature Communications / Nature Machine Intelligence 论文范式调整摘要、引言、结果、讨论或标题。
- 对 NMI 识别独立路由，检查 3,500 词正文、150 词摘要、6 个 display、代码审查与会议论文实质扩展，不再误用旗舰 Nature 数字。
- 区分 research paper 与 methods paper 的写作重点。
- 检查 AI 味、夸张声称、过度因果表达和不自然搭配。
- 对全文或多轮修改稿执行一致性扫描，定位术语、单位、数值精度和内部声称漂移。
- 对 Results 执行主文必要性审计：区分核心发现、必要支撑与稳健性/异质性/替代推断，分配到主文、图注或 SI；每次新增文字都触发删除或替换检查。

## 方法来源

- 写作策略：学术写作课程笔记中的沙漏结构、读者工作流和章节职责。
- 发表论文模式：精选 Nature 与 Nature Communications 文章的 section moves。
- 短语支持：Academic Phrasebank 中适合学术论文的表达族。

## 典型请求

- “把这段中文结果翻译成 Nature 风格英文，保持克制。”
- “润色 abstract，不要改变事实和引用意图。”
- “这段 introduction 太像 AI 写的，帮我重构逻辑和语言。”

## 你需要提供

- 原文、目标章节、论文类型和希望保留的术语。
- 不能改变的事实、数据、引用和专有表达。
- 期望输出：只给改写版，还是给修改说明和风险标记。

## 产出

- 可粘贴的英文改写或中英对照版本。
- 关键修改说明：逻辑重排、语气收敛、术语统一和声称边界。
- 全文一致性风险清单；机械扫描结果逐条回到上下文确认后再修改。
- 主文压缩任务可附结果分配表、删除记录、统计位置记录和 claim repetition map。
- 需要作者确认的事实或引用意图。

## 边界

- 不会替作者新增结果、机制、统计意义或未给出的引用。
- 不会为了更像 Nature 而夸大 novelty、causality 或 generality。
- 如果需要从零搭建论文章节，优先使用 `nature-writing`。

## 相关技能

- `nature-writing`：章节级起草和论证重建。
- `nature-response`：返修回复信和 cover letter 语言。
- `nature-statistics`：统计文本、图注和审稿统计回复。
