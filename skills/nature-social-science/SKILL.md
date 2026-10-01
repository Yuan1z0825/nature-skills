---
name: nature-social-science
description: 社会科学及相邻学科学术写作与选题论证工作台，覆盖选题构思、文献梳理、论证组织、学术表达四大要素。Use for 找论文题目/研究问题、把兴趣或宽泛主题变成可讨论的研究方向、文献综述与领域版图、区分"研究少"与真正未决的知识问题、设计证据路线与主张边界、新颖性审计与"审稿人2"式攻击、博士/论文可行性评估、导师沟通话术、或检查论文中的过度断言与概念混用。也适用于开题报告、研究计划书、学位论文的选题阶段与论证自检。
metadata:
  author: community contribution, adapted from the "Finding a PhD Topic with Codex" workflow
---

# Nature Social Science — 社科写作与选题论证工作台

本技能将社科硕博科研选题可落地工作流（源自《Finding a PhD Topic with Codex》一文的思想）转成一套可执行的写作与自检流程，覆盖定量、质性、民族志、档案、文件、语料和数字研究。

**适用范围**：社会科学及相邻人文学科。定量、质性、民族志、档案、文件、语料和数字研究都能用。
判断标准始终相同：**问题是否清楚，证据是否匹配，主张是否诚实，项目是否能由这名研究者完成。**

**不做什么**：不替你生成一个"正确题目"，不保证新颖、录取、资助、发表或论文成功，
不把某种方法当作高质量研究的默认答案。**AI 的自信不是证据；填完的表格不是通关证明。**

---

## 一、先做路由：用户在哪个环节？

| 用户诉求 | 对应要素 | 走哪几步 | 读哪些参考 |
|---|---|---|---|
| "我想研究 XX"／"帮我找个论文题目" | 选题构思 | Step 1 → 2 → 3 | `01-foundations.md`、`02-workflow-steps1-3.md` |
| "这方向有人做过吗"／文献怎么梳理／版图怎么画 | 文献梳理 | Step 2 → 3 | `02-workflow-steps1-3.md` |
| "我有数据/我想用方法 M" | 选题构思（假起点） | 先回 Step 1 | `01-foundations.md` §六 Two false starts |
| "这个题目能不能做"／证据够不够 | 论证组织 + 可行性 | Step 4 → 7 | `03-workflow-steps4-5.md`、`04-workflow-steps6-8.md` |
| "帮我生成几个研究问题"／RQ 怎么写 | 选题构思 | Step 5 | `03-workflow-steps4-5.md` |
| "帮我想想审稿人会怎么攻击"／查新颖性 | 论证组织 | Step 6 | `04-workflow-steps6-8.md` |
| "结论是不是说过头了"／表述定级 | 学术表达 | Step 4 的 claim ceiling + 术语纪律 | `09-academic-expression.md`、`07-status-terminology.md` |
| "帮我改稿／润色论证段落" | 学术表达 | 对照 claim ceiling 与 Red flags | `09-academic-expression.md` |
| "怎么跟导师谈"／开题材料怎么写 | 交付使用 | Part III | `08-usage-handoff.md` |
| 需要现成提示词 | — | 按步骤取 | `05-prompt-library.md`（唯一权威版本） |
| 需要填表模板 | — | 按步骤取 | `06-worksheets.md` |

**入口判断（必做第一步）**：只有兴趣 → Mode A；已有宽泛主题或关系 → Mode B；
已有暂定研究问题 → Mode C（**audit route，不是 advanced route**）。
只有数据集或方法偏好时，先问"它能帮助理解什么未决现象"，答不出来从 Mode A 开始。

---

## 二、四条铁律（每条回复都要守）

1. **不知道的地方写"未知"，不要让 AI 补猜。**
2. **主动找矛盾、零结果、反向关系和替代解释**——不是找支持起点的材料。
3. **保留证据层级、证据状态、失败搜索和关键未知**，不把它们抹平成一个乐观结论。
4. **每步结束后更新 `Current Research State`，不要把整段旧对话带进下一步。**

配套禁止项（写进每一次给出的提示词里）：

- 不要生成选题、题目或假设（在尚未到那一步时）；
- 不要声称存在研究空白或新颖性；
- 不要默认使用定量、定性、因果或任何特定方法；
- 不要把"本轮没找到"写成"没有研究"；
- 不要把个人兴趣写成已经得到证明的学术重要性；
- 不要编造引文、来源或结果。

---

## 三、十二个判断（写作自检红线）

任何一次关于选题或论证的判断，先过这张表。完整版见 `01-foundations.md` §四。

| 不要混为一谈 | 可操作的检查 |
|---|---|
| Interest ≠ Topic | 是否已经划出要探索的现象、过程和边界？ |
| Topic ≠ Research problem | 是否指出领域中具体哪里解释不通？ |
| Research problem ≠ Research question | 是否把知识困难变成可由证据推进的任务？ |
| Research gap ≠ "few studies" | 研究少造成了什么知识后果？ |
| Novelty ≠ nobody has studied it | 是否解决矛盾、机制、测量或新近可回答的问题？ |
| Interesting ≠ Important | 除了个人兴趣，答案会改变谁对什么的理解？ |
| Important ≠ Answerable | 是否有合适、合规且时间匹配的证据？ |
| Available source ≠ Valid evidence | 字段、文本或观察真的对应目标概念吗？ |
| Correlation ≠ Mechanism | 是否看见过程，还是只看见现象同时出现？ |
| Advanced method ≠ Strong contribution | 方法是否解决了原来的知识困难？ |
| Feasible study ≠ PhD-worthy project | 它能否支撑一个核心谜题与连贯发展？ |
| AI judgement ≠ Researcher judgement | 哪些决定需要用户的价值、经验和导师判断？ |

---

## 四、八步工作流一页速览

| Step | 主产物 | 决策问题 | Gate |
|---|---|---|---|
| 1. Research Search Space | 一页搜索空间 | 概念与边界是否足以搜索？ | PASS / REVISE / STOP |
| 2. Research Landscape | 领域版图 | 是否看见多种问题、解释和反证？ | 同上 |
| 3. Unresolved Problems | 3–7 个问题卡 | 是否存在有后果的知识不确定性？ | 同上 |
| 4. Evidence Map | 1–3 条证据路线 | 是否能观察核心问题并守住主张上限？ | 同上 |
| 5. Candidate RQs | 6–12 张候选卡 | 是否有实质不同、可被攻击的问句？ | 同上（起用 PARK） |
| 6. Academic Survival | Novelty Audit + Reviewer 2 | 候选是否经学术攻击仍存活？ | 同上 |
| 7. PhD Feasibility | 可行性档案 | 是否没有未处理硬失败，且能发展成博士？ | 同上 |
| 8. Final Shortlist | 最多三张 Topic Cards | 能否清楚说明取舍和下一项核实？ | 同上 |

> Step 5 会短暂扩展候选、随后收窄，**这不是纯线性管道**。

**回退规则**：若设计只能提供弱代理、错误单位或不合适时间 → 返回 Question；
若连问题的知识后果也消失 → 返回 Problem。

---

## 五、五套状态系统（不要合成一个分数）

| 在问什么 | 用哪套 | 取值 |
|---|---|---|
| 我能进入下一步吗？ | **Workflow Gate** | PASS / REVISE / STOP（+ PARK） |
| 这条证据路线核实到哪了？ | **Evidence State** | NAMED / DOCUMENTED / ACCESS-CONFIRMED / TESTED |
| 这条候选经学术攻击后怎样？ | **Academic Survival** | SURVIVE / REDESIGN / PARK / REJECT |
| 这项硬条件现在什么状态？ | **PhD Feasibility Dependency** | CONFIRMED / RESOLVABLE DEPENDENCY / UNKNOWN / FAIL |
| 这条候选能进最终比较吗？ | **PhD Feasibility Disposition** | PROCEED TO COMPARISON / REDESIGN / PARK / REJECT |

**六条不许抹平的不等式**：

- `UNKNOWN ≠ PASS` — 未知需要核实动作，不是乐观解释。
- `DOCUMENTED ≠ ACCESS-CONFIRMED` — 官方文件说来源存在，不等于用户已满足资格、许可、地点、费用和伦理条件。
- `SURVIVE ≠ novel` — 通过一次有界攻击，不等于证明全世界没有近似研究。
- `PARK ≠ bad idea` — 缺的是决定性证据或条件，不是想法本身。
- `PASS ≠ permanent approval` — 新文献、访问变化、伦理意见、实测结果都可能把它变成 REVISE 或 STOP。
- `REJECT ≠ wasted work` — 拒绝记录保存了最近似工作、失败条件和边界，能阻止以后重复同一错误。

**不要创建"综合状态"。** 一条候选完全可以同时是：
Step 6 SURVIVE、证据 DOCUMENTED、访问依赖 UNKNOWN、Step 7 处置 PARK、本步 Gate REVISE。
这些标签并不矛盾，它们回答不同问题。详见 `07-status-terminology.md`。

---

## 六、工作节奏（每一步重复这五拍）

1. 读当前章节，确认本步的**目的和 Gate**；
2. 在 `05-prompt-library.md` 找到对应 prompt，只准备 `Required input`；
3. 把输出写进 `06-worksheets.md` 里的对应表格，**不把长对话当作最终记录**；
4. 用质量检查和 Red flags 审阅结果；**需要真人判断时停下**；
5. 更新 `Current Research State`，再按 `08-usage-handoff.md` 进入下一步或暂时退出。

**上下文控制**：每次转段只带 `Carry forward` 的内容，主动丢弃 `Leave behind`。
`08-usage-handoff.md` 给出了九次交接各自该带什么、丢什么、哪项判断必须由用户作出、
以及哪类未知会阻塞推进。

---

## 七、什么时候必须停下来找真人

当你无法判断争论在本学科中的分量、关键全文或资料说明无法取得、研究涉及敏感参与者或高风险材料、
方法学习成本不清楚，或项目依赖某位导师、机构与资料提供者时——**把当前卡片交给合适的人**。

AI 可以帮你准备问题，**不能替他们授权**。

需要交给真人的典型场景与方法，见 `08-usage-handoff.md` 与 `01-foundations.md` §五「什么时候找真人」。

---

## 八、使用约定

- **提示词里的称谓**：`05-prompt-library.md` 中的提示词为**逐字保留**原件，正文里自称"我正在使用 Codex"。
  直接复制即可；若在别的 agent 里使用，可把 `Codex` 替换为当前助手的名字，其余一字不改。
- **提示词的唯一权威版本是 `05-prompt-library.md`**。各步骤文件里的"短预览"只作说明，不要另造一版并行维护。
- **Quick / Deep 分层**：Step 2、4、6、7 提供 Quick Run 与 Deep Run 两档。
  Quick Run 减少首轮工作量，**不降低证据、伦理、访问或 hard-failure 标准**。
- **不要把长对话当记录**：所有结论必须落进 `06-worksheets.md` 的对应表格与 `Current Research State`。
- **不确定的一律写"未知"**，不要接受任何一方（包括你自己）的乐观补全。

---

## 九、参考文件索引

以下九个文件均位于本 skill 的 `references/` 目录下，按需只读当前步骤需要的那个。

| 文件 | 内容 |
|---|---|
| `01-foundations.md` | 核心概念、六个易混概念、十二个判断、能力边界、证据层级、三种入口模式、Gate 定义、Funnel |
| `02-workflow-steps1-3.md` | Step 1 搜索空间 / Step 2 领域版图（文献梳理核心）/ Step 3 未决问题 |
| `03-workflow-steps4-5.md` | Step 4 证据地图与 claim ceiling / Step 5 候选研究问题 |
| `04-workflow-steps6-8.md` | Step 6 学术攻击（Novelty Audit + Reviewer 2）/ Step 7 可行性 / Step 8 最终短名单 |
| `05-prompt-library.md` | 全部可复制提示词（**唯一权威版本**） |
| `06-worksheets.md` | 11 份工作表模板 |
| `07-status-terminology.md` | 五套状态系统 + 术语小词典 + Current Research State |
| `08-usage-handoff.md` | 短名单使用、导师沟通、九次交接、恢复规则 |
| `09-academic-expression.md` | **学术表达纪律**：主张上限、动词与证据相称、诚实措辞句式表、各步 Red flags（起草与改稿时必读） |

**使用时只做四件事**：不知道的写"未知"；要求找反证；保留证据层级与失败记录；每步更新状态表。
