<div align="center">
  <p>
    <img src="assets/readme-banner-cn.png" alt="Nature Skills：面向全球学者的科研 Skill 库" width="100%">
  </p>
  <p>
    <a href="LICENSE"><img alt="License" src="https://img.shields.io/badge/license-Apache--2.0-2ea44f"></a>
    <a href="#安装"><img alt="Install" src="https://img.shields.io/badge/install-Claude%20Code%20%7C%20Codex%20%7C%20OpenClaw%20%7C%20OpenCode%20%7C%20Hermes-111827"></a>
    <a href="#技能索引"><img alt="Skills" src="https://img.shields.io/badge/skills-17-0ea5e9"></a>
    <a href="README_EN.md"><img alt="Language" src="https://img.shields.io/badge/language-中文%20%7C%20English-1f6feb"></a>
  </p>
  <p>
    <a href="#安装">立即安装</a>
    · <a href="#快速开始">快速开始</a>
    · <a href="#技能索引">技能索引</a>
    · <a href="docs/open-source-agent-frameworks.md">其他安装</a>
    · <a href="#共享设计原则">设计原则</a>
    · <a href="#新增技能">贡献方式</a>
    · <a href="README_EN.md">English</a>
  </p>
</div>

---

* 大家好，我是 nature skills 的创立者袁一哲。感谢大家持续关注 `nature-skills`。我们在抖音更新了很多视频教程，大家可以根据名称检索查看，希望真心能够帮助到大家。
* 如果你有任何需求，欢迎提交 issue；如果我们认为该需求有意义且可行，会尽量推进实现。我们也欢迎 PR，但请按照本文后面的贡献格式提交，方便更高效地审核与合并。
* 面向全球AI学者收录通用科研skill，nature-skills是skill期刊的雏形，不以讲故事假大空的科研为目标，这里只在乎能否真正解决领域问题！
* 知识星球名称：Nature Skills以及背后的哲学！

## 快速开始

安装完成后，可以直接把论文、段落、审稿意见或任务描述交给 agent。下面这些提示词可以直接复制使用：

| 想做什么 | 直接这样说 |
| --- | --- |
| 读论文 / 中英文对照 | `把这篇 PDF 做成图文对应的中英文对照 Markdown reader。` |
| 生成文献汇报 PPT | `把这篇论文做成中文组会汇报 PPT，保留关键图件和来源标注。` |
| 润色或翻译论文段落 | `把这段中文改写成 Nature 风格英文，保持学术含义不变。` |
| 写摘要、引言或讨论 | `根据这些结果和图件，帮我起草 Nature 风格的摘要和引言。` |
| 预投稿审稿模拟 | `从 Nature 审稿人视角评估这篇稿件，给出三份 reviewer reports。` |
| 回复审稿意见 | `根据这封返修邮件，帮我写逐点回复、cover letter，并标出修改稿需要标红的位置。` |
| 查文献、他引和引用者画像 | `整理这篇文章的引用数、严格他引数、DOI，并看引用者里有没有院士、Fellow 或领域大牛。` |
| 做科研图或论文示意图 | `根据这段方法和结果，帮我生成投稿级科研图或论文示意图草稿。` |

如果你不确定该用哪个技能，直接描述任务即可；如果你已经知道技能名，可以在提示词里明确写“使用 `nature-reader`”或“使用 `nature-response`”。

## 主要贡献者

* **袁一哲**：`nature-skills` 创立者。
* **马昕瑞**：本项目第二贡献者，现为东南大学土木工程学院博士研究生，主要专注于深度学习，以及使用 agent 在结构设计领域开展研究。
  * GitHub: [Travisma2233](https://github.com/Travisma2233)
  * Email: [travisma2233@gmail.com](mailto:travisma2233@gmail.com)
  * Google Scholar: [Xin-Rui Ma](https://scholar.google.com/citations?user=CDydADoAAAAJ&hl=en)
  * ResearchGate: [Xin-Rui Ma](https://www.researchgate.net/profile/Xin-Rui-Ma?ev=hdr_xprf)


# 自己的一些浅薄观点
* 最近发现，我设计的Nature-skills被谷歌DeepMind关注并借鉴，他们参考了其中的引用体系、脚本思路以及技能设计哲学，推出了Science-skills。说实话，这让我挺欣慰的——当国外的顶尖AI机构开始从我们的工作中汲取灵感时，说明中国开发者的原创思想正在被世界看见。这不是被复制的失落，而是中国力量在开源土壤里生根后，自然向外生长出的影响力。
* 我们设计Skills的重心，从来不是要求每个人都来啃透这套思想，而是这套思想本身就具备被机器理解并复用的能力。你如果想创立一个全新的Skill，或者把它适配到自己的专属领域，根本不需要从头学起——直接把Nature-Skills的GitHub地址发给Codex，它就能自动学习其中的设计精髓，帮你完成新Skill的创建和修改。这才是思想的真正解放：它不再依赖口口相传，而是通过AI直接流淌进每一个需要它的角落。
* Nature-Skills真正的价值，或许并不在于那些具体的技能模块，而在于它悄悄推开了一扇新的大门——它让很多人第一次意识到，原来可以借助Codex或智能体来操控本地电脑做科研。我有幸见证并陪伴了许多人完成了科研范式的转变，当他们惊叹‘原来科研还可以这样去做’的那一刻，这种认知上的破壁和解放，远比Skills本身更让我觉得有意义。它不是一个工具的成功，而是一种新的思考方式开始在人群中蔓延。
* 在当下，几乎所有实用的工具，都可以被提炼为标准化的流程，而标准化的流程，恰好就能封装成可复用的技能。

<table>
  <tr>
    <td align="center">
      <b>视频教程请关注抖音</b><br>
      <img width="300" alt="635611d42c5739d8a98ea08eec010d30" src="https://github.com/user-attachments/assets/37d4b0b6-3d22-4492-bb01-c0d9bae5a9e0" />
    </td>
    <td align="center">
      <b>知识星球50¥/年</b><br>
      <img width="300" alt="aaa39bcfddacc2d92a5922b50b5edf46" src="https://github.com/user-attachments/assets/7a7e467a-59d4-4514-9b42-eefd01bf9591" />
    </td> 
    <td align="center">
      <b>Agent科研交流群</b><br>
      <img width="300" alt="Agent科研交流群" src="https://github.com/user-attachments/assets/28d1886a-69be-46bc-a1cb-777d7510ddab" />
    </td>
  </tr>
</table>

---

## 安装

`nature-skills` 是一组围绕 `SKILL.md` 组织的可复用技能包。`skills/` 下的每个顶层技能目录都是一个可安装单元，例如 `nature-*`；`skills/_shared/` 是共享内容目录，安装完整仓库时也需要保留。

### Claude Code 安装方式

Claude Code 不能直接使用 `scripts/update-codex-skills.sh`，因为这个脚本只负责同步到 Codex 的 `~/.codex/skills/`。用于 Claude Code 时，推荐保留一个稳定的本地 clone，再用 subagent 或 slash command 指向真实的 `skills/*/SKILL.md`。这样不会破坏技能目录结构，也能继续读取 `references/`、`static/`、`manifest.yaml`、脚本、资产和 `skills/_shared/`。

如果还没有安装 Claude Code：

```bash
npm install -g @anthropic-ai/claude-code
claude
```

先把仓库 clone 到一个稳定路径：

```bash
mkdir -p ~/ai-skills
cd ~/ai-skills
git clone https://github.com/Yuan1z0825/nature-skills.git
```

推荐方式：为常用技能创建 Claude Code subagent wrapper。以 `nature-reader` 为例：

```bash
mkdir -p ~/.claude/agents
cat > ~/.claude/agents/nature-reader.md <<'EOF'
---
name: nature-reader
description: Use for Chinese-English paper reading, figure-aware translation, and source-grounded paper notes.
---

When invoked, first read `~/ai-skills/nature-skills/skills/nature-reader/SKILL.md` and follow it as the governing workflow.
Read supporting files from `~/ai-skills/nature-skills/skills/nature-reader/` and `~/ai-skills/nature-skills/skills/_shared/` only when needed.
Do not replace this skill with a generic paper-reading response.
EOF
```

然后开启新的 Claude Code 会话，直接请求使用这个 subagent：

```text
Use the nature-reader subagent to turn this paper into a Chinese-English Markdown reader.
```

如果你更喜欢 slash command，也可以创建命令 wrapper：

```bash
mkdir -p ~/.claude/commands
cat > ~/.claude/commands/nature-reader.md <<'EOF'
Read `~/ai-skills/nature-skills/skills/nature-reader/SKILL.md` first and follow it strictly.
Read directly needed supporting files from `~/ai-skills/nature-skills/skills/nature-reader/` and `~/ai-skills/nature-skills/skills/_shared/`.

$ARGUMENTS
EOF
```

在 Claude Code 中使用：

```text
/nature-reader 把这篇论文做成中英文对照的完整 Markdown reader。
```

安装其他技能时，把示例中的 `nature-reader` 换成对应目录名即可，例如 `nature-polishing`、`nature-writing`、`nature-reviewer`、`nature-response` 或 `nature-figure`。后续更新只需要：

```bash
cd ~/ai-skills/nature-skills
git pull
```

只要 wrapper 仍然指向这个稳定 clone 路径，就不需要重复复制技能文件。

### Codex 推荐安装方式

推荐使用仓库自带脚本安装或更新 Codex skills。脚本会同步 `skills/` 下所有顶层技能目录，并在复制后做 `diff` 验证；它不会覆盖其他无关 Codex skills。

```bash
git clone https://github.com/Yuan1z0825/nature-skills.git
cd nature-skills
scripts/update-codex-skills.sh --pull
```

如果已经 clone 过仓库：

```bash
cd nature-skills
scripts/update-codex-skills.sh --pull
```

验证当前 Codex 安装是否和这个 checkout 一致：

```bash
scripts/update-codex-skills.sh --check
```

如果你长期用这个脚本更新，并希望清理上游已经删除的旧技能目录：

```bash
scripts/update-codex-skills.sh --pull --prune
```

`--prune` 只会删除以前由这个脚本记录过、但当前仓库已经不再包含的目录。第一次运行没有历史记录时，它不会猜测删除旧目录。

也可以把仓库链接交给 Codex，让 Codex 执行安装脚本。推荐提示词：

```text
请从这个仓库安装 Codex skills：
https://github.com/Yuan1z0825/nature-skills.git

请 clone 仓库后运行 scripts/update-codex-skills.sh --pull。
安装后再运行 scripts/update-codex-skills.sh --check 验证。
请保留 skills/ 下的完整技能目录，不要只复制 SKILL.md。
```

如果只安装单个技能，请明确说明技能名：

```text
只安装这个仓库里的 nature-reader：
https://github.com/Yuan1z0825/nature-skills.git

如果该技能需要共享文件，也请一并安装 skills/_shared。
```

关键规则：保留完整目录结构。请复制或引用整个技能文件夹，而不是只复制 `SKILL.md`，因为许多技能依赖 `references/`、`static/`、`manifest.yaml`、脚本、资产或共享文件。

安装脚本不会自动安装 Python 依赖。需要使用相关脚本或 MCP 服务时，再按需安装：

```bash
python -m pip install -r skills/nature-paper-to-patent/requirements.txt
python -m pip install -r skills/nature-academic-search/mcp-server/requirements.txt
```

`nature-academic-search` 的 MCP 服务还需要单独配置 `PUBMED_EMAIL`，Scopus / ScienceDirect 等可选 provider 需要使用本机凭据配置，不要把 API key 写入仓库文件。

安装后，请开启一个新的 Codex 会话，然后自然描述任务，例如：

```text
把这篇论文做成中英文对照的完整 Markdown reader。
```

```text
把这篇论文做成中文PPT。
```

如果你使用 OpenClaw、OpenCode、Hermes 等开源 agent / 编程框架，请看 [OpenClaw / OpenCode / Hermes 接入教程](docs/open-source-agent-frameworks.md)。


### 目录结构

```text
skills/
├── _shared/              # 当技能引用 ../_shared 时需要保留
├── nature-<topic>/
│   ├── README.md
│   ├── README_EN.md
│   ├── SKILL.md
│   ├── manifest.yaml     # router-style 技能会包含
│   ├── static/           # router-style 技能会包含
│   └── references/...
└── nature-proposal-writer/
    ├── README.md
    ├── README_EN.md
    ├── SKILL.md
    ├── scripts/...
    ├── templates/...
    └── references/...
```

### 其他 agent 场景

OpenClaw、OpenCode、Hermes 的具体接入方式见 [OpenClaw / OpenCode / Hermes 接入教程](docs/open-source-agent-frameworks.md)。

用于其他 agent 时，建议保留一个稳定的仓库 clone，再创建轻量 subagent、slash command 或 custom prompt wrapper，指向真实的 `skills/*/SKILL.md`，并保留 `skills/_shared/`。

手动或其他 agent 使用时：

1. 将完整技能目录复制到你的 prompt library 或项目中。
2. 保留 `SKILL.md`、`manifest.yaml`、`static/`、`references/`、脚本、资产和需要的 `skills/_shared/` 文件。
3. 如目标 agent 有自己的格式要求，可调整 frontmatter 和正文结构。

## Star 历史

[![Star History Chart](https://api.star-history.com/svg?repos=Yuan1z0825/nature-skills&type=Date&cache_bust=2026-06-07T16)](https://star-history.com/#Yuan1z0825/nature-skills&Date)

## 技能索引

当前 `skills/` 下包含以下可触发技能；`skills/_shared/` 是共享内容目录，不计入技能索引。点击技能名或“详情页”可以进入每个 skill 的单独说明页面。

| 技能 | 状态 | 用途 | 触发词 | 详情页 |
|-------|--------|---------|-----------------|--------|
| [`nature-figure`](skills/nature-figure/README.md) | Stable | 面向 Nature / 高影响力期刊的 Python 或 R 投稿级科研图工作流，内置 figures4papers demo，并支持通过 OpenRouter GPT Image 2 生成论文示意图草稿 | “Nature figure”, “投稿级图片”, “publication plot”, “scientific figure”, “figures4papers”, “论文示意图”, “GPT Image 2” | [详情](skills/nature-figure/README.md) |
| [`nature-polishing`](skills/nature-polishing/README.md) | Stable | 将学术文本润色、重构或翻译为 Nature 风格英文 | “Nature style”, “润色”, “academic writing”, “论文英文” | [详情](skills/nature-polishing/README.md) |
| [`nature-writing`](skills/nature-writing/README.md) | Draft | 起草 Nature 风格手稿章节，并重建论文论证 | “Nature writing”, “写摘要”, “写引言”, “manuscript draft”, “论文写作” | [详情](skills/nature-writing/README.md) |
| [`nature-reviewer`](skills/nature-reviewer/README.md) | Draft | 从审稿人视角模拟 Nature 风格评审，输出三份 reviewer reports 和综合意见 | “Nature reviewer”, “预投稿评审”, “reviewer report”, “审稿人视角评估” | [详情](skills/nature-reviewer/README.md) |
| [`nature-citation`](skills/nature-citation/README.md) | Beta | 检索严格限定在 Nature / CNS 系列的支撑文献，并导出 ENW、RIS 或 Zotero RDF | “Nature citation”, “CNS citation”, “分段引用”, “支撑文献”, “Zotero RDF” | [详情](skills/nature-citation/README.md) |
| [`nature-data`](skills/nature-data/README.md) | Draft | 准备 Data Availability statement、数据仓储方案和 FAIR 检查 | “Data Availability”, “数据可用性”, “repository”, “FAIR metadata” | [详情](skills/nature-data/README.md) |
| [`nature-statistics`](skills/nature-statistics/README.md) | Draft | 审查、改写或起草 Nature / 高影响力期刊投稿中的统计报告，覆盖样本量、独立分析单位、重复数、p 值、多重比较、效应量、置信区间、图注统计和审稿人统计意见 | “Nature statistics”, “统计审查”, “statistical analysis”, “p value”, “sample size”, “replicates”, “multiple comparisons”, “图注统计”, “统计分析小节” | [详情](skills/nature-statistics/README.md) |
| [`nature-reader`](skills/nature-reader/README.md) | Beta | 生成带来源锚点、图文对应和中英文对照的全文 Markdown reader | “nature reader”, “全文 Markdown”, “原文对照”, “图文对应”, “全文翻译” | [详情](skills/nature-reader/README.md) |
| [`nature-response`](skills/nature-response/README.md) | Beta | 解析返修邮件，起草、审查和修改返修 cover letter、逐点回复审稿人的 response letter、标红修改稿，并提供 LaTeX 模板 | “response to reviewers”, “rebuttal letter”, “cover letter”, “major revision”, “返修邮件”, “审稿意见回复”, “修回信”, “LaTeX 模板” | [详情](skills/nature-response/README.md) |
| [`nature-paper2ppt`](skills/nature-paper2ppt/README.md) | Beta | 从科研论文生成中文 PPTX 文献汇报 deck | “paper PPT”, “journal club”, “paper to slides”, “论文汇报” | [详情](skills/nature-paper2ppt/README.md) |
| [`nature-paper-to-patent`](skills/nature-paper-to-patent/README.md) | Beta | 从论文、技术报告或项目材料生成有证据约束的中国发明专利草稿 | “paper to patent”, “Chinese patent”, “论文转专利”, “权利要求书” | [详情](skills/nature-paper-to-patent/README.md) |
| [`nature-ref-verifier`](skills/nature-ref-verifier/README.md) | Beta | 参考文献多源交叉验证：逐字段对比作者/标题/年份/卷期/页码，标记卷年冲突、作者编造、页码偏差等 | “verify refs”, “校验文献”, “check references”, “文献验证”, “ref check” | [详情](skills/nature-ref-verifier/README.md) |
| [`nature-academic-search`](skills/nature-academic-search/README.md) | Beta | 多源文献检索、引用核验、严格他引审计、文章引用指标表、高影响力引用者画像和参考文献管理 | “search papers”, “find articles”, “literature search”, “查文献”, “verify DOI”, “严格他引”, “文章引用表”, “引用我的文章的人有没有大牛” | [详情](skills/nature-academic-search/README.md) |
| [`nature-downloader`](skills/nature-downloader/README.md) | Beta | 通过图书馆资源入口、Chrome 登录态和开放获取路径合法获取学术全文/PDF | “download papers”, “图书馆下载文献”, “CARSI”, “Web of Science”, “PDF 下载” | [详情](skills/nature-downloader/README.md) |
| [`nature-literature-pipeline`](skills/nature-literature-pipeline/README.md) | Stable | 自动化文献发现管线：多源检索、六维评分、精读推送和本地归档 | “literature pipeline”, “每日文献”, “文献推送”, “daily literature push”, “cron” | [详情](skills/nature-literature-pipeline/README.md) |
| [`nature-experiment-log`](skills/nature-experiment-log/README.md) | Draft | 标准化记录实验图片、语音和文字材料，生成带 YAML frontmatter 的 Obsidian 实验日志并归档原始材料 | “实验日志”, “记录实验”, “experiment log”, “Obsidian vault”, “飞书科研群” | [详情](skills/nature-experiment-log/README.md) |
| [`nature-proposal-writer`](skills/nature-proposal-writer/README.md) | Beta | proposal-first 科研写作状态机，先建立证据、论证和章节契约，再起草或审查文本 | “researchwrite”, “proposal”, “开题报告”, “研究方案”, “科研写作 QA” | [详情](skills/nature-proposal-writer/README.md) |

---

## 共享设计原则

所有技能都遵守以下原则：

1. **优先使用一手来源**：规则基于已发表 Nature 内容、官方期刊指南或明确的本地来源，而不是泛泛审美偏好。
2. **显式胜过隐式**：每条规则都应说明理由，而不是只给断言。
3. **感知章节与任务上下文**：学术写作、图件、引用和回复都依赖上下文；不同论文部分使用不同逻辑。
4. **输出优先**：每个技能都应返回能直接使用的产物，例如可粘贴文本、`.svg`、`.pptx`、`.docx` 或具体建议。
5. **可扩展**：每个技能自包含在自己的目录中，新增技能不应要求修改既有技能。

---

## 新增技能

向本仓库添加技能时，请按以下流程：

### 1. 创建目录

```text
skills/nature-<topic>/
```

### 2. 最低文件要求

| 文件 | 是否必需 | 用途 |
|------|----------|------|
| `SKILL.md` | 必需 | frontmatter（`name`、`description`）+ 规则 + 工作流；触发后由 agent 加载 |
| `README.md` | 必需 | 面向人的中文说明文档 |
| `README_EN.md` | 必需 | 与中文详情页配套的英文说明文档 |
| `references/*.md` | 复杂技能推荐 | 模块化规则文件，例如 API、设计理论、教程、图表类型等 |

建议每个 `README.md` / `README_EN.md` 尽量使用统一的信息结构，方便用户点进详情页后快速判断能不能用：

```markdown
# nature-<topic>

## 它能做什么
## 适合什么时候用
## 你可以直接这样问
## 输入需要什么
## 输出会是什么
## 依赖 / API Key / 本地环境
## 常见问题
## 相关技能
```

### 3. `SKILL.md` frontmatter 模板

```yaml
---
name: nature-<topic>
description: >-
  用一句话说明这个技能做什么、什么时候触发、主要输出格式和核心使用场景。
---
```

### 4. 更新技能索引

在上方 [技能索引](#技能索引) 表格中添加一行：

```markdown
| [`nature-<topic>`](skills/nature-<topic>/README.md) | Draft / Stable | 一句话用途 | 触发词 | [详情](skills/nature-<topic>/README.md) |
```

### 5. 状态标签

| 标签 | 含义 |
|-------|------|
| `Draft` | 规则已定义，但尚未在真实案例上测试 |
| `Beta` | 已在示例上测试，仍可能存在边界问题 |
| `Stable` | 已在真实学术内容上验证，规则相对稳定 |

---
