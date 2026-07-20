---
name: researchwrite
description: |
  Proposal-first scientific writing pipeline. Three modes (compose/revise/hybrid) with four-layer QA pipeline. Enforces evidence-before-prose, argument-before-sections, and contracts-before-paragraphs.
license: MIT
metadata:
  hermes:
    tags: [research, writing, proposal, revision, qa, multi-agent]
    related_skills: [brainstorming, professor, avoid-ai-writing, docx]
---

# researchwrite — proposal-first 科研写作 pipeline

受 autonovel（状态机+打分）、professor（动态专家）、brainstorming（入口追问）、anti-AI-writing（语言清理）启发的科研写作状态机。**不是通用"帮我写论文"prompt。**

## 核心原则

1. **证据先于文字** — 起草前必须建立或读取 `research_canon` 和 `evidence_table`
2. **论证先于章节** — 写正文前必须完成 `argument_map`
3. **契约先于段落** — 每节需要 purpose / allowed claims / forbidden claims / inputs / validation
4. **范围先于完备** — 如果是分阶段写作，先锁定阶段边界
5. **动态专家，不设固定池** — 用 `professor` 按失败模式召唤对应专家
6. **内容先于语言** — 诊断科学逻辑后再做 anti-slop / 语言打磨
7. **不自动升级事实** — 永远不把 "may indicate" 改成 "proves"，除非有证据支撑
8. **删除胜于解释** — 当某主张不可行，直接删除。正文干净，解释留给答辩
9. **该停就停** — 平台期、专家冲突、证据缺失是停止理由，不是润色理由

## 模式分派

| 输入 | 模式 |
|---|---|
| 题目、方向、模糊想法 | `compose` — 加载 `references/compose-mode.md` |
| 已有段落/章节/完整 proposal | `revise` — 加载 `references/revise-mode.md` |
| 已有草稿 + 扩写/补写/重构 | `hybrid` — 加载 `references/hybrid-mode.md` |

模糊时推断默认模式。只在选择会改变工作流时才问用户。

## 项目结构

**工作目录**：`<outputs>/researchwrite/<project-slug>/`

**标准文件**：

```
00_scope.md              写作任务边界
01_research_canon.md     硬事实和约束
02_evidence_table.md      claim → evidence 映射表
03_argument_map.md        论证架构
04_section_contracts.md   每节的 purpose / inputs / allowed & forbidden claims
05_style_guide.md         风格、术语、禁用表达
state.json                项目状态（mode、round、scores、technical_debts）
sources/                  用户材料、文献、数据
drafts/                   草稿和分节文件
revision_briefs/          修订简报
qa_logs/                  诊断、专家审查、anti-slop、打分记录
exports/                  最终输出（.md + .docx）
```

新建项目时从 `templates/` 取空模板。`references/worked-example-quaternary-proposal.md` 提供了基于通用材料科学领域的完整填写示例。

## Reference 文件索引

完整 reference 按任务需要加载，不要一次性注入全部文件：

| Reference | 加载时机 |
|---|---|
| `references/compose-mode.md` | 模式 = compose（9 步流程） |
| `references/revise-mode.md` | 模式 = revise（9 步流程） |
| `references/hybrid-mode.md` | 模式 = hybrid |
| `references/evaluation-rubric.md` | 使用 8 维 × 4 锚点评分体系时 |
| `references/research-anti-slop.md` | 清理中文 proposal 的模板化和空泛表达时 |
| `references/chinese-review-writing-style.md` | 撰写或修订中文综述时 |
| `references/stopping-rules.md` | 判断继续迭代、拆分范围或停止时 |
| `references/professor-dispatch.md` | 按失败模式分派动态专家时 |
| `references/foundation-files.md` | 建立或修复 foundation 五文件时 |
| `references/project-structure.md` | 初始化项目目录或维护 `state.json` 时 |
| `references/export-archive.md` | 导出和归档 `.md` / `.docx` 时 |
| `references/partial-proposal-scope.md` | 分阶段写作并防止范围蔓延时 |
| `references/ref-renumbering-cascade.md` | 处理参考文献增删和编号级联时 |
| `references/review-paper-framework.md` | 设计综述论文框架时 |
| `references/review-critique-methodology.md` | 建立综述的批判性分析时 |
| `references/validation-checklist.md` | 自动检查主张、引用、编号和可复现性时 |
| `references/gpt-handoff-revision-brief.md` | 生成跨 agent 修订交接简报时 |
| `references/within-approved-proposal.md` | 在已批准的 proposal 框架内扩写时 |
| `references/worked-example-quaternary-proposal.md` | 需要查看完整 foundation 文件填写示例时 |
| `references/降承诺提案模式.md` | 证据不足，需要降低承诺强度时 |

## 运行交付

每次运行结束时输出：

1. 当前文件路径或修订后文本
2. 当前分数/状态
3. 剩余风险
4. 一条建议的下一步

## QA Mode — 四层质量保障 Pipeline

当用户说"审查这段/跑 QA/检查方案/过 pipeline"时，进入 QA 模式。

### 情境挡位

| 挡位 | 适用场景 | 阈值 |
|------|---------|------|
| `paper` | 投稿论文 | 7.0 |
| `proposal` | 研究方案/开题 | 7.0 |
| `internal` | 内部汇报/周报 | 5.0 |
| `quick` | 快速扫读 | 无 |

### Pipeline 顺序（先内容后语言）

```
Gate 2: professor Convener（内容层）
  ├── 论文 → 方法论专家 + 领域专家
  ├── proposal → 可行性专家 + 创新性专家
  └── 文献综述 → 覆盖面专家 + 批判深度专家
  │
  ▼
Gate 1: avoid-ai-writing 模式 detect-only
  └── 只对英文有效，中文跳过或降级为手工扫读
  │
  ▼
Gate 3: auto-validation（格式/完整性层）
  └── 每个 claim 有 citation？方法可复现？编号连续？
  │
  ▼
Gate 4: 评分阈值（分维度打分）
  ├── 总分≥阈值 → 通过 ✅
  └── 总分<阈值 → 按低分维度定向回退（不超过 3 轮）
```

**Gate 2 在 Gate 1 之前** — 避免改了句子后被专家打回重写。

### 使用方法

```
用户: "用 researchwrite 审查这段 discussion，paper 挡位"
  → 自动走 Gate 2 → Gate 1 → Gate 3 → Gate 4
  → 返回审查报告 + 定向修改建议

用户: "快速扫一下这个邮件"
  → 走 quick 挡位，只标记 P0 问题
```

## 配置你的研究域

首次使用告诉 agent 你的研究背景，agent 会调用 `professor` 建立领域专家知识。后续写作中专家审查会基于你的领域。
